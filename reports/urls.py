from django.urls import path
from . import views

urlpatterns = [
    path('submit/success/', views.submit_report_success, name='submit_report_success'), #has to appear before report_form url-- "submit/<str:selected_residence>/"
    path('submit/<str:residence_type>/<str:selected_residence>/', views.submit_report, name='report_form'),
    path('select_residence_type/', views.select_residence_type, name='select_residence_type'),
    path('select_residence/<str:residence_type>/', views.select_residence, name='select_residence'),
    path('detail/<int:report_id>/', views.report_detail, name='report_detail'),
    path('list/', views.report_list, name='report_list'),
   
    path('user_residence/', views.user_residence, name='user_residence'),
    path('get-residences/', views.get_residences, name='get_residences'),
    path('get-buildings/', views.get_buildings, name='get_buildings'),

    path('mark-resolved/<int:report_id>/', views.change_status_resolved, name='change_status_resolved'),
    path('reports/detail/<int:report_id>/', views.report_detail, name='report_detail'),
    path('reports/detail/<int:report_id>/add_comment/', views.add_report_comment, name='add_report_comment'),
 #   path('report/', views.report_form_view, name='report_form'),
    path('reports/detail/<int:report_id>/delete/', views.delete_report, name='delete_report'),

     path('save_residence_selection/', views.save_residence_selection, name='save_residence_selection'),

    path('filter_reports/', views.filter_reports, name='filter_reports'),


   # path('list/', views.report_list, name='report_list'),
   # path('detail/<int:report_id>/', views.report_detail, name='report_detail'),
]

