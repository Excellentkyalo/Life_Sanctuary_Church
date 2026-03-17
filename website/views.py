# website/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.db import models
import json

from .models import (
    SiteSetting, Announcement, Ministry, MinistryMember, MinistryMedia,
    Pastor, Sermon, Event, EventRegistration, Donation, DonationCategory,
    DonationCampaign, ContactMessage, PrayerRequest, NewsletterSubscriber,
    MemberProfile, VolunteerApplication, GalleryCategory, GalleryImage, GalleryVideo
)
from .forms import (
    ContactForm, PrayerRequestForm, EventRegistrationForm,
    UserRegistrationForm, DonationForm, MemberProfileForm, VolunteerApplicationForm
)
from .mpesa_utils import MpesaAPI

def is_admin(user):
    """Check if user is admin/staff"""
    return user.is_authenticated and (user.is_staff or user.is_superuser)


def home(request):
    """Home page view"""
    # Get site settings
    try:
        site_settings = SiteSetting.objects.first()
    except:
        site_settings = None
    
    # Get announcements
    try:
        announcements = Announcement.objects.filter(active=True, end_date__gte=timezone.now())[:3]
    except:
        announcements = []
    
    # Get ministries
    try:
        ministries = Ministry.objects.filter(is_active=True)[:8]
    except:
        ministries = []
    
    # Get upcoming events
    try:
        upcoming_events = Event.objects.filter(start_date__gte=timezone.now(), is_active=True)[:3]
    except:
        upcoming_events = []
    
    # Get latest sermons
    try:
        latest_sermons = Sermon.objects.filter(published=True)[:3]
    except:
        latest_sermons = []
    
    context = {
        'site_settings': site_settings,
        'announcements': announcements,
        'ministries': ministries,
        'upcoming_events': upcoming_events,
        'latest_sermons': latest_sermons,
    }
    return render(request, 'website/home.html', context)
def about(request):
    """About page view"""
    pastors = Pastor.objects.filter(is_active=True)
    return render(request, 'website/about.html', {'pastors': pastors})

def services(request):
    """Services page view"""
    return render(request, 'website/services.html')

def ministries(request):
    """Ministries page view"""
    all_ministries = Ministry.objects.filter(is_active=True)
    return render(request, 'website/ministries.html', {'ministries': all_ministries})

def ministry_detail(request, slug):
    """Ministry detail page"""
    ministry = get_object_or_404(Ministry, slug=slug)
    members = ministry.members.all()
    media = ministry.media.all()
    return render(request, 'website/ministry_detail.html', {
        'ministry': ministry,
        'members': members,
        'media': media,
    })

def sermons(request):
    """Sermons page view"""
    sermons = Sermon.objects.filter(published=True).order_by('-date')
    pastors = Pastor.objects.filter(is_active=True)
    return render(request, 'website/sermons.html', {'sermons': sermons, 'pastors': pastors})

def sermon_detail(request, slug):
    """Sermon detail page"""
    sermon = get_object_or_404(Sermon, slug=slug)
    sermon.views += 1
    sermon.save()
    return render(request, 'website/sermon_detail.html', {'sermon': sermon})

def events(request):
    """Events page view"""
    upcoming = Event.objects.filter(start_date__gte=timezone.now(), is_active=True).order_by('start_date')
    past = Event.objects.filter(start_date__lt=timezone.now(), is_active=True).order_by('-start_date')
    return render(request, 'website/events.html', {'upcoming_events': upcoming, 'past_events': past})

def event_detail(request, slug):
    """Event detail page"""
    event = get_object_or_404(Event, slug=slug)
    if request.method == 'POST' and event.registration_required:
        form = EventRegistrationForm(request.POST)
        if form.is_valid():
            registration = form.save(commit=False)
            registration.event = event
            registration.save()
            messages.success(request, 'You have successfully registered for this event!')
            return redirect('event_detail', slug=event.slug)
    else:
        form = EventRegistrationForm()
    return render(request, 'website/event_detail.html', {'event': event, 'form': form})


def live(request):
    """Live streaming page view"""
    return render(request, 'website/live.html')

def donate(request):
    """Donation page view"""
    categories = DonationCategory.objects.filter(is_active=True)
    campaigns = DonationCampaign.objects.filter(is_active=True, featured=True)[:2]
    return render(request, 'website/donate.html', {'categories': categories, 'campaigns': campaigns})

