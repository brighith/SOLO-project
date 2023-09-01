from django.urls import path
from . import views

app_name = 'app'
urlpatterns = [
    path('', views.index, name='index'),
    path('registration/', views.registration, name='registration'),
    path('logout/', views.logout, name='logout'),
    path('home/', views.success, name='home'),
    path('sections/new/', views.newSection, name='newSection'),
    path('sectionCreate/', views.sectionCreate, name='sectionCreate'),
    path('newSectionRedirect/', views.newSectionRedirect, name='newSectionRedirect'),
    path('login/', views.login, name='login'),
    path('successRedirect/', views.successRedirect, name='successRedirect'),
    path('sections/<int:id>/', views.sectionDetails, name='sectionDetails'),
    path('sections/<int:section_id>/edit/', views.sectionEdit, name='sectionEdit'),
    path('editSection/<int:section_id>/', views.editSection, name='editSection'),
    path('deleteSection/<int:section_id>/', views.deletesection, name='deleteSection'),
    path('add_student/<int:section_id>/', views.addStudent, name='addStudent'),
    path('sections/<int:section_id>/marks/', views.marks, name='marks'),
    path('sections/<int:id>', views.sectionDetails, name='sectionDetails'),
]
