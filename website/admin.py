from django.contrib import admin
from .models import (
    SiteSetting, Announcement, Ministry, Pastor, Sermon,
    Event, EventRegistration, ContactMessage, PrayerRequest,
    NewsletterSubscriber, GalleryCategory, GalleryImage, GalleryVideo
)

admin.site.register(SiteSetting)
admin.site.register(Announcement)
admin.site.register(Ministry)
admin.site.register(Pastor)
admin.site.register(Sermon)
admin.site.register(Event)
admin.site.register(EventRegistration)
admin.site.register(ContactMessage)
admin.site.register(PrayerRequest)
admin.site.register(NewsletterSubscriber)
admin.site.register(GalleryCategory)
admin.site.register(GalleryImage)
admin.site.register(GalleryVideo)