def contact(request):
    """Contact page view"""
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your message has been sent successfully! We will get back to you soon.')
            return redirect('contact')
    else:
        form = ContactForm()
    return render(request, 'website/contact.html', {'form': form})

# ==================== M-PESA DONATION ====================

@require_http_methods(["POST"])
def initiate_payment(request):
    """Handle AJAX request to start M-Pesa STK Push"""
    try:
        data = json.loads(request.body)
        phone = data.get('phone', '').strip()
        amount = data.get('amount')
        purpose = data.get('purpose', 'Donation')
        name = data.get('name', 'Anonymous')
        email = data.get('email', '')
        
        # Validation
        if not phone or not amount:
            return JsonResponse({
                'status': 'error',
                'message': 'Phone number and amount are required'
            }, status=400)
        
        # Validate phone format
        phone = phone.replace('+', '').replace(' ', '')
        if phone.startswith('0'):
            phone = '254' + phone[1:]
        
        if not phone.startswith('254') or len(phone) != 12:
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid phone number. Use format 0712345678'
            }, status=400)
        
        # Validate amount
        try:
            amount = float(amount)
            if amount < 10:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Minimum donation amount is KES 10'
                }, status=400)
        except (ValueError, TypeError):
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid amount'
            }, status=400)
        
        # Create pending donation record
        donation = Donation.objects.create(
            donor_name=name,
            donor_phone=phone,
            donor_email=email,
            amount=amount,
            payment_method='mpesa',
            status='pending',
            notes=f'Purpose: {purpose}'
        )
        
        # Initiate M-Pesa STK Push
        mpesa_response = stk_push_request(
            phone_number=phone,
            amount=amount,
            account_reference=f"Church-{purpose}",
            transaction_desc=f"Donation for {purpose}"
        )
        
        if mpesa_response.get('ResponseCode') == '0':
            donation.checkout_request_id = mpesa_response.get('CheckoutRequestID')
            donation.transaction_id = mpesa_response.get('MerchantRequestID')
            donation.save()
            
            return JsonResponse({
                'status': 'success',
                'message': 'STK Push sent to your phone. Please check and enter PIN.'
            })
        else:
            donation.status = 'failed'
            donation.save()
            
            error_message = mpesa_response.get('errorMessage', 'Failed to initiate payment')
            return JsonResponse({
                'status': 'error',
                'message': error_message
            }, status=400)
            
    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid request data'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

def stk_push_request(phone_number, amount, account_reference, transaction_desc):
    """Make STK Push request to M-Pesa Daraja API"""
    try:
        # Get Access Token
        access_token = get_mpesa_access_token()
        if not access_token:
            return {'ResponseCode': '1', 'errorMessage': 'Failed to get access token'}
        
        # Generate Password
        password, timestamp = generate_mpesa_password()
        
        # Prepare headers
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        # Prepare payload
        payload = {
            "BusinessShortCode": settings.MPESA_SHORTCODE,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": int(amount),
            "PartyA": phone_number,
            "PartyB": settings.MPESA_SHORTCODE,
            "PhoneNumber": phone_number,
            "CallBackURL": f"{settings.BASE_URL}{settings.MPESA_CALLBACK_URL}",
            "AccountReference": account_reference[:12],  # Max 12 chars
            "TransactionDesc": transaction_desc[:13]  # Max 13 chars
        }
        
        # Make request
        url = f'{settings.MPESA_BASE_URL}/mpesa/stkpush/v1/processrequest'
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        return response.json()
        
    except Exception as e:
        return {'ResponseCode': '1', 'errorMessage': str(e)}

def get_mpesa_access_token():
    """Generate OAuth Access Token from M-Pesa"""
    try:
        import requests
        url = f'{settings.MPESA_BASE_URL}/oauth/v1/generate?grant_type=client_credentials'
        response = requests.get(
            url, 
            auth=(settings.MPESA_CONSUMER_KEY, settings.MPESA_CONSUMER_SECRET),
            timeout=10
        )
        
        if response.status_code == 200:
            return response.json().get('access_token')
        return None
    except Exception as e:
        print(f"Token error: {e}")
        return None

def generate_mpesa_password():
    """Generate Base64 encoded password for STK Push"""
    import base64
    from datetime import datetime
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    data_to_encode = f"{settings.MPESA_SHORTCODE}{settings.MPESA_PASSKEY}{timestamp}"
    encoded = base64.b64encode(data_to_encode.encode()).decode('utf-8')
    return encoded, timestamp

