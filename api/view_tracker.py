# api/view_tracker.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.db.models import F
from .models import Offer
from rest_framework import status

class RecordOfferViewView(APIView):
    """تسجيل مشاهدة للعرض"""
    permission_classes = [AllowAny]
    
    def post(self, request, offer_id):
        try:
            offer = Offer.objects.get(id=offer_id)
            offer.views_count = F('views_count') + 1
            offer.save(update_fields=['views_count'])
            offer.refresh_from_db()
            
            return Response({
                'success': True,
                'views_count': offer.views_count
            })
        except Offer.DoesNotExist:
            return Response(
                {'error': 'العرض غير موجود'},
                status=status.HTTP_404_NOT_FOUND
            )