from django.urls import path
from . import views

urlpatterns = [
    path("", views.starting_page, name = "starting-page-margin"),
    path('upl/', views.upload_files, name = 'upload_files'),
    path('upl_arr/', views.refresh, name = 'upload_files')
]