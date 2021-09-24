from django.urls import path
from . import views

urlpatterns = [
    path("", views.indexing_page, name = "indexing-page-plain"),
    path('upl_arr/', views.refresh, name = 'upload_files'),
    path('update/', views.update, name = 'upload_files'),
    path('upl_test/', views.test_get_json, name = 'upload_files_test'),
    path('upl_test2/', views.test_get_json_2, name = 'upload_files_test_2'),
    path('get_table/', views.get_table, name = 'getTable'),
]