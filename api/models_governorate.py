# Add to api/models.py

class Governorate(models.Model):
    """نموذج المحافظات"""
    name = models.CharField(max_length=100, verbose_name="اسم المحافظة")
    name_en = models.CharField(max_length=100, blank=True, null=True, verbose_name="الاسم بالإنجليزية")
    image = models.ImageField(upload_to='governorates/', blank=True, null=True, verbose_name="صورة المحافظة")
    icon = models.CharField(max_length=50, blank=True, null=True, verbose_name="أيقونة", help_text="اسم الأيقونة من Ionicons")
    color = models.CharField(max_length=7, default="#3b82f6", verbose_name="اللون المميز", help_text="لون hex للمحافظة")
    description = models.TextField(blank=True, null=True, verbose_name="وصف المحافظة")
    population = models.IntegerField(blank=True, null=True, verbose_name="عدد السكان")
    order = models.IntegerField(default=0, verbose_name="الترتيب")
    is_active = models.BooleanField(default=True, verbose_name="نشط")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإضافة")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="آخر تحديث")
    
    class Meta:
        verbose_name = "محافظة"
        verbose_name_plural = "المحافظات"
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name
    
    @property
    def cities_count(self):
        """عدد المدن في المحافظة"""
        return self.cities.filter(is_active=True).count()
    
    @property
    def offers_count(self):
        """عدد العروض في المحافظة"""
        return Offer.objects.filter(city__governorate=self, is_active=True).count()
    
    @property
    def active_cities(self):
        """المدن النشطة في المحافظة"""
        return self.cities.filter(is_active=True).order_by('name')


# Update City model to add governorate relationship
# Add this field to the existing City model:
"""
governorate = models.ForeignKey(
    'Governorate', 
    on_delete=models.SET_NULL, 
    null=True, 
    blank=True,
    related_name='cities',
    verbose_name="المحافظة"
)
is_active = models.BooleanField(default=True, verbose_name="نشط")
"""
