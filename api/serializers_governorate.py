# Add to api/serializers.py

class GovernorateSerializer(serializers.ModelSerializer):
    """Serializer للمحافظات"""
    cities_count = serializers.IntegerField(read_only=True)
    offers_count = serializers.IntegerField(read_only=True)
    image = serializers.SerializerMethodField()
    
    class Meta:
        model = Governorate
        fields = [
            'id', 'name', 'name_en', 'image', 'icon', 'color',
            'description', 'population', 'cities_count', 'offers_count'
        ]
    
    def get_image(self, obj):
        request = self.context.get('request')
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None

class GovernorateDetailSerializer(serializers.ModelSerializer):
    """Serializer لتفاصيل المحافظة مع المدن"""
    cities = serializers.SerializerMethodField()
    cities_count = serializers.IntegerField(read_only=True)
    offers_count = serializers.IntegerField(read_only=True)
    image = serializers.SerializerMethodField()
    
    class Meta:
        model = Governorate
        fields = [
            'id', 'name', 'name_en', 'image', 'icon', 'color',
            'description', 'population', 'cities_count', 'offers_count',
            'cities'
        ]
    
    def get_image(self, obj):
        request = self.context.get('request')
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None
    
    def get_cities(self, obj):
        cities = obj.cities.filter(is_active=True).order_by('name')
        return CitySerializer(cities, many=True, context=self.context).data
