"""
Simple script to add 30 test reviews directly
Run from project root: python simple_add_reviews.py
"""

import os
import sys

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tawfir_backend.settings')

import django
django.setup()

from django.contrib.auth import get_user_model
from api.models import Merchant, Review
from django.db.models import Avg
from datetime import datetime, timedelta
import random

User = get_user_model()

# Sample tags
POSITIVE_TAGS = ['خدمة ممتازة', 'جودة عالية', 'أسعار مناسبة', 'موقع ممتاز', 'نظافة', 'موظفين ودودين']
NEGATIVE_TAGS = ['خدمة بطيئة', 'جودة منخفضة', 'أسعار مرتفعة', 'موقع غير مناسب', 'موظفين غير ودودين']

def generate_comment(rating):
    if rating >= 4:
        num_pos, num_neg = random.randint(2, 4), random.randint(0, 1)
    elif rating >= 3:
        num_pos, num_neg = random.randint(1, 2), random.randint(1, 2)
    else:
        num_pos, num_neg = random.randint(0, 1), random.randint(2, 3)
    
    positive = random.sample(POSITIVE_TAGS, min(num_pos, len(POSITIVE_TAGS)))
    negative = random.sample(NEGATIVE_TAGS, min(num_neg, len(NEGATIVE_TAGS))) if num_neg > 0 else []
    
    parts = positive + negative
    random.shuffle(parts)
    return ', '.join(parts)

def main():
    print("🚀 Adding test reviews...")
    print("="*50)
    
    # List merchants
    merchants = Merchant.objects.all()
    print("\n📋 Available merchants:")
    for m in merchants:
        print(f"  {m.id}. {m.business_name}")
    
    merchant_id = int(input("\n🔢 Enter merchant ID: "))
    num_reviews = int(input("📝 Number of reviews (default 30): ") or "30")
    
    try:
        merchant = Merchant.objects.get(id=merchant_id)
        print(f"\n✅ Found: {merchant.business_name}")
    except:
        print("❌ Merchant not found!")
        return
    
    # Create test users
    test_emails = ['user1@test.com', 'user2@test.com', 'user3@test.com', 
                   'customer@example.com', 'reviewer@test.com', 'ahmad@test.com',
                   'sara@test.com', 'mohammed@test.com', 'fatima@test.com', 'ali@test.com']
    
    users = []
    for email in test_emails:
        user, _ = User.objects.get_or_create(email=email, defaults={'full_name': email.split('@')[0]})
        users.append(user)
    
    print(f"✅ Got {len(users)} users")
    
    # Delete ALL old reviews for this merchant
    old_count = Review.objects.filter(merchant=merchant).count()
    if old_count > 0:
        print(f"\n⚠️  Found {old_count} existing reviews for this merchant")
        confirm = input(f"Delete all {old_count} reviews and create {num_reviews} new ones? (yes/no): ").lower()
        if confirm == 'yes':
            deleted = Review.objects.filter(merchant=merchant).delete()[0]
            print(f"✅ Deleted {deleted} old reviews")
        else:
            print("❌ Cancelled")
            return
    
    # Create new reviews
    print(f"\n📝 Creating {num_reviews} reviews...")
    now = datetime.now()
    
    for i in range(num_reviews):
        rating = random.choices([1, 2, 3, 4, 5], weights=[1, 2, 3, 7, 12])[0]
        comment = generate_comment(rating)
        user = random.choice(users)
        created_at = now - timedelta(days=random.randint(0, 60))
        
        Review.objects.create(
            merchant=merchant,
            user=user,
            rating=rating,
            comment=comment,
            created_at=created_at
        )
        
        if (i + 1) % 5 == 0:
            print(f"  ✓ {i + 1}/{num_reviews}")
    
    # Stats
    total = Review.objects.filter(merchant=merchant).count()
    avg = Review.objects.filter(merchant=merchant).aggregate(Avg('rating'))['rating__avg']
    
    print(f"\n" + "="*50)
    print(f"✅ Created {num_reviews} reviews!")
    print(f"📊 Total reviews: {total}")
    print(f"⭐ Average rating: {avg:.2f}")
    print("="*50)

if __name__ == '__main__':
    main()
