from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from allauth.socialaccount.models import SocialApp
from django.contrib.sites.models import Site


class PlaceholderTests(TestCase):
    def test_placeholder(self):
        """
        A simple test case that always passes.
        This is used to check that tests are being discovered and run.
        """
        self.assertTrue(True)

class ViewsTests(TestCase):

    def setUp(self):
        site = Site.objects.get_current()
        self.social_app = SocialApp.objects.create(
            provider='google',
            name='Google',
            client_id='fake_client_id',
            secret='fake_secret'
        )
        self.social_app.sites.add(site)
        

    def test_logout_redirects_to_index(self):
        # Creating a test user for the logout test
        self.user = User.objects.create_user(username='testuser', email='testuser@example.com', password='testpassword123')

        # Defining URLs used in the logout test
        self.logout_url = reverse('custom_logout')  
        self.index_url = reverse('index')  # Assuming you have an URL name 'index' for your homepage or landing page
        
        # First, log the user in
        self.client.force_login(self.user)  # Using force_login for simplicity
        
        # Simulate clicking the "logout" button by making a request to the logout URL
        response = self.client.get(self.logout_url)
        
        # Check that after logging out, the user is redirected to the index page
        self.assertRedirects(response, self.index_url)