"""
Add test reviews using Django shell
Copy and paste this code into Django shell
"""

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

# 1. List merchants
print("📋 Available merchants:")
for m in Merchant.objects.all():
    print(f"  {m.id}. {m.business_name}")

# 2. Set merchant ID (CHANGE THIS!)
merchant_id = 1  # ⚠️ غير هذا الرقم لمعرف التاجر الصحيح
num_reviews = 30

merchant = Merchant.objects.get(id=merchant_id)
print(f"\n✅ Selected: {merchant.business_name}")

# 3. Create test users
test_emails = ['user1@test.com', 'user2@test.com', 'user3@test.com', 
               'customer@example.com', 'reviewer@test.com', 'ahmad@test.com',
               'sara@test.com', 'mohammed@test.com', 'fatima@test.com', 'ali@test.com']

users = []
for email in test_emails:
    user, _ = User.objects.get_or_create(email=email, defaults={'username': email.split('@')[0]})
    users.append(user)

print(f"✅ Got {len(users)} users")

# 4. Delete old test reviews
deleted = Review.objects.filter(merchant=merchant, user__email__in=test_emails).delete()[0]
if deleted:
    print(f"🗑️  Deleted {deleted} old test reviews")

# 5. Create new reviews
print(f"\n📝 Creating {num_reviews} reviews...")
now = datetime.now()
created = 0

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
    created += 1
    
    if (i + 1) % 5 == 0:
        print(f"  ✓ {i + 1}/{num_reviews}")

# 6. Show stats
total = Review.objects.filter(merchant=merchant).count()
avg = Review.objects.filter(merchant=merchant).aggregate(Avg('rating'))['rating__avg']

print(f"\n{'='*50}")
print(f"✅ Created {created} reviews!")
print(f"📊 Total reviews: {total}")
print(f"⭐ Average rating: {avg:.2f}")
print(f"{'='*50}")