@csrf_exempt
@require_http_methods(["POST"])
def mpesa_callback(request):
    """Handle M-Pesa Callback URL"""
    try:
        callback_data = json.loads(request.body)
        stk_callback = callback_data.get('Body', {}).get('stkCallback', {})
        
        checkout_request_id = stk_callback.get('CheckoutRequestID')
        result_code = stk_callback.get('ResultCode')
        
        # Find the donation
        try:
            donation = Donation.objects.get(checkout_request_id=checkout_request_id)
        except Donation.DoesNotExist:
            return JsonResponse({'ResultCode': 0, 'ResultDesc': 'Accepted'})
        
        if result_code == 0:
            # Payment Successful
            callback_metadata = stk_callback.get('CallbackMetadata', {}).get('Item', [])
            receipt = None
            amount = None
            phone = None
            
            for item in callback_metadata:
                if item.get('Name') == 'MpesaReceiptNumber':
                    receipt = item.get('Value')
                elif item.get('Name') == 'Amount':
                    amount = item.get('Value')
                elif item.get('Name') == 'PhoneNumber':
                    phone = item.get('Value')
            
            donation.status = 'completed'
            donation.mpesa_receipt_number = receipt
            if amount:
                donation.amount = amount
            if phone:
                donation.donor_phone = phone
            donation.save()
            
            # Send email receipt
            if donation.donor_email:
                send_donation_receipt(donation)
            
            print(f"Payment completed: {receipt} - {amount}")
        else:
            # Payment Cancelled or Failed
            donation.status = 'cancelled'
            donation.save()
            print(f"Payment cancelled/failed: {checkout_request_id}")
        
        return JsonResponse({'ResultCode': 0, 'ResultDesc': 'Accepted'})
        
    except Exception as e:
        print(f"Callback error: {e}")
        return JsonResponse({'ResultCode': 1, 'ResultDesc': str(e)})

def send_donation_receipt(donation):
    """Send email receipt to donor"""
    try:
        site_setting = SiteSetting.objects.first()
        church_name = site_setting.church_name if site_setting else 'Life Sanctuary Church'
        
        subject = f'Thank You for Your Donation - {church_name}'
        message = f'''
Dear {donation.donor_name or 'Donor'},

Thank you for your generous donation to {church_name}!

Donation Details:
-----------------
Amount: KES {donation.amount}
Purpose: {donation.notes}
Receipt Number: {donation.mpesa_receipt_number}
Date: {donation.created_at.strftime('%Y-%m-%d %H:%M')}

"Each of you should give what you have decided in your heart to give, 
not reluctantly or under compulsion, for God loves a cheerful giver."
- 2 Corinthians 9:7

May God bless you abundantly!

Blessings,
{church_name}
{site_setting.phone_primary if site_setting else ''}
{site_setting.email if site_setting else ''}
        '''
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[donation.donor_email],
            fail_silently=True,
        )
    except Exception as e:
        print(f"Email error: {e}")

# ==================== PRAYER & NEWSLETTER ====================

def submit_prayer_request(request):
    """Submit prayer request"""
    if request.method == 'POST':
        form = PrayerRequestForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your prayer request has been submitted. We are praying with you!')
    return redirect('home')

def newsletter_subscribe(request):
    """Subscribe to newsletter"""
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            NewsletterSubscriber.objects.create(email=email)
            messages.success(request, 'Thank you for subscribing to our newsletter!')
        except:
            messages.info(request, 'You are already subscribed!')
    return redirect('home')

# ==================== AUTHENTICATION ====================

# website/views.py
def register(request):
    """User registration view"""
    if request.user.is_authenticated:
        return redirect('homepage')
    
    # Define admin codes (store in environment variables for production)
    ADMIN_CODES = ['ADMIN2026', 'PASTOR123', 'LEADER456']
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.email = form.cleaned_data['email']
            user.save()
            
            # Get admin code
            admin_code = form.cleaned_data.get('admin_code', '')
            
            # Create member profile
            profile = MemberProfile.objects.create(
                user=user,
                phone=form.cleaned_data['phone'],
                gender=form.cleaned_data['gender'],
                admin_code=admin_code,
            )
            
            # Check if admin code is valid
            if admin_code.upper() in ADMIN_CODES:
                profile.user_type = 'admin'
                profile.is_admin_approved = True
                user.is_staff = True
                user.save()
                profile.save()
                messages.success(request, f'Welcome Admin {user.first_name}! You have full access.')
            else:
                profile.user_type = 'member'
                profile.save()
                messages.success(request, f'Welcome {user.first_name}! Your account has been created.')
            
            # Send welcome SMS
            try:
                from .sms_utils import SMSNotifier
                notifier = SMSNotifier()
                message = f"""
WELCOME TO LIFE SANCTUARY CHURCH
Dear {user.first_name},
Thank you for registering with us!
{'You have admin access.' if profile.user_type == 'admin' else 'Please login to access the church portal.'}
God bless you!
"""
                if profile.full_phone:
                    notifier.send_sms(profile.full_phone, message.strip())
            except Exception as e:
                print(f"Welcome SMS error: {e}")
            
            login(request, user)
            return redirect('homepage')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = UserRegistrationForm()
    return render(request, 'website/members/register.html', {'form': form})
