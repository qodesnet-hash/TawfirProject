"""
Basic tests for Tawfir App
"""
from django.test import TestCase
from django.contrib.auth import get_user_model

User = get_user_model()


class BasicTestCase(TestCase):
    """اختبارات أساسية للتأكد من عمل التطبيق"""
    
    def test_user_model_exists(self):
        """اختبار: نموذج المستخدم موجود"""
        self.assertTrue(User is not None)
    
    def test_user_creation(self):
        """اختبار: إنشاء مستخدم"""
        user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.assertEqual(user.email, 'test@example.com')
        self.assertTrue(user.check_password('testpass123'))
    
    def test_settings_loaded(self):
        """اختبار: الإعدادات تم تحميلها"""
        from django.conf import settings
        self.assertTrue(settings.SECRET_KEY is not None)
        self.assertTrue(len(settings.SECRET_KEY) > 10)


class APIEndpointsTestCase(TestCase):
    """اختبار endpoints الأساسية"""
    
    def test_api_root_exists(self):
        """اختبار: API root يعمل"""
        response = self.client.get('/api/v1/')
        # يجب أن يرجع 200 أو 301 (redirect)
        self.assertIn(response.status_code, [200, 301, 302])
    
    def test_cities_endpoint(self):
        """اختبار: endpoint المدن يعمل"""
        response = self.client.get('/api/v1/cities/')
        # قبول 200 أو 301 (redirect)
        self.assertIn(response.status_code, [200, 301])

    def test_offers_endpoint(self):
        """اختبار: endpoint العروض يعمل"""
        response = self.client.get('/api/v1/offers/')
        # قبول 200 أو 301 (redirect)
        self.assertIn(response.status_code, [200, 301])
