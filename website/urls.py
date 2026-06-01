from django.urls import path
from . import views
from django.contrib.auth.decorators import user_passes_test

# Check if user is admin
def is_admin(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)

urlpatterns = [
    # ==================== PUBLIC PAGES (No Login Required) ====================
    path('', views.home, name='home'),  # ← Root URL now maps to home view
    path('about/', views.about, name='about'),
    path('services/', views.services, name='services'),
    path('ministries/', views.ministries, name='ministries'),
    path('ministries/<slug:slug>/', views.ministry_detail, name='ministry_detail'),
    path('sermons/', views.sermons, name='sermons'),
    path('sermons/<slug:slug>/', views.sermon_detail, name='sermon_detail'),
    path('events/', views.events, name='events'),
    path('events/<slug:slug>/', views.event_detail, name='event_detail'),
    path('gallery/', views.gallery, name='gallery'),
    path('gallery/<slug:slug>/', views.gallery_category, name='gallery_category'),
    path('contact/', views.contact, name='contact'),
    
    # ==================== ADMIN ONLY PAGES ====================
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),

       
]