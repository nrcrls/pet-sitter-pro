from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase


class CustomUserTests(TestCase):
    def test_create_user(self):
        User = get_user_model()
        user = User.objects.create_user(
            username="test1", email="test@email.com", password="testpass123"
        )
        self.assertEqual(user.username, "test1")
        self.assertEqual(user.email, "test@email.com")
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_superuser(self):
        User = get_user_model()
        admin_user = User.objects.create_superuser(
            username="superadmin", email="superadmin@email.com", password="testpass123"
        )
        self.assertEqual(admin_user.username, "superadmin")
        self.assertEqual(admin_user.email, "superadmin@email.com")
        self.assertTrue(admin_user.is_active)
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)

# class SignUpPageTests(TestCase):
#     def setUp(self):
#         url = reverse("signup")
#         self.response = self.client.get(url)
    
#     def test_signup_template(self):
#         self.assertEqual(self.response.status_code, 200)
#         self.assertTemplateUsed(self.response, "/signup.html")
#         self.assertContains(self.response, "Sign Up")
#         self.assertNotContains(self.response, "Hi there! I should not be on the page.")