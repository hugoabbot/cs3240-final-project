from django.test import TestCase
from django.test import override_settings
from django.test import TestCase, RequestFactory
from django.contrib.sites.models import Site
from django.conf import settings
from utilities.middleware.dynamicsiteid import DynamicSiteIDMiddleware
from unittest.mock import patch
from unittest.mock import patch, call

class PlaceholderTests(TestCase):
    def test_placeholder(self):
        """
        A simple test case that always passes.
        This is used to check that tests are being discovered and run.
        """
        self.assertTrue(True)


class DynamicSiteIDMiddlewareTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.default_site = Site.objects.create(domain='default.com', name='Default Site')
        settings.SITE_ID = self.default_site.id

    @override_settings(ALLOWED_HOSTS=['example2.com'])
    def test_middleware_with_existing_domain(self):
        # Create a mock site
        mock_site = Site.objects.create(domain='example2.com', name='Example2')
        
        # Create a request with the mock site's domain
        request = self.factory.get('/', HTTP_HOST=mock_site.domain)
        
        # Patch the get method of the Site.objects to return the mock site
        with patch('django.contrib.sites.models.Site.objects.get', return_value=mock_site) as mock_get:
            middleware = DynamicSiteIDMiddleware(lambda req: req)
            middleware(request)
            
            # Check if the request now has the current_site attribute set to mock_site
            self.assertEqual(request.current_site, mock_site)
            mock_get.assert_called_once_with(domain=mock_site.domain)
    
    @override_settings(ALLOWED_HOSTS=['nonexistent.com'])
    def test_middleware_with_nonexistent_domain_fallbacks_to_default(self):
        # Create a request with a nonexistent domain
        request = self.factory.get('/', HTTP_HOST='nonexistent.com')
        
        # Patch the get method of the Site.objects to raise DoesNotExist on the first call and return default on second call
        with patch('django.contrib.sites.models.Site.objects.get', side_effect=[Site.DoesNotExist, self.default_site]) as mock_get:
            middleware = DynamicSiteIDMiddleware(lambda req: req)
            middleware(request)
            
            # Check if the request now has the current_site attribute set to the default site
            self.assertEqual(request.current_site, self.default_site)
            self.assertEqual(mock_get.call_count, 2)
            calls = [call(domain='nonexistent.com'), call(id=settings.SITE_ID)]
            mock_get.assert_has_calls(calls, any_order=True)

