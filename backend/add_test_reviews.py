#!/usr/bin/env python3
"""
Script to add 30 test reviews for a merchant
"""

import os
import sys
import django
import random
from datetime import datetime, timedelta

# Setup Django
sys.path.append('/mnt/c/Users/mus_2/GitHub/TawfirProject')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tawfir_backend.settings')
django.setup()

from merchants.models import Merchant, Review
from django.contrib.auth import get_user_model

User = get_user_model()

# Sample review comments with tags
POSITIVE_TAGS = [
    'خدمة ممتازة',
    'جودة عالية',
    'أسعار مناسبة',
    'موقع ممتاز',
    'نظافة',
    'موظفين ودودين'
]

NEGATIVE_TAGS = [
    'خدمة بطيئة',
    'جودة منخفضة',
    'أسعار مرتفعة',
    'موقع غير مناسب',
    'موظفين غير ودودين'
]

NEUTRAL_COMMENTS = [
    'تجربة عادية',
    'يمكن أن يكون أفضل',
    'محل متوسط',
    'لا بأس به'
]

def generate_review_comment(rating):
    """Generate a realistic review comment based on rating"""
    if rating >= 4:
        # Positive review
        num_positive = random.randint(2, 4)
        num_negative = random.randint(0, 1)
        
        positive = random.sample(POSITIVE_TAGS, num_positive)
        negative = random.sample(NEGATIVE_TAGS, num_negative) if num_negative > 0 else []
        
        comment_parts = positive + negative
        random.shuffle(comment_parts)
        return ', '.join(comment_parts)
        
    elif rating >= 3:
        # Mixed review
        num_positive = random.randint(1, 2)
        num_negative = random.randint(1, 2)
        
        positive = random.sample(POSITIVE_TAGS, num_positive)
        negative = random.sample(NEGATIVE_TAGS, num_negative)
        
        comment_parts = positive + negative
        random.shuffle(comment_parts)
        return ', '.join(comment_parts)
        
    else:
        # Negative review
        num_positive = random.randint(0, 1)
        num_negative = random.randint(2, 3)
        
        positive = random.sample(POSITIVE_TAGS, num_positive) if num_positive > 0 else []
        negative = random.sample(NEGATIVE_TAGS, num_negative)
        
        comment_parts = positive + negative
        random.shuffle(comment_parts)
        return ', '.join(comment_parts)

def add_test_reviews(merchant_id, num_reviews=30):
    """Add test reviews for a merchant"""
    
    try:
        merchant = Merchant.objects.get(id=merchant_id)
        print(f"✅ Found merchant: {merchant.business_name}")
    except Merchant.DoesNotExist:
        print(f"❌ Merchant with ID {merchant_id} not found!")
        return
    
    # Get or create test users
    test_emails = [
        'user1@test.com',
        'user2@test.com', 
        'user3@test.com',
        'customer@example.com',
        'reviewer@test.com',
        'ahmad@test.com',
        'sara@test.com',
        'mohammed@test.com',
        'fatima@test.com',
        'ali@test.com'
    ]
    
    users = []
    for email in test_emails:
        user, created = User.objects.get_or_create(
            email=email,
            defaults={'username': email.split('@')[0]}
        )
        users.append(user)
    
    print(f"✅ Created/found {len(users)} test users")
    
    # Delete existing test reviews for this merchant
    deleted_count = Review.objects.filter(
        merchant=merchant,
        user__email__in=test_emails
    ).delete()[0]
    
    if deleted_count > 0:
        print(f"🗑️  Deleted {deleted_count} existing test reviews")
    
    # Create new reviews
    reviews_created = 0
    now = datetime.now()
    
    for i in range(num_reviews):
        # Random rating (weighted towards higher ratings)
        rating_weights = [1, 2, 3, 7, 12]  # 1*, 2*, 3*, 4*, 5*
        rating = random.choices([1, 2, 3, 4, 5], weights=rating_weights)[0]
        
        # Generate comment
        comment = generate_review_comment(rating)
        
        # Random user
        user = random.choice(users)
        
        # Random date (within last 60 days)
        days_ago = random.randint(0, 60)
        created_at = now - timedelta(days=days_ago)
        
        # Create review
        review = Review.objects.create(
            merchant=merchant,
            user=user,
            rating=rating,
            comment=comment,
            created_at=created_at
        )
        
        reviews_created += 1
        
        # Print progress
        if (i + 1) % 5 == 0:
            print(f"📝 Created {i + 1}/{num_reviews} reviews...")
    
    print(f"\n✅ Successfully created {reviews_created} reviews!")
    print(f"📊 Total reviews for {merchant.business_name}: {Review.objects.filter(merchant=merchant).count()}")
    
    # Calculate average rating
    from django.db.models import Avg
    avg_rating = Review.objects.filter(merchant=merchant).aggregate(Avg('rating'))['rating__avg']
    print(f"⭐ Average rating: {avg_rating:.2f}")

if __name__ == '__main__':
    print("🚀 Starting review creation script...")
    print("=" * 50)
    
    # Get merchant ID
    if len(sys.argv) > 1:
        merchant_id = int(sys.argv[1])
    else:
        # List all merchants
        print("\n📋 Available merchants:")
        merchants = Merchant.objects.all()
        for m in merchants:
            print(f"  ID: {m.id} - {m.business_name}")
        
        merchant_id = int(input("\n🔢 Enter merchant ID: "))
    
    # Get number of reviews
    if len(sys.argv) > 2:
        num_reviews = int(sys.argv[2])
    else:
        num_reviews = 30
    
    print(f"\n📝 Adding {num_reviews} reviews to merchant ID: {merchant_id}")
    print("=" * 50)
    
    add_test_reviews(merchant_id, num_reviews)
    
    print("\n" + "=" * 50)
    print("✅ Done!")
