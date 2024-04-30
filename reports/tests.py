from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import Report, Residence
from django.core.files.uploadedfile import SimpleUploadedFile
from .forms import ReportForm
from .models import Residence, Report
from django.test import Client
from django.urls import reverse
from django.contrib.auth.models import User, Group
from .models import Report, Residence
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import Permission
from allauth.socialaccount.models import SocialApp
from django.contrib.sites.models import Site

# Tesing Models:
User = get_user_model()

class ReportModelTest(TestCase):

    def setUp(self):
        # Create a user for foreign key requirement
        self.user = User.objects.create_user(username='testuser', password='12345')

        # Create a report instance to use in tests
        self.report = Report.objects.create(
            report_text='Test Report',
            residence_type='Dormitory',
            residence='Residence Name',
            building='Building Name',
            report_type='Test Type',
            floor=3,
            room='303',
            status='New',
            user=self.user
        )

    def test_string_representation(self):
        self.assertEqual(str(self.report), f"Report #{self.report.id} - New")

    def test_default_status(self):
        new_report = Report(report_text='Another Test')
        self.assertEqual(new_report.status, 'New')

    def test_status_choices(self):
        self.report.status = 'Resolved'
        self.report.save()
        self.assertEqual(self.report.status, 'Resolved')

    def test_report_fields(self):
        self.assertEqual(self.report.report_text, 'Test Report')
        self.assertEqual(self.report.residence_type, 'Dormitory')
        self.assertEqual(self.report.residence, 'Residence Name')
        self.assertEqual(self.report.building, 'Building Name')
        self.assertEqual(self.report.report_type, 'Test Type')
        self.assertEqual(self.report.floor, 3)
        self.assertEqual(self.report.room, '303')
        self.assertIsNotNone(self.report.submission_timestamp)

    def test_submission_timestamp(self):
        self.assertTrue(isinstance(self.report.submission_timestamp, timezone.datetime))

    def test_report_file_is_optional(self):
        self.assertFalse(self.report.report_file)

    def test_building_is_optional(self):
        report_no_building = Report(report_text='No Building')
        self.assertIsNone(report_no_building.building)

    def test_floor_is_optional(self):
        report_no_floor = Report(report_text='No Floor')
        self.assertIsNone(report_no_floor.floor)

    def test_room_is_optional(self):
        report_no_room = Report(report_text='No Room')
        self.assertIsNone(report_no_room.room)

    def test_user_is_optional(self):
        report_no_user = Report(report_text='No User')
        self.assertIsNone(report_no_user.user)

    def test_admin_message_is_optional(self):
        report_no_message = Report(report_text='No Message')
        self.assertIsNone(report_no_message.admin_message)


class ResidenceModelTest(TestCase):

    def setUp(self):
        # Create a Residence instance to use in tests.
        self.residence = Residence.objects.create(
            residence_type='Dormitory',
            residence='Residence Name',
            building='Building Name'
        )

    def test_string_representation(self):
        self.assertEqual(str(self.residence), self.residence.building)

    def test_residence_fields(self):
        self.assertEqual(self.residence.residence_type, 'Dormitory')
        self.assertEqual(self.residence.residence, 'Residence Name')
        self.assertEqual(self.residence.building, 'Building Name')

# Testing Forms:
class ReportFormTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Create test residences and buildings from the actual Residence database
        cls.residence = Residence.objects.create(residence_type='First Year Housing', residence='Alderman Road Hall-Style', building='Balz-Dobie')

    def test_report_form_fields(self):
        form = ReportForm()
        expected_fields = ['building', 'floor', 'report_file', 'report_text', 'report_type', 'room']
        self.assertListEqual(sorted(list(form.fields)), sorted(expected_fields))

    def test_report_form_valid_data(self):
        form_data = {
            'report_type': 'Noise Complaint',
            'report_text': 'Test report content',
            'building': self.residence.building,
            'floor': 2,
            'room': '201A'
        }
        form = ReportForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_report_form_file_upload(self):
        uploaded_file = SimpleUploadedFile('testfile.txt', b'file_content', content_type='text/plain')
        form_data = {
            'report_type': 'Safety Concern',
            'report_text': 'Test report content with file',
            'building': self.residence.building,
            'floor': 3,
            'room': '301B'
        }
        form = ReportForm(data=form_data, files={'report_file': uploaded_file})
        self.assertTrue(form.is_valid())

    def test_report_form_initial_building_choices_with_selected_residence(self):
        form = ReportForm(selected_residence=self.residence.residence)
        buildings = Residence.objects.filter(residence=self.residence.residence).values_list('building', flat=True).distinct()
        expected_choices = [('', '--- Select Building ---')] + [(building, building) for building in buildings]
        self.assertEqual(list(form.fields['building'].widget.choices), expected_choices)

    def test_report_form_invalid_data(self):
        form_data = {
            'report_type': '',  # This is now a required field, so it should raise an error
            'report_text': '',  # Required field, still should raise an error
        }
        form = ReportForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('report_type', form.errors)  # Check for required field error
        self.assertIn('report_text', form.errors)  # Check for required field error

    def test_report_form_update_existing_report(self):
        report = Report.objects.create(
            report_type='Noise Complaint',
            report_text='Original report content',
            residence_type=self.residence.residence_type,
            residence=self.residence.residence,
            building=self.residence.building,
            floor=1,
            room='101'
        )
        form_data = {
            'report_type': 'Rule Violation',  # Updated type
            'report_text': 'Updated report content',
            'building': self.residence.building,
            'floor': report.floor,
            'room': '102'
        }
        form = ReportForm(data=form_data, instance=report)
        self.assertTrue(form.is_valid())
        updated_report = form.save()
        self.assertEqual(updated_report.report_text, 'Updated report content')
        self.assertEqual(updated_report.report_type, 'Rule Violation')
        self.assertEqual(updated_report.room, '102')

