# website/sms_utils.py
import africastalking
from django.conf import settings

class SMSNotifier:
    def __init__(self):
        self.username = settings.AFRICASTALKING_USERNAME
        self.api_key = settings.AFRICASTALKING_API_KEY
        
        # Initialize Africa's Talking
        africastalking.initialize(self.username, self.api_key)
        self.sms = africastalking.SMS
    
    def send_sms(self, phone_number, message):
        """Send SMS to a single number"""
        try:
            # Format phone number (ensure it starts with +254)
            phone = str(phone_number).replace('+', '')
            if phone.startswith('0'):
                phone = '+254' + phone[1:]
            elif phone.startswith('254'):
                phone = '+' + phone
            
            result = self.sms.send(message, [phone])
            return {'success': True, 'message': 'SMS sent successfully', 'data': result}
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    def send_bulk_sms(self, phone_numbers, message):
        """Send SMS to multiple numbers"""
        try:
            # Format all phone numbers
            formatted_numbers = []
            for phone in phone_numbers:
                phone = str(phone).replace('+', '')
                if phone.startswith('0'):
                    phone = '+254' + phone[1:]
                elif phone.startswith('254'):
                    phone = '+' + phone
                formatted_numbers.append(phone)
            
            result = self.sms.send(message, formatted_numbers)
            return {'success': True, 'message': f'SMS sent to {len(formatted_numbers)} recipients', 'data': result}
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    def send_event_reminder(self, phone_number, event_name, event_date, location):
        """Send event reminder SMS"""
        message = f"""
CHURCH EVENT REMINDER
Event: {event_name}
Date: {event_date}
Location: {location}
We look forward to seeing you!
- Life Sanctuary Church
"""
        return self.send_sms(phone_number, message.strip())
    
    def send_donation_receipt(self, phone_number, amount, receipt_number):
        """Send donation receipt SMS"""
        message = f"""
DONATION RECEIPT
Amount: KES {amount}
Receipt: {receipt_number}
Thank you for your generous giving!
God bless you.
- Life Sanctuary Church
"""
        return self.send_sms(phone_number, message.strip())
    
    def send_prayer_response(self, phone_number, prayer_request_id):
        """Send prayer response SMS"""
        message = f"""
PRAYER UPDATE
Dear Member,
Our prayer team has received your request (#{prayer_request_id}).
We are standing with you in faith!
- Life Sanctuary Church
"""
        return self.send_sms(phone_number, message.strip())

# Helper function
def send_sms_notification(phone_number, message):
    """Quick function to send SMS"""
    try:
        notifier = SMSNotifier()
        return notifier.send_sms(phone_number, message)
    except Exception as e:
        return {'success': False, 'message': str(e)}
    
def send_sms_to_user(user, message):
    """Send SMS to a user using their profile phone number"""
    try:
        profile = MemberProfile.objects.get(user=user)
        if profile.full_phone:
            notifier = SMSNotifier()
            return notifier.send_sms(profile.full_phone, message)
        else:
            return {'success': False, 'message': 'No phone number registered'}
    except MemberProfile.DoesNotExist:
        return {'success': False, 'message': 'User profile not found'}
    except Exception as e:
        return {'success': False, 'message': str(e)}