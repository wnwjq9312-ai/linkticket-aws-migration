from django.test import TestCase
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import PBKDF2PasswordHasher
from accounts.models import Member
from accounts.views import LoginView
from rest_framework.test import APIRequestFactory


class PreservingAuthenticationTests(TestCase):
    def setUp(self):
        self.member = Member.objects.create_user(username='preserved',email='preserved@example.invalid', password='fixture-password')

    def test_old_hash_is_verified_without_reencoding(self):
        encoded = PBKDF2PasswordHasher().encode('fixture-password', 'fixture-salt', iterations=1000)
        Member.objects.filter(pk=self.member.pk).update(password=encoded)
        self.assertEqual(authenticate(username='preserved',email='preserved@example.invalid', password='fixture-password').pk, self.member.pk)
        self.client.post('/login/', {'username':'preserved', 'password':'fixture-password'})
        self.member.refresh_from_db()
        self.assertEqual(self.member.password, encoded)

    def test_inactive_rejected_by_both_login_routes(self):
        self.member.member_status = 'SUSPENDED'
        self.member.save(update_fields=['member_status'])
        self.assertIsNone(authenticate(username='preserved',email='preserved@example.invalid', password='fixture-password'))
        request = APIRequestFactory().post('/', {'username':'preserved', 'password':'fixture-password'})
        self.assertEqual(LoginView.as_view()(request).status_code, 400)
        self.client.post('/login/', {'username':'preserved', 'password':'fixture-password'})
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_unrecognized_hash_is_not_changed(self):
        Member.objects.filter(pk=self.member.pk).update(password='unknown-fixture-format')
        self.assertIsNone(authenticate(username='preserved',email='preserved@example.invalid', password='fixture-password'))
        self.member.refresh_from_db()
        self.assertEqual(self.member.password, 'unknown-fixture-format')

    def test_deactivated_session_is_not_restored(self):
        self.client.force_login(self.member)
        Member.objects.filter(pk=self.member.pk).update(member_status='SUSPENDED')
        self.assertEqual(self.client.get('/mypage/').status_code, 302)
