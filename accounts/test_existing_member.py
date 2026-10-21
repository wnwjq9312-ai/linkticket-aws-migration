"""Contract tests against the production member shape plus nullable profile columns.

All data below is synthetic; these tests never connect to the production DB.
"""
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import PBKDF2PasswordHasher
from django.db import connection
from django.test import TestCase
from django.test.utils import CaptureQueriesContext
from accounts.models import Member


class ExistingMemberContractTests(TestCase):
    def setUp(self):
        self.encoded = PBKDF2PasswordHasher().encode('fixture-password', 'legacy-fixture', iterations=1000)
        with connection.cursor() as cursor:
            cursor.execute('''INSERT INTO member
                (member_id, login_id, name, phone, email, password, role, joined_at, member_status)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)''',
                [713, 'existing-id', '기존 회원', '010-0000-0000', 'existing@example.invalid',
                 self.encoded, 'USER', '2026-01-01 00:00:00', 'ACTIVE'])

    def test_exact_columns_and_primary_key(self):
        self.assertEqual(Member._meta.db_table, 'member')
        self.assertEqual(Member._meta.pk.column, 'member_id')
        self.assertEqual(Member._meta.pk.get_internal_type(), 'AutoField')
        self.assertEqual({f.column for f in Member._meta.local_fields}, {
            'member_id', 'login_id', 'password', 'name', 'phone', 'email',
            'role', 'joined_at', 'member_status', 'birth_date', 'gender',
        })
        self.assertEqual(Member.objects.get(username='existing-id').pk, 713)

    def test_existing_row_login_preserves_every_member_column(self):
        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM member WHERE member_id=713')
            before = cursor.fetchone()
        with CaptureQueriesContext(connection) as queries:
            response = self.client.post('/api/auth/login/',
                {'login_id': 'existing-id', 'password': 'fixture-password'}, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['data']['member_id'], 713)
        self.assertEqual(self.client.session['_auth_user_backend'], 'accounts.backends.ExistingMemberBackend')
        self.assertFalse(any('accounts_member' in q['sql'] or 'auth_user' in q['sql'] for q in queries))
        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM member WHERE member_id=713')
            self.assertEqual(cursor.fetchone(), before)

    def test_unknown_role_does_not_grant_admin(self):
        Member.objects.filter(pk=713).update(role='UNKNOWN')
        user = authenticate(username='existing-id', password='fixture-password')
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_inactive_and_unknown_hash_are_denied(self):
        Member.objects.filter(pk=713).update(member_status='SUSPENDED')
        self.assertIsNone(authenticate(username='existing-id', password='fixture-password'))
        Member.objects.filter(pk=713).update(member_status='ACTIVE', password='unknown-format')
        self.assertIsNone(authenticate(username='existing-id', password='fixture-password'))
        self.assertEqual(Member.objects.get(pk=713).password, 'unknown-format')

    def test_old_auth_user_backend_session_not_reinterpreted(self):
        session = self.client.session
        session['_auth_user_id'] = '713'
        session['_auth_user_backend'] = 'django.contrib.auth.backends.ModelBackend'
        session['_auth_user_hash'] = Member.objects.get(pk=713).get_session_auth_hash()
        session.save()
        self.assertEqual(self.client.get('/mypage/').status_code, 302)
        self.assertEqual(self.client.get('/admin-site/').status_code, 404)

    def test_new_signup_hash_and_limits(self):
        from accounts.serializers import RegisterSerializer
        data = dict(username='new-member', first_name='신규', email='new@example.invalid', password='new-fixture-password')
        form = RegisterSerializer(data=data)
        self.assertTrue(form.is_valid(), form.errors)
        user = form.save()
        self.assertTrue(user.password.startswith('pbkdf2_sha256$'))
        self.assertEqual(user.role, 'USER')
        self.assertEqual(Member.objects.get(pk=713).password, self.encoded)
        self.assertFalse(RegisterSerializer(data={**data, 'username':'x'*51}).is_valid())
        self.assertFalse(RegisterSerializer(data={**data, 'email':'existing@example.invalid'}).is_valid())
        self.assertTrue(RegisterSerializer(data={**data, 'username':'another', 'email':'another@example.invalid', 'birth_date':'2000-01-01', 'gender':'F'}).is_valid())

    def test_all_member_foreign_keys_preserve_target(self):
        from reservations.models import Reservation
        from coupons.models import Coupon
        from tickets.models import Ticket
        from notices.models import Notice
        from events.models import DigitalCollectible, EventReward, CollectibleFavorite
        for model, field, column in (
            (Reservation, 'member', 'member_id'), (Coupon, 'member', 'member_id'),
            (Ticket, 'checked_by', 'checked_by'), (Notice, 'author', 'author_id'),
            (DigitalCollectible, 'member', 'member_id'), (EventReward, 'member', 'member_id'),
            (CollectibleFavorite, 'member', 'member_id'),
        ):
            with self.subTest(model=model.__name__):
                fk = model._meta.get_field(field)
                self.assertEqual(fk.column, column)
                self.assertEqual(fk.target_field.column, 'member_id')
                self.assertEqual(fk.remote_field.model._meta.db_table, 'member')