def logout_view(request):
    """User logout view"""
    logout(request)
    messages.info(request, 'You have been logged out')
    return redirect('home')

@login_required
def dashboard(request):
    """User dashboard view"""
    profile, created = MemberProfile.objects.get_or_create(user=request.user)
    
    # Get user's donations
    donations = Donation.objects.filter(donor_email=request.user.email).order_by('-created_at')[:5]
    
    # Get user's event registrations
    event_registrations = EventRegistration.objects.filter(email=request.user.email)
    
    # Get user's volunteer applications
    volunteer_apps = VolunteerApplication.objects.filter(member=profile)
    
    # Get total donations amount
    total_donated = donations.aggregate(total=models.Sum('amount'))['total'] or 0
    
    # Get upcoming events
    upcoming_events = Event.objects.filter(start_date__gte=timezone.now(), is_active=True)[:3]
    
    context = {
        'profile': profile,
        'donations': donations,
        'event_registrations': event_registrations,
        'volunteer_apps': volunteer_apps,
        'total_donated': total_donated,
        'upcoming_events': upcoming_events,
    }
    return render(request, 'website/members/dashboard.html', context)
@login_required
def profile(request):
    """User profile view"""
    profile, created = MemberProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = MemberProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = MemberProfileForm(instance=profile)
    return render(request, 'website/members/profile.html', {'form': form, 'profile': profile})

@login_required
@user_passes_test(is_admin, login_url='home')
def dashboard(request):
    """Admin dashboard view - only accessible to admin/staff"""
    profile, created = MemberProfile.objects.get_or_create(user=request.user)
    
    # Get all members (for admin monitoring)
    all_members = User.objects.filter(profile__is_active=True)
    total_members = all_members.count()
    
    # Get recent registrations
    recent_members = all_members.order_by('-date_joined')[:10]
    
    # Get all donations
    all_donations = Donation.objects.all().order_by('-created_at')[:10]
    total_donations = Donation.objects.aggregate(total=models.Sum('amount'))['total'] or 0
    
    # Get all event registrations
    all_event_registrations = EventRegistration.objects.all().order_by('-registered_at')[:10]
    
    # Get upcoming events
    upcoming_events = Event.objects.filter(start_date__gte=timezone.now(), is_active=True)[:5]
    
    # Get contact messages
    unread_messages = ContactMessage.objects.filter(is_read=False).count()
    recent_messages = ContactMessage.objects.order_by('-created_at')[:5]
    
    # Get prayer requests
    prayer_requests = PrayerRequest.objects.order_by('-created_at')[:5]
    
    # Get volunteer applications
    volunteer_apps = VolunteerApplication.objects.order_by('-applied_at')[:5]
    
    context = {
        'profile': profile,
        'total_members': total_members,
        'recent_members': recent_members,
        'all_donations': all_donations,
        'total_donations': total_donations,
        'all_event_registrations': all_event_registrations,
        'upcoming_events': upcoming_events,
        'unread_messages': unread_messages,
        'recent_messages': recent_messages,
        'prayer_requests': prayer_requests,
        'volunteer_apps': volunteer_apps,
    }
    return render(request, 'website/members/dashboard.html', context)
def gallery(request):
    """Gallery page view"""
    categories = GalleryCategory.objects.filter(is_active=True)
    images = GalleryImage.objects.filter(is_featured=True)[:12]
    videos = GalleryVideo.objects.filter(is_featured=True)[:6]
    return render(request, 'website/gallery.html', {
        'categories': categories,
        'images': images,
        'videos': videos,
    })

def gallery_category(request, slug):
    """Gallery category page"""
    category = get_object_or_404(GalleryCategory, slug=slug)
    images = category.images.all()
    videos = category.videos.all()
    return render(request, 'website/gallery_category.html', {
        'category': category,
        'images': images,
        'videos': videos,
    })


