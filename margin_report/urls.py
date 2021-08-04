from django.urls import path
from . import views

urlpatterns = [
    path("", views.starting_page, name = "starting-page-margin"),
    path('upl/', views.upload_files, name = 'upload_files'),
    path('upl_test/', views.test_get_json, name = 'upload_files_test'),
    path('upl_test1/', views.test_get_json1, name = 'upload_files_test'),
]