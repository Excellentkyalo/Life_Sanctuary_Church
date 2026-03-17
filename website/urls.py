from django.urls import path
from . import views

urlpatterns = [
    # Main Pages
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('services/', views.services, name='services'),
    path('ministries/', views.ministries, name='ministries'),
    path('ministries/<slug:slug>/', views.ministry_detail, name='ministry_detail'),
    path('sermons/', views.sermons, name='sermons'),
    path('sermons/<slug:slug>/', views.sermon_detail, name='sermon_detail'),
    path('events/', views.events, name='events'),
    path('events/<slug:slug>/', views.event_detail, name='event_detail'),
    
    # Gallery
    path('gallery/', views.gallery, name='gallery'),
    path('gallery/<slug:slug>/', views.gallery_category, name='gallery_category'),
    
    path('live/', views.live, name='live'),
    path('donate/', views.donate, name='donate'),
    path('contact/', views.contact, name='contact'),
    
    # M-Pesa Payment
    path('donations/api/initiate/', views.initiate_payment, name='initiate_payment'),
    path('donations/mpesa/callback/', views.mpesa_callback, name='mpesa_callback'),
    
    # Prayer & Newsletter
    path('prayer-request/', views.submit_prayer_request, name='submit_prayer_request'),
    path('newsletter/subscribe/', views.newsletter_subscribe, name='newsletter_subscribe'),
    
    # Authentication
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    path('volunteer/', views.volunteer_apply, name='volunteer_apply'),
]