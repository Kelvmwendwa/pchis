from django.urls import path
from . import views

app_name = "patients"

urlpatterns = [
    path('register/', views.register_patient, name='register'),
    path('profile/update/', views.update_profile, name='update_profile'),
    path('logout/', views.user_logout, name='logout'),

]
