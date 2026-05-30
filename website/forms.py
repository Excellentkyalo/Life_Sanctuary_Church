from django import forms
from .models import ContactMessage, PrayerRequest

class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'phone', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control-custom', 'placeholder': 'Your Name', 'required': True}),
            'email': forms.EmailInput(attrs={'class': 'form-control-custom', 'placeholder': 'Your Email', 'required': True}),
            'phone': forms.TextInput(attrs={'class': 'form-control-custom', 'placeholder': 'Your Phone (Optional)'}),
            'subject': forms.TextInput(attrs={'class': 'form-control-custom', 'placeholder': 'Subject', 'required': True}),
            'message': forms.Textarea(attrs={'class': 'form-control-custom', 'placeholder': 'Your Message', 'rows': 5, 'required': True}),
        }

class PrayerRequestForm(forms.ModelForm):
    class Meta:
        model = PrayerRequest
        fields = ['name', 'email', 'request']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control-custom', 'placeholder': 'Your Name (Optional)'}),
            'email': forms.EmailInput(attrs={'class': 'form-control-custom', 'placeholder': 'Your Email (Optional)'}),
            'request': forms.Textarea(attrs={'class': 'form-control-custom', 'placeholder': 'Your Prayer Request', 'rows': 5, 'required': True}),
        }