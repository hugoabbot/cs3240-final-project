from django.shortcuts import render, redirect, get_object_or_404
from .forms import ReportForm
from .models import Report, Residence, UserProfile, User
from django.http import JsonResponse
from django.http import HttpResponseForbidden
from django.contrib import messages
from allauth.socialaccount.models import SocialApp
from django.contrib.sites.models import Site
from urllib.parse import quote



def submit_report(request, residence_type, selected_residence):
    if request.method == 'POST':
        form = ReportForm(request.POST, request.FILES, selected_residence=selected_residence)
        if form.is_valid():
            report = form.save(commit=False)
            report.residence_type = residence_type
            report.residence = selected_residence
            if not request.user.is_authenticated:
                report.user = None
            else:
                report.user = request.user
            if 'report_file' in request.FILES:
                report.report_file = request.FILES['report_file']
            report.save()
            return redirect('submit_report_success')
    else:
        form = ReportForm(selected_residence=selected_residence)

    # Retrieve buildings associated with the selected residence
    buildings = Residence.objects.filter(residence=selected_residence).values_list('building', flat=True).distinct()

    return render(request, 'reports/report_form.html',
                  {'form': form, 'selected_residence': selected_residence, 'residence_type': residence_type,
                   'buildings': buildings})


def select_residence_type(request):
    if not SocialApp.objects.filter(provider='google').exists():
        social_app = SocialApp.objects.create(
            provider='google',
            name=f'Google',
            client_id='test',
            secret='test',
        )
        social_app.sites.add(Site.objects.get_current())

    return render(request, 'reports/select_residence_type.html')


def select_residence(request, residence_type):
    residences = Residence.objects.filter(residence_type=residence_type).values('residence').distinct()
    return render(request, 'reports/select_residence.html',
                  {'residences': residences, 'residence_type': residence_type})


def change_status_in_progress(report):
    report.status = 'In Progress'
    report.save()


def change_status_resolved(request, report_id):
    report = get_object_or_404(Report, pk=report_id)
    if request.method == 'POST':
        admin_message = request.POST.get('admin_message', '')
        report.admin_message = admin_message
        report.status = 'Resolved'
        report.save()
    return redirect('report_detail', report_id=report_id)


def is_site_admin(request):
    return request.user.groups.filter(name='Site Admins').exists()


def report_detail(request, report_id):
    report = get_object_or_404(Report, pk=report_id)
    admin_message = None

    if is_site_admin(request) and report.status == 'New':
        change_status_in_progress(report)

    if request.method == 'POST' and 'admin_message' in request.POST:
        if is_site_admin(request):
            admin_message = request.POST.get('admin_message')
            report.admin_message = admin_message
            report.save()

    if report.report_file and report.report_file.name.lower().endswith('.txt'):
        with report.report_file.open() as file:
            text_content = file.read().decode('utf-8')
    else:
        text_content = None

    return render(request, 'reports/report_detail.html',
                  {'report': report, 'admin_message': report.admin_message, 'text_content': text_content})


def delete_report(request, report_id):
    report = Report.objects.get(id=report_id)
    report.delete()
    messages.success(request, 'Report successfully deleted!')
    return redirect('report_list')


def add_report_comment(request, report_id):
    report = get_object_or_404(Report, pk=report_id)
    if request.method == 'POST' and 'admin_message' in request.POST:
        if is_site_admin(request):
            admin_message = request.POST.get('admin_message')
            report.admin_message = admin_message
            report.save()
    return redirect('report_detail', report_id=report_id)


def report_list(request):
    reports = Report.objects.all()
    return render(request, 'reports/report_list.html', {'reports': reports})


def submit_report_success(request):
    return render(request, 'reports/submit_report_success.html')


def user_residence(request):
    report_types = Residence.objects.values_list('residence_type', flat=True).distinct()
    return render(request, 'reports/user_residence.html', {'report_types': report_types})


def get_residences(request):
    report_type = request.GET.get('report_type')
    residences = Residence.objects.filter(residence_type=report_type).values_list('residence', flat=True).distinct()
    residences_list = list(residences)
    return JsonResponse({'residences': residences_list})


def get_buildings(request):
    residence = request.GET.get('residence')
    buildings = Residence.objects.filter(residence=residence).values_list('building', flat=True).distinct()
    buildings_list = list(buildings)
    return JsonResponse({'buildings': buildings_list})


def save_residence_selection(request):
    if request.method == 'POST':
        residence = request.POST.get('residence')
        building = request.POST.get('building')
        floor = request.POST.get('floor')

        # Get or create the user profile for the logged-in user
        user_profile, created = UserProfile.objects.get_or_create(user=request.user)

        # Update the user profile with the selected values
        user_profile.residence = residence
        user_profile.building = building
        user_profile.floor = floor
        user_profile.save()

    return render(request, 'index.html')


def filter_reports(request):
    if request.user.is_authenticated and request.user.groups.filter(name='Site Admins').exists():
        user_profile = UserProfile.objects.get(user=request.user)
        residence = user_profile.residence
        building = user_profile.building
        floor = user_profile.floor

        # Query reports based on user profile entries
        filtered_reports = Report.objects.filter(
            residence=residence,
            #  building=building,
            #  floor=floor,
        )

        context = {
            'reports': filtered_reports
        }
        return render(request, 'reports/filter_reports.html', context)
    else:
        return HttpResponseForbidden("You are not authorized to view this page.")
