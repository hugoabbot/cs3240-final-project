from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.utils.functional import SimpleLazyObject

# setup test environment
User = get_user_model()

class UserAccessTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.index_url = reverse('index')
        self.disclaimer_url = reverse('disclaimer')
        
        # Create users
        self.user = User.objects.create_user(username='user', password='password')
        self.admin = User.objects.create_user(username='admin', password='password')
        
        # Create and assign groups
        self.common_users_group, _ = Group.objects.get_or_create(name='Common Users')
        self.site_admins_group, _ = Group.objects.get_or_create(name='Site Admins')
        self.common_users_group.user_set.add(self.user)
        self.site_admins_group.user_set.add(self.admin)

    def login_user(self):
        self.client.login(username='user', password='password')

    def login_admin(self):
        self.client.login(username='admin', password='password')
   
    def is_user_instance(user):
        if isinstance(user, SimpleLazyObject):
            user = user._wrapped
        return isinstance(user, User)

# Testing Views: 
    def test_index_view_for_admin_users(self):
        self.login_admin()
        response = self.client.get(self.index_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'stafflogin.html')

    def test_disclaimer_view_access(self):
        response = self.client.get(self.disclaimer_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'disclaimer.html')

    def test_add_to_common_users(self):
        self.login_user()
        response = self.client.get(self.index_url)
        self.user.refresh_from_db()
        self.assertTrue(self.common_users_group in self.user.groups.all())
        self.assertTemplateUsed(response, 'commonlogin.html')
