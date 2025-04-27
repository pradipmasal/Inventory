from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('user_dashboard/', views.user_dashboard, name='user_dashboard'),
    path('add_component/', views.add_component, name='add_component'),
    path('issue_component/', views.issue_component, name='issue_component'),
    path('available_components/', views.available_components, name='available_components'),
    path('issued_components/', views.issued_components, name='issued_components'),
    path('returned_components/', views.returned_components, name='returned_components'),
    path('all-users/', views.view_all_users, name='view_all_users'),
    path('create-staff/', views.create_staff, name='create_staff'),
    path('staff-success/', views.staff_success, name='staff_success'),
    path('staff-list/', views.staff_list, name='staff_list'),
    path('deactivate-staff/<int:staff_id>/', views.deactivate_staff, name='deactivate_staff'),
    path('activate-staff/<int:staff_id>/', views.activate_staff, name='activate_staff'),
    path('delete-component/<int:component_id>/', views.delete_component, name='delete_component'),
    path('make-staff/<int:user_id>/', views.make_staff, name='make_staff'),
    path('make-user/<int:user_id>/', views.make_user, name='make_user'),
]