def mpesa_callback(request):
    """Handle M-Pesa Callback URL"""
    try:
        callback_data = json.loads(request.body)
        stk_callback = callback_data.get('Body', {}).get('stkCallback', {})
        
        checkout_request_id = stk_callback.get('CheckoutRequestID')
        result_code = stk_callback.get('ResultCode')
        
        # Find the donation
        try:
            donation = Donation.objects.get(checkout_request_id=checkout_request_id)
        except Donation.DoesNotExist:
            return JsonResponse({'ResultCode': 0, 'ResultDesc': 'Accepted'})
        
        if result_code == 0:
            # Payment Successful
            callback_metadata = stk_callback.get('CallbackMetadata', {}).get('Item', [])
            receipt = None
            amount = None
            phone = None
            
            for item in callback_metadata:
                if item.get('Name') == 'MpesaReceiptNumber':
                    receipt = item.get('Value')
                elif item.get('Name') == 'Amount':
                    amount = item.get('Value')
                elif item.get('Name') == 'PhoneNumber':
                    phone = item.get('Value')
            
            donation.status = 'completed'
            donation.mpesa_receipt_number = receipt
            if amount:
                donation.amount = amount
            if phone:
                donation.donor_phone = phone
            donation.save()
            
            # Send email receipt
            if donation.donor_email:
                send_donation_receipt(donation)
            
            # Send SMS receipt
            if donation.donor_phone:
                try:
                    from .sms_utils import SMSNotifier
                    notifier = SMSNotifier()
                    notifier.send_donation_receipt(
                        donation.donor_phone,
                        donation.amount,
                        receipt
                    )
                except Exception as e:
                    print(f"SMS error: {e}")
            
            print(f"Payment completed: {receipt} - {amount}")
        else:
            # Payment Cancelled or Failed
            donation.status = 'cancelled'
            donation.save()
            print(f"Payment cancelled/failed: {checkout_request_id}")
        
        return JsonResponse({'ResultCode': 0, 'ResultDesc': 'Accepted'})
        
    except Exception as e:
        print(f"Callback error: {e}")
        return JsonResponse({'ResultCode': 1, 'ResultDesc': str(e)})
    
def send_event_reminder_sms(event):
    """Send SMS reminders to all registered members for an event"""
    try:
        from .sms_utils import SMSNotifier
        notifier = SMSNotifier()
        
        registrations = EventRegistration.objects.filter(event=event, is_confirmed=True)
        
        for reg in registrations:
            # Try to find user by email and get their profile phone
            try:
                user = User.objects.get(email=reg.email)
                profile = MemberProfile.objects.get(user=user)
                if profile.full_phone:
                    message = f"""
EVENT REMINDER
{event.title}
Date: {event.start_date|date:"M d, Y"}
Location: {event.location}
We look forward to seeing you!
- Life Sanctuary Church
"""
                    notifier.send_sms(profile.full_phone, message.strip())
            except:
                # If no user found, use registration phone
                if reg.phone:
                    message = f"""
EVENT REMINDER
{event.title}
Date: {event.start_date|date:"M d, Y"}
Location: {event.location}
We look forward to seeing you!
- Life Sanctuary Church
"""
                    notifier.send_sms(reg.phone, message.strip())
        
        return {'success': True, 'message': f'SMS sent to {registrations.count()} recipients'}
    except Exception as e:
        print(f"Event SMS error: {e}")
    return {'success': False, 'message': str(e)}

@login_required
def volunteer_apply(request):
    """Volunteer application view"""
    if request.method == 'POST':
        form = VolunteerApplicationForm(request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            # Get or create member profile
            profile, created = MemberProfile.objects.get_or_create(user=request.user)
            application.member = profile
            application.save()
            messages.success(request, 'Your volunteer application has been submitted! We will contact you soon.')
            return redirect('dashboard')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = VolunteerApplicationForm()
    return render(request, 'website/members/volunteer.html', {'form': form})

def login_view(request):
    """User login view"""
    if request.user.is_authenticated:
        return redirect('homepage')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name or user.username}!')
            return redirect('homepage')
        else:
            messages.error(request, 'Invalid username or password')
    
    return render(request, 'website/members/login.html')


def logout_view(request):
    """User logout view"""
    logout(request)
    messages.info(request, 'You have been logged out')
    return redirect('homepage')