# Testing Views:
#     To achieve full coverage testing for the provided views in your Django app, you'll want to write tests that 
#     exercise all the paths through each view. For each view, you'll want to test:
#     How the view responds to GET and POST requests (as appropriate).
#     That the view behaves correctly with valid and invalid data.
#     Any permissions or authentication required by the view.
#     Any redirects that should occur.
#     The context data passed to the templates.
#      File handling (where relevant).

class ReportViewsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='user', password='testpass')
        self.site_admin_group, created = Group.objects.get_or_create(name='Site Admins')

        site = Site.objects.get_current()
        self.social_app = SocialApp.objects.create(
            provider='google',
            name='Google',
            client_id='fake_client_id',
            secret='fake_secret'
        )
        self.social_app.sites.add(site)
        
        # Add user to group and permissions
        if created:
            # If the group was created, then set up permissions as necessary
            # Assume we have a permission named 'change_report' for this example
            self.site_admin_permission = Permission.objects.get(codename='change_report')
            self.site_admin_group.permissions.add(self.site_admin_permission)
        
        self.user.groups.add(self.site_admin_group)
        self.site_admin_permission = Permission.objects.get(codename='change_report')
        self.site_admin_group.permissions.add(self.site_admin_permission)
        self.residence_type = 'Dormitory'
        self.selected_residence = 'Residence Name'
        self.residence = Residence.objects.create(residence_type=self.residence_type, residence=self.selected_residence, building='Building Name')
        self.report = Report.objects.create(report_text='Some text', residence_type=self.residence_type, residence=self.selected_residence, user=self.user, report_type='Noise Complaint')
        # URL endpoints
        self.report_form_url = reverse('report_form', args=[self.residence_type, self.selected_residence])
        self.select_residence_type_url = reverse('select_residence_type')
        self.select_residence_url = reverse('select_residence', args=[self.residence_type])
        self.report_detail_url = reverse('report_detail', args=[self.report.id])
        self.change_status_resolved_url = reverse('change_status_resolved', args=[self.report.id])
        self.report_list_url = reverse('report_list')
        self.submit_report_success_url = reverse('submit_report_success')

    # report_form view tests
    def test_report_form_get(self):
        response = self.client.get(self.report_form_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'reports/report_form.html')

    def test_report_form_post_valid(self):
        self.client.login(username='user', password='testpass')
        report_data = {
            'report_type': 'Noise Complaint',
            'report_text': 'New Report',
            'building': self.residence.building,
            'floor': 1,
            'room': '101',
        }
        response = self.client.post(self.report_form_url, report_data)
        self.assertEqual(response.status_code, 302)  # Assuming redirection to success page
        self.assertTrue(Report.objects.filter(report_text='New Report').exists())

    def test_report_form_post_invalid(self):
        self.client.login(username='user', password='testpass')
        report_data = {
            # 'report_type': 'Noise Complaint',  # Omit required field for testing
            'report_text': '',  # Omit required text
        }
        response = self.client.post(self.report_form_url, report_data)
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'report_text', 'This field is required.')
        self.assertFormError(response, 'form', 'report_type', 'This field is required.')

    # select_residence_type view tests
    def test_select_residence_type_get(self):
        response = self.client.get(self.select_residence_type_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'reports/select_residence_type.html')

    # select_residence view tests
    def test_select_residence_get(self):
        response = self.client.get(self.select_residence_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'reports/select_residence.html')

        # Extract the 'residence' key from each dictionary in the actual residences list
        actual_residences = [res['residence'] for res in response.context['residences']]
        # Fetch the expected residences directly as a list of strings
        expected_residences = list(Residence.objects.filter(residence_type=self.residence_type).values_list('residence', flat=True).distinct())
    
        self.assertEqual(actual_residences, expected_residences)

    # change_status_resolved view tests
    def test_change_status_resolved_post(self):
        self.client.login(username='user', password='testpass')
        response = self.client.post(self.change_status_resolved_url, {'admin_message': 'Resolved message'})
        self.report.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.report.status, 'Resolved')
        self.assertEqual(self.report.admin_message, 'Resolved message')

    # report_detail view tests
    def test_report_detail_get(self):
        response = self.client.get(self.report_detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'reports/report_detail.html')
        self.assertEqual(response.context['report'], self.report)

    # add_report_comment view tests
    # Assume similar to change_status_resolved test, but with permission checks and comment creation.

    # report_list view tests
    def test_report_list_get(self):
        response = self.client.get(self.report_list_url)
        self.assertEqual(response.status_code, 200)