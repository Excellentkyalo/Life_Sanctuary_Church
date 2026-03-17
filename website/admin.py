# website/admin.py
from django.contrib import admin
from .models import (
    SiteSetting, Announcement, Ministry, MinistryMember, MinistryMedia,
    Pastor, Sermon, Event, EventRegistration, DonationCategory, Donation,
    DonationCampaign, ContactMessage, PrayerRequest, NewsletterSubscriber,
    MemberProfile, VolunteerApplication, GalleryCategory, GalleryImage, GalleryVideo
)

# Register all models with basic admin
admin.site.register(SiteSetting)
admin.site.register(Announcement)
admin.site.register(Ministry)
admin.site.register(MinistryMember)
admin.site.register(MinistryMedia)
admin.site.register(Pastor)
admin.site.register(Sermon)
admin.site.register(Event)
admin.site.register(EventRegistration)
admin.site.register(DonationCategory)
admin.site.register(Donation)
admin.site.register(DonationCampaign)
admin.site.register(ContactMessage)
admin.site.register(PrayerRequest)
admin.site.register(NewsletterSubscriber)
admin.site.register(VolunteerApplication)
admin.site.register(GalleryCategory)
admin.site.register(GalleryImage)
admin.site.register(GalleryVideo)