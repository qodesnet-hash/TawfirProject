from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from api.models import Governorate, City, Offer

class GovernorateListView(APIView):
    """قائمة المحافظات"""
    
    def get(self, request):
        governorates = Governorate.objects.filter(is_active=True).order_by('order', 'name')
        data = []
        
        for governorate in governorates:
            data.append({
                'id': governorate.id,
                'name': governorate.name,
                'name_en': governorate.name_en,
                'image': request.build_absolute_uri(governorate.image.url) if governorate.image else None,
                'icon': governorate.icon,
                'color': governorate.color,
                'description': governorate.description,
                'population': governorate.population,
                'cities_count': governorate.cities_count,
                'offers_count': governorate.offers_count,
            })
        
        return Response(data)

class GovernorateDetailView(APIView):
    """تفاصيل المحافظة"""
    
    def get(self, request, pk):
        governorate = get_object_or_404(Governorate, pk=pk, is_active=True)
        
        data = {
            'id': governorate.id,
            'name': governorate.name,
            'name_en': governorate.name_en,
            'image': request.build_absolute_uri(governorate.image.url) if governorate.image else None,
            'icon': governorate.icon,
            'color': governorate.color,
            'description': governorate.description,
            'population': governorate.population,
            'cities_count': governorate.cities_count,
            'offers_count': governorate.offers_count,
            'cities': []
        }
        
        # Add cities
        for city in governorate.cities.filter(is_active=True):
            data['cities'].append({
                'id': city.id,
                'name': city.name,
                'image': request.build_absolute_uri(city.image.url) if city.image else None,
                'offers_count': Offer.objects.filter(city=city, status='مقبول').count()
            })
        
        return Response(data)

class GovernorateCitiesView(APIView):
    """مدن المحافظة"""
    
    def get(self, request, governorate_id):
        governorate = get_object_or_404(Governorate, pk=governorate_id, is_active=True)
        cities = governorate.cities.filter(is_active=True).order_by('name')
        
        cities_data = []
        for city in cities:
            cities_data.append({
                'id': city.id,
                'name': city.name,
                'image': request.build_absolute_uri(city.image.url) if city.image else None,
                'latitude': city.latitude,
                'longitude': city.longitude,
                'offers_count': Offer.objects.filter(city=city, status='مقبول').count()
            })
        
        return Response({
            'governorate': {
                'id': governorate.id,
                'name': governorate.name,
                'name_en': governorate.name_en,
                'color': governorate.color,
                'description': governorate.description,
                'population': governorate.population,
            },
            'cities': cities_data
        })
