"""
Management command to check and expire featured ads
يتحقق من الإعلانات المميزة المنتهية ويوقفها تلقائياً
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from api.models import FeaturedRequest


class Command(BaseCommand):
    help = 'Check and expire featured ads that have passed their end date'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be expired without actually expiring',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        self.stdout.write('=' * 70)
        self.stdout.write(self.style.SUCCESS('🔍 Checking for expired featured ads...'))
        self.stdout.write('=' * 70)
        
        # البحث عن الإعلانات النشطة المنتهية
        now = timezone.now()
        expired_requests = FeaturedRequest.objects.filter(
            status='active',
            end_date__lt=now
        ).select_related('offer', 'merchant', 'plan')
        
        count = expired_requests.count()
        
        if count == 0:
            self.stdout.write(self.style.SUCCESS('✅ No expired featured ads found'))
            return
        
        self.stdout.write(f'Found {count} expired featured ad(s):')
        self.stdout.write('')
        
        for request in expired_requests:
            expired_days = (now - request.end_date).days
            
            self.stdout.write(f'📌 {request.offer.title}')
            self.stdout.write(f'   Merchant: {request.merchant.business_name}')
            self.stdout.write(f'   Plan: {request.plan.name} ({request.plan.duration_days} days)')
            self.stdout.write(f'   Started: {request.start_date.strftime("%Y-%m-%d %H:%M")}')
            self.stdout.write(f'   Ended: {request.end_date.strftime("%Y-%m-%d %H:%M")}')
            self.stdout.write(f'   Expired: {expired_days} day(s) ago')
            self.stdout.write(f'   Views: {request.views_count}')
            self.stdout.write(f'   Clicks: {request.clicks_count}')
            self.stdout.write(f'   Favorites: {request.favorites_count}')
            
            if not dry_run:
                # تحديث حالة الطلب
                request.status = 'expired'
                request.save()
                
                # إيقاف العرض من المميزة
                request.offer.is_featured = False
                request.offer.featured_until = None
                request.offer.save()
                
                self.stdout.write(self.style.SUCCESS('   ✅ Expired and deactivated'))
            else:
                self.stdout.write(self.style.WARNING('   ⚠️  Would be expired (dry-run mode)'))
            
            self.stdout.write('')
        
        if not dry_run:
            self.stdout.write('=' * 70)
            self.stdout.write(self.style.SUCCESS(f'✅ Successfully expired {count} featured ad(s)'))
            self.stdout.write('=' * 70)
        else:
            self.stdout.write('=' * 70)
            self.stdout.write(self.style.WARNING(f'⚠️  Dry-run mode: {count} ad(s) would be expired'))
            self.stdout.write('=' * 70)
