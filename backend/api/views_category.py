from rest_framework.views import APIView
from rest_framework.response import Response
from api.models import Category

class CategoryListView(APIView):
    """قائمة الفئات"""
    
    def get(self, request):
        categories = Category.objects.filter(is_active=True).order_by('order', 'name')
        data = []
        
        for category in categories:
            data.append({
                'id': category.id,
                'name': category.name,
                'name_en': category.name_en,
                'icon': category.icon,
                'color': category.color,
                'offers_count': category.offers_count,
            })
        
        return Response(data)
