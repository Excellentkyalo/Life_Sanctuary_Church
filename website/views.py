# website/views.py
# Complete views for Life Sanctuary Church

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test, login_required
from django.utils import timezone
from django.core.management import call_command
from io import StringIO

from .models import SiteSetting, Announcement, Ministry, Sermon, Event, ContactMessage, GalleryCategory, GalleryImage, GalleryVideo
from .forms import ContactForm

# ============================================
# Helper Function: Check if user is admin
# ============================================
def is_admin(user):
    """Check if user is staff or superuser"""
    return user.is_authenticated and (user.is_staff or user.is_superuser)

# ============================================
# PUBLIC PAGES (No Login Required)
# ============================================

def home(request):
    """Homepage"""
    site_settings = SiteSetting.objects.first()
    announcements = Announcement.objects.filter(active=True, end_date__gte=timezone.now())[:3]
    ministries = Ministry.objects.filter(is_active=True)[:6]
    upcoming_events = Event.objects.filter(start_date__gte=timezone.now(), is_active=True)[:3]
    latest_sermons = Sermon.objects.filter(published=True)[:3]
    context = {
        'site_settings': site_settings,
        'announcements': announcements,
        'ministries': ministries,
        'upcoming_events': upcoming_events,
        'latest_sermons': latest_sermons,
    }
    return render(request, 'website/home.html', context)

def about(request):
    """About Page"""
    return render(request, 'website/about.html')

def services(request):
    """Services Page"""
    return render(request, 'website/services.html')

def ministries(request):
    """Ministries Page"""
    return render(request, 'website/ministries.html')

def ministry_detail(request, slug):
    """Ministry Detail Page"""
    return render(request, 'website/ministry_detail.html', {'slug': slug})

def sermons(request):
    """Sermons Page"""
    sermons = Sermon.objects.filter(published=True).order_by('-date')
    return render(request, 'website/sermons.html', {'sermons': sermons})

def sermon_detail(request, slug):
    """Sermon Detail Page"""
    sermon = get_object_or_404(Sermon, slug=slug)
    sermon.views += 1
    sermon.save()
    return render(request, 'website/sermon_detail.html', {'sermon': sermon})

def events(request):
    """Events Page"""
    upcoming = Event.objects.filter(start_date__gte=timezone.now(), is_active=True).order_by('start_date')
    past = Event.objects.filter(start_date__lt=timezone.now(), is_active=True).order_by('-start_date')
    return render(request, 'website/events.html', {'upcoming_events': upcoming, 'past_events': past})

def event_detail(request, slug):
    """Event Detail Page"""
    event = get_object_or_404(Event, slug=slug)
    return render(request, 'website/event_detail.html', {'event': event})

def gallery(request):
    """Gallery Page"""
    categories = GalleryCategory.objects.filter(is_active=True)
    images = GalleryImage.objects.filter(is_featured=True)[:12]
    videos = GalleryVideo.objects.filter(is_featured=True)[:6]
    return render(request, 'website/gallery.html', {'categories': categories, 'images': images, 'videos': videos})

def gallery_category(request, slug):
    """Gallery Category Page"""
    category = get_object_or_404(GalleryCategory, slug=slug)
    images = category.images.all()
    videos = category.videos.all()
    return render(request, 'website/gallery_category.html', {'category': category, 'images': images, 'videos': videos})

def contact(request):
    """Contact Page"""
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your message has been sent successfully!')
            return redirect('contact')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = ContactForm()
    return render(request, 'website/contact.html', {'form': form})

# ============================================
# ADMIN ONLY PAGES (Login Required)
# ============================================

@login_required
def admin_dashboard(request):
    """Admin Dashboard - Self-Healing for Render Free Tier"""
    
    # 1. SELF-HEALING: Try to run migrations if tables are missing
    try:
        out = StringIO()
        call_command('migrate', '--run-syncdb', stdout=out)
    except Exception:
        pass 

    # 2. Prepare Context with Safe Defaults
    context = {
        'user': request.user,
        'total_sermons': 0,
        'total_events': 0,
        'total_gallery_images': 0,
        'total_messages': 0,
        'recent_events': [],
        'recent_sermons': [],
        'recent_messages': [],
        'unread_messages_count': 0,
    }

    # 3. Safely Fetch Data
    try:
        context['total_sermons'] = Sermon.objects.count()
        context['total_events'] = Event.objects.count()
        context['total_gallery_images'] = GalleryImage.objects.count()
        context['total_messages'] = ContactMessage.objects.count()
        
        context['recent_events'] = Event.objects.order_by('-start_date')[:5]
        context['recent_sermons'] = Sermon.objects.order_by('-date')[:5]
        context['recent_messages'] = ContactMessage.objects.filter(is_read=False).order_by('-created_at')[:5]
        context['unread_messages_count'] = ContactMessage.objects.filter(is_read=False).count()
    except Exception as e:
        print(f"Dashboard Data Error: {e}")

    return render(request, 'website/admin_dashboard.html', context)