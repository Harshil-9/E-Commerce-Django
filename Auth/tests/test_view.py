from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth import SESSION_KEY

User = get_user_model()

class AuthViewsTest(TestCase):
    def setUp(self):
        self.login_url = reverse('login')
        self.register_url = reverse('register')
        self.index_url = reverse('index')
        self.logout_url = reverse('logout')

        self.user_data = {
            'email': 'testuser@example.com',
            'password': 'testpassword123',
            'name': 'Test User',  
        }
        self.user = User.objects.create_user(**self.user_data)

    def test_redirect_authenticated_user_from_login(self):
        self.client.login(email=self.user_data['email'], password=self.user_data['password'])
        response = self.client.get(self.login_url)
        self.assertRedirects(response, self.index_url)

    def test_custom_login_view_success(self):
        response = self.client.post(self.login_url, {
            'username': self.user_data['email'],
            'password': self.user_data['password'],
        }, follow=True)
        self.assertRedirects(response, self.index_url)
        session = self.client.session
        self.assertEqual(session['user_id'], self.user.id)
        self.assertEqual(session['username'], self.user.email)

    def test_login_invalid_credentials(self):
        response = self.client.post(self.login_url, {
            'username': self.user_data['email'],
            'password': 'wrongpassword',
        })
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertFormError(form, None, ['Please enter a correct email and password.'])  

    def test_register_view_logout_if_authenticated(self):
        self.client.login(email=self.user_data['email'], password=self.user_data['password'])
        session_before = self.client.session
        self.assertIn(SESSION_KEY, session_before)
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(SESSION_KEY, self.client.session)

    def test_register_view_form_valid(self):
        response = self.client.post(self.register_url, {
            'email': 'newuser@example.com',
            'name': 'New User',  
            'password1': 'newstrongpassword',
            'password2': 'newstrongpassword',
        }, follow=True)
        self.assertRedirects(response, self.index_url)
        user = User.objects.get(email='newuser@example.com')
        self.assertTrue(user)

    def test_logout_view_clears_session_and_redirects(self):
        self.client.login(email=self.user_data['email'], password=self.user_data['password'])
        session = self.client.session
        session['user_id'] = self.user.id
        session['username'] = self.user.email
        session.save()

        response = self.client.get(self.logout_url, follow=True)
        self.assertRedirects(response, self.login_url)
        session = self.client.session
        self.assertNotIn('user_id', session)
        self.assertNotIn('username', session)
