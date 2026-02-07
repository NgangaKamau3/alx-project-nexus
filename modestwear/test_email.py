"""
Test email configuration
Run: python manage.py shell < test_email.py
"""
import os
from django.core.mail import send_mail
from django.conf import settings

print("=" * 50)
print("EMAIL CONFIGURATION TEST")
print("=" * 50)

print(f"\nEMAIL_BACKEND: {settings.EMAIL_BACKEND}")
print(f"EMAIL_HOST: {settings.EMAIL_HOST}")
print(f"EMAIL_PORT: {settings.EMAIL_PORT}")
print(f"EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
print(f"EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
print(f"EMAIL_HOST_PASSWORD: {'*' * len(settings.EMAIL_HOST_PASSWORD) if settings.EMAIL_HOST_PASSWORD else 'NOT SET'}")
print(f"DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")

print("\n" + "=" * 50)
print("SENDING TEST EMAIL...")
print("=" * 50)

try:
    result = send_mail(
        subject='ModestWear Test Email',
        message='This is a test email from ModestWear backend.',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[settings.EMAIL_HOST_USER],
        fail_silently=False
    )
    print(f"\n✅ SUCCESS! Email sent. Result: {result}")
except Exception as e:
    print(f"\n❌ ERROR: {str(e)}")
    import traceback
    print(traceback.format_exc())

print("\n" + "=" * 50)
