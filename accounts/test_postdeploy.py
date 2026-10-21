"""Regression coverage for the production login/profile and role failures."""
import json
from datetime import timedelta
from io import StringIO
from unittest.mock import patch

from django.core.management import call_command, CommandError
from django.db import connection
from django.test import TestCase, override_settings
from django.test.utils import CaptureQueriesContext
from django.utils import timezone

from accounts.models import Member
from accounts.serializers import RegisterSerializer
from common.ui_forms import ProfileForm
from notices.models import Notice


class PostDeploymentTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.members = {
            role: Member.objects.create_user(
                username=role.lower(), email=role.lower()+'@example.invalid',
                password='local-test-password-837', role=role,
            ) for role in ('USER', 'STAFF', 'ADMIN')
        }

    def test_signup_optional_and_invalid_profile(self):
        base = dict(username='new', email='new@example.invalid', password='local-test-password-837')
        for extra in ({'birth_date':'','gender':''}, {'birth_date':'2000-01-02','gender':'F'}):
            serializer = RegisterSerializer(data={**base, **extra})
            self.assertTrue(serializer.is_valid(), serializer.errors)
        for extra in ({'gender':'ADMIN'}, {'birth_date':str(timezone.localdate()+timedelta(days=1))}):
            serializer = RegisterSerializer(data={**base, **extra})
            self.assertFalse(serializer.is_valid())
        serializer = RegisterSerializer(data={**base, 'birth_date':'2000-01-02','gender':'M', 'role':'ADMIN'})
        self.assertTrue(serializer.is_valid(), serializer.errors)
        member = serializer.save()
        self.assertEqual((str(member.birth_date),member.gender,member.role), ('2000-01-02','M','USER'))
        self.assertEqual(Member._meta.get_field('gender').max_length, 10)

    def test_profile_rejects_future_birth(self):
        form = ProfileForm(data={'birth_date':str(timezone.localdate()+timedelta(days=1))}, instance=self.members['USER'])
        self.assertFalse(form.is_valid())

    @override_settings(COLLECTIBLE_LINKS_ENABLED=False)
    def test_login_home_and_profile_without_unrelated_queries(self):
        before = self.members['USER'].password
        response = self.client.post('/login/', {'username':'user','password':'local-test-password-837'})
        self.assertRedirects(response, '/')
        self.members['USER'].refresh_from_db()
        self.assertEqual(before, self.members['USER'].password)
        with CaptureQueriesContext(connection) as queries:
            self.assertEqual(self.client.get('/mypage/').status_code, 200)
        sql = ' '.join(q['sql'] for q in queries)
        for unrelated in ('digital_collectible','reservation','coupon','ticket'):
            self.assertNotIn('"'+unrelated+'"', sql)
        for section in ('reservations','tickets','coupons','nft'):
            self.assertEqual(self.client.get('/mypage/'+section+'/').status_code,200)

    def test_role_matrix_including_direct_urls(self):
        for path in ('/dashboard/','/staff/'):
            self.assertEqual(self.client.get(path).status_code,302)
        for role, dashboard, staff in (('USER',403,403),('STAFF',403,200),('ADMIN',200,200)):
            self.client.force_login(self.members[role])
            self.assertEqual(self.client.get('/dashboard/').status_code,dashboard)
            self.assertEqual(self.client.get('/staff/').status_code,staff)
            self.assertEqual(self.client.get('/api/admin/members/').status_code,dashboard)
            self.assertEqual(self.client.get('/api/staff/notices/').status_code,staff)

    def test_staff_notice_saved_and_public(self):
        self.client.force_login(self.members['STAFF'])
        payload = {'title':'직원 공지 검증','content':'공개 공지 본문','notice_type':'NOTICE','is_published':True}
        response = self.client.post('/api/staff/notices/', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code,201)
        row = Notice.objects.get(title=payload['title'])
        self.assertEqual(row.author_id,self.members['STAFF'].pk)
        self.assertEqual(row.content,payload['content'])
        self.assertEqual(row.notice_type,'공지')
        self.assertTrue(row.is_published)
        self.client.logout()
        self.assertContains(self.client.get('/notices/'),payload['title'])

    def test_provision_never_resets_existing_account(self):
        before = self.members['ADMIN'].password
        with patch('getpass.getpass') as prompt:
            with self.assertRaises(CommandError):
                call_command('provision_member', username='admin', email='admin@example.invalid', role='ADMIN', stdout=StringIO())
            prompt.assert_not_called()
        self.members['ADMIN'].refresh_from_db()
        self.assertEqual(before,self.members['ADMIN'].password)
