# website/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import ContactMessage, PrayerRequest, EventRegistration, Donation, VolunteerApplication, MemberProfile
import re
class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'phone', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control-custom',
                'placeholder': 'Your Name',
                'required': True
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control-custom',
                'placeholder': 'Your Email',
                'required': True
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control-custom',
                'placeholder': 'Your Phone (Optional)'
            }),
            'subject': forms.TextInput(attrs={
                'class': 'form-control-custom',
                'placeholder': 'Subject',
                'required': True
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control-custom',
                'rows': 5,
                'placeholder': 'Your Message',
                'required': True
            }),
        }

class PrayerRequestForm(forms.ModelForm):
    class Meta:
        model = PrayerRequest
        fields = ['name', 'email', 'phone', 'request', 'is_public']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control-custom',
                'placeholder': 'Your Name (Optional)'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control-custom',
                'placeholder': 'Your Email (Optional)'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control-custom',
                'placeholder': 'Your Phone (Optional)'
            }),
            'request': forms.Textarea(attrs={
                'class': 'form-control-custom',
                'rows': 5,
                'placeholder': 'Your Prayer Request',
                'required': True
            }),
            'is_public': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }

class EventRegistrationForm(forms.ModelForm):
    class Meta:
        model = EventRegistration
        fields = ['first_name', 'last_name', 'email', 'phone', 'number_of_guests', 'special_requests']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control-custom',
                'placeholder': 'First Name',
                'required': True
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control-custom',
                'placeholder': 'Last Name',
                'required': True
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control-custom',
                'placeholder': 'Email',
                'required': True
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control-custom',
                'placeholder': 'Phone',
                'required': True
            }),
            'number_of_guests': forms.NumberInput(attrs={
                'class': 'form-control-custom',
                'min': 1,
                'value': 1
            }),
            'special_requests': forms.Textarea(attrs={
                'class': 'form-control-custom',
                'rows': 3,
                'placeholder': 'Special Requests (Optional)'
            }),
        }

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'class': 'form-control-custom',
        'placeholder': 'Email',
        'required': True
    }))
    
    phone = forms.CharField(max_length=20, required=True, widget=forms.TextInput(attrs={
        'class': 'form-control-custom',
        'placeholder': 'Phone Number (e.g., 0712345678)',
        'required': True,
        'pattern': '^0[17]\d{8}$',
        'title': 'Enter a valid Kenyan phone number (07XX or 01XX)'
    }))
    
    gender = forms.ChoiceField(choices=[
        ('', 'Select Gender'),
        ('male', 'Male'),
        ('female', 'Female'),
    ], required=True, widget=forms.Select(attrs={
        'class': 'form-control-custom',
        'required': True
    }))
    
    first_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={
        'class': 'form-control-custom',
        'placeholder': 'First Name',
        'required': True
    }))
    
    last_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={
        'class': 'form-control-custom',
        'placeholder': 'Last Name',
        'required': True
    }))
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'phone', 'gender', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control-custom',
                'placeholder': 'Username',
                'required': True
            }),
            'password1': forms.PasswordInput(attrs={
                'class': 'form-control-custom',
                'placeholder': 'Password',
                'required': True
            }),
            'password2': forms.PasswordInput(attrs={
                'class': 'form-control-custom',
                'placeholder': 'Confirm Password',
                'required': True
            }),
        }
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        # Remove any non-digit characters
        phone = re.sub(r'\D', '', phone)
        
        # Validate Kenyan phone format
        if not re.match(r'^0[17]\d{8}$', phone):
            raise forms.ValidationError('Please enter a valid Kenyan phone number (e.g., 0712345678)')
        
        # Check if phone is already registered
        if MemberProfile.objects.filter(phone=phone).exists():
            raise forms.ValidationError('This phone number is already registered')
        
        return phone
    
class DonationForm(forms.ModelForm):
    class Meta:
        model = Donation
        fields = ['donor_name', 'donor_email', 'donor_phone', 'category', 'amount', 'notes', 'is_anonymous']
        widgets = {
            'donor_name': forms.TextInput(attrs={
                'class': 'form-control-custom',
                'placeholder': 'Your Name (Optional)'
            }),
            'donor_email': forms.EmailInput(attrs={
                'class': 'form-control-custom',
                'placeholder': 'Your Email (Optional)'
            }),
            'donor_phone': forms.TextInput(attrs={
                'class': 'form-control-custom',
                'placeholder': 'M-Pesa Phone Number',
                'required': True
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control-custom',
                'placeholder': 'Amount (KES)',
                'min': 10,
                'required': True
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control-custom',
                'rows': 3,
                'placeholder': 'Notes (Optional)'
            }),
            'is_anonymous': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }

class VolunteerApplicationForm(forms.ModelForm):
    class Meta:
        model = VolunteerApplication
        fields = ['ministry_interest', 'availability', 'skills', 'previous_experience', 'why_serve']
        widgets = {
            'ministry_interest': forms.TextInput(attrs={
                'class': 'form-control-custom',
                'placeholder': 'Ministry You Want to Join',
                'required': True
            }),
            'availability': forms.Textarea(attrs={
                'class': 'form-control-custom',
                'rows': 3,
                'placeholder': 'Days and Times Available',
                'required': True
            }),
            'skills': forms.Textarea(attrs={
                'class': 'form-control-custom',
                'rows': 3,
                'placeholder': 'Your Skills (Optional)'
            }),
            'previous_experience': forms.Textarea(attrs={
                'class': 'form-control-custom',
                'rows': 3,
                'placeholder': 'Previous Experience (Optional)'
            }),
            'why_serve': forms.Textarea(attrs={
                'class': 'form-control-custom',
                'rows': 4,
                'placeholder': 'Why Do You Want to Serve?',
                'required': True
            }),
        }

class MemberProfileForm(forms.ModelForm):
    class Meta:
        model = MemberProfile
        fields = ['phone', 'address', 'city', 'country', 'date_of_birth', 'avatar', 'bio', 'spiritual_gifts', 'ministries', 'is_volunteer']
        widgets = {
            'phone': forms.TextInput(attrs={'class': 'form-control-custom'}),
            'address': forms.Textarea(attrs={'class': 'form-control-custom', 'rows': 3}),
            'city': forms.TextInput(attrs={'class': 'form-control-custom'}),
            'country': forms.TextInput(attrs={'class': 'form-control-custom'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control-custom', 'type': 'date'}),
            'avatar': forms.FileInput(attrs={'class': 'form-control-custom'}),
            'bio': forms.Textarea(attrs={'class': 'form-control-custom', 'rows': 4}),
            'spiritual_gifts': forms.Textarea(attrs={'class': 'form-control-custom', 'rows': 3}),
            'ministries': forms.Textarea(attrs={'class': 'form-control-custom', 'rows': 3}),
            'is_volunteer': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }