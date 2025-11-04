"""
Quick script to list all merchants
"""
import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tawfir_backend.settings')

# Don't import rest_framework dependent stuff
import django
django.setup()

from api.models import Merchant

print("=" * 50)
print("📋 All Merchants:")
print("=" * 50)

merchants = Merchant.objects.all()

if not merchants:
    print("❌ No merchants found!")
else:
    for m in merchants:
        print(f"ID: {m.id} - {m.business_name}")
        
print("=" * 50)
