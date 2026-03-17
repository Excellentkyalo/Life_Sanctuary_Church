# website/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse


# ==================== SITE SETTINGS ====================
class SiteSetting(models.Model):
    church_name = models.CharField(max_length=200, default="Life Sanctuary Church International")
    tagline = models.CharField(max_length=300, blank=True)
    motto = models.CharField(max_length=300, default="Pray without ceasing")
    motto_scripture = models.CharField(max_length=200, default="1 Thessalonians 5:17")
    logo = models.ImageField(upload_to='settings/logo/', blank=True, null=True)
    favicon = models.ImageField(upload_to='settings/favicon/', blank=True, null=True)
    address = models.TextField(default="Nairobi, Kenya")
    phone_primary = models.CharField(max_length=20, default="+254 713 349691")
    phone_secondary = models.CharField(max_length=20, blank=True, default="+254 722 881267")
    email = models.EmailField(default="info@lifesanctuarychurch.org")
    email_secondary = models.EmailField(blank=True, default="pastor@lifesanctuarychurch.org")
    facebook_url = models.URLField(blank=True, default="https://web.facebook.com/people/Life-Sanctuary-Church/100067613066530/")
    instagram_url = models.URLField(blank=True)
    youtube_url = models.URLField(blank=True, default="https://www.youtube.com/@lifesanctuarychurchkwa-reu8729")
    tiktok_url = models.URLField(blank=True)
    google_maps_embed = models.TextField(blank=True, default='<iframe src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3988.7665625229624!2d36.86640807361098!3d-1.3156139986718944!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x182f130014fb0273%3A0xd632d2744c464460!2sLife%20Sanctuary%20Church%2C%20Kwa%20Ruben!5e0!3m2!1sen!2ske!4v1771671092293!5m2!1sen!2ske" width="100%" height="400" style="border:0;" allowfullscreen="" loading="lazy"></iframe>')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Site Setting'
        verbose_name_plural = 'Site Settings'
    
    def __str__(self):
        return self.church_name

# ==================== ANNOUNCEMENTS ====================
class Announcement(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    image = models.ImageField(upload_to='announcements/', blank=True, null=True)
    active = models.BooleanField(default=True)
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField()
    priority = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-priority', '-start_date']
    
    def __str__(self):
        return self.title

# ==================== MINISTRIES ====================
class Ministry(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    short_description = models.CharField(max_length=300, blank=True)
    image = models.ImageField(upload_to='ministries/', blank=True, null=True)
    icon = models.CharField(max_length=50, blank=True, help_text="Font Awesome icon class (e.g., fas fa-users)")
    leader = models.CharField(max_length=200, blank=True)
    leader_email = models.EmailField(blank=True)
    leader_phone = models.CharField(max_length=20, blank=True)
    meeting_schedule = models.TextField(blank=True)
    youtube_url = models.URLField(blank=True)
    facebook_url = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Ministries'
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('ministry_detail', kwargs={'slug': self.slug})

class MinistryMember(models.Model):
    ministry = models.ForeignKey(Ministry, on_delete=models.CASCADE, related_name='members')
    name = models.CharField(max_length=200)
    role = models.CharField(max_length=100)
    image = models.ImageField(upload_to='ministry_members/', blank=True, null=True)
    is_leader = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-is_leader', 'name']
    
    def __str__(self):
        return f"{self.name} - {self.ministry.name}"

class MinistryMedia(models.Model):
    MEDIA_TYPES = [
        ('image', 'Image'),
        ('video', 'Video'),
    ]
    
    ministry = models.ForeignKey(Ministry, on_delete=models.CASCADE, related_name='media')
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPES)
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='ministry_media/', blank=True, null=True)
    youtube_url = models.URLField(blank=True, help_text="YouTube video URL")
    description = models.TextField(blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-uploaded_at']
        verbose_name_plural = 'Ministry Media'
    
    def __str__(self):
        return self.title

# ==================== SERMONS ====================
class Pastor(models.Model):
    name = models.CharField(max_length=200)
    title = models.CharField(max_length=200, blank=True)
    image = models.ImageField(upload_to='pastors/', blank=True, null=True)
    bio = models.TextField(blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name

class Sermon(models.Model):
    title = models.CharField(max_length=300)
    slug = models.SlugField(unique=True)
    pastor = models.ForeignKey(Pastor, on_delete=models.SET_NULL, null=True, blank=True, related_name='sermons')
    description = models.TextField()
    scripture_reference = models.CharField(max_length=200, blank=True)
    video_url = models.URLField(blank=True, help_text="YouTube or Vimeo URL")
    audio_file = models.FileField(upload_to='sermons/audio/', blank=True, null=True)
    thumbnail = models.ImageField(upload_to='sermons/thumbnails/', blank=True, null=True)
    duration = models.CharField(max_length=20, blank=True, help_text="e.g., 45:30")
    date = models.DateTimeField(default=timezone.now)
    published = models.BooleanField(default=False)
    views = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-date']
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('sermon_detail', kwargs={'slug': self.slug})

# ==================== EVENTS ====================
class Event(models.Model):
    title = models.CharField(max_length=300)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    short_description = models.CharField(max_length=300, blank=True)
    image = models.ImageField(upload_to='events/', blank=True, null=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(blank=True, null=True)
    location = models.CharField(max_length=300)
    max_attendees = models.PositiveIntegerField(blank=True, null=True)
    registration_required = models.BooleanField(default=False)
    registration_deadline = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['start_date']
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('event_detail', kwargs={'slug': self.slug})
    
    @property
    def is_upcoming(self):
        return self.start_date >= timezone.now()

class EventRegistration(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='registrations')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    number_of_guests = models.PositiveIntegerField(default=1)
    special_requests = models.TextField(blank=True)
    registered_at = models.DateTimeField(auto_now_add=True)
    is_confirmed = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-registered_at']
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.event.title}"

# ==================== DONATIONS ====================
class DonationCategory(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True, help_text="Font Awesome icon")
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name_plural = 'Donation Categories'
    
    def __str__(self):
        return self.name

class Donation(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    PAYMENT_METHODS = [
        ('mpesa', 'M-Pesa'),
        ('cash', 'Cash'),
        ('bank', 'Bank Transfer'),
    ]
    
    donor_name = models.CharField(max_length=200, blank=True)
    donor_phone = models.CharField(max_length=15)
    donor_email = models.EmailField(blank=True)
    category = models.ForeignKey(DonationCategory, on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    mpesa_receipt_number = models.CharField(max_length=50, blank=True)
    transaction_id = models.CharField(max_length=100, blank=True)
    checkout_request_id = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True)
    is_anonymous = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Donations'
    
    def __str__(self):
        return f"{self.donor_phone} - {self.amount} ({self.status})"

class DonationCampaign(models.Model):
    title = models.CharField(max_length=300)
    description = models.TextField()
    goal_amount = models.DecimalField(max_digits=12, decimal_places=2)
    current_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    start_date = models.DateField()
    end_date = models.DateField()
    image = models.ImageField(upload_to='campaigns/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-featured', '-start_date']
    
    def __str__(self):
        return self.title
    
    @property
    def progress_percentage(self):
        if self.goal_amount == 0:
            return 0
        return min(100, round((self.current_amount / self.goal_amount) * 100, 2))

# ==================== CONTACT & PRAYER ====================
class ContactMessage(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    subject = models.CharField(max_length=300)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    replied = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.subject}"

class PrayerRequest(models.Model):
    name = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    request = models.TextField()
    is_public = models.BooleanField(default=False, help_text="Show on prayer wall")
    is_answered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Prayer Request - {self.name or 'Anonymous'}"

class NewsletterSubscriber(models.Model):
    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.email

# ==================== MEMBER PORTAL ====================
class MemberProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=20, blank=True)
    gender = models.CharField(max_length=10, choices=[
        ('male', 'Male'),
        ('female', 'Female'),
    ], blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, default='Kenya')
    date_of_birth = models.DateField(blank=True, null=True)
    membership_date = models.DateField(blank=True, null=True)
    avatar = models.ImageField(upload_to='members/avatars/', blank=True, null=True)
    bio = models.TextField(blank=True)
    spiritual_gifts = models.TextField(blank=True, help_text="Comma-separated list")
    ministries = models.TextField(blank=True, help_text="Comma-separated list")
    is_volunteer = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"
    
    @property
    def full_phone(self):
        """Format phone number for SMS"""
        if not self.phone:
            return None
        phone = str(self.phone).replace('+', '').replace(' ', '')
        if phone.startswith('0'):
            return '+254' + phone[1:]
        elif phone.startswith('254'):
            return '+' + phone
        return phone
class VolunteerApplication(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    member = models.ForeignKey(MemberProfile, on_delete=models.CASCADE, related_name='volunteer_applications')
    ministry_interest = models.CharField(max_length=200)
    availability = models.TextField(help_text="Days and times available")
    skills = models.TextField(blank=True)
    previous_experience = models.TextField(blank=True)
    why_serve = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    applied_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.member.user.email} - {self.ministry_interest}"
    

# ==================== GALLERY ====================
class GalleryCategory(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = 'Gallery Categories'
        ordering = ['name']
    
    def __str__(self):
        return self.name

class GalleryImage(models.Model):
    category = models.ForeignKey(GalleryCategory, on_delete=models.CASCADE, related_name='images')
    title = models.CharField(max_length=200, blank=True)
    image = models.ImageField(upload_to='gallery/images/')
    description = models.TextField(blank=True)
    is_featured = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return self.title or f'Image {self.id}'

class GalleryVideo(models.Model):
    category = models.ForeignKey(GalleryCategory, on_delete=models.CASCADE, related_name='videos')
    title = models.CharField(max_length=200)
    youtube_url = models.URLField(help_text='YouTube video URL')
    thumbnail = models.ImageField(upload_to='gallery/video_thumbnails/', blank=True, null=True)
    description = models.TextField(blank=True)
    is_featured = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return self.title
    

