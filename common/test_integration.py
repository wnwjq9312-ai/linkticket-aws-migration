import json
from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import Member
from payments.mock_data import DATES, SEATS, CARDS
from payments.forms import MockPaymentForm


class IntegrationTests(TestCase):
    def setUp(self):
        self.member = Member.objects.create_user(username='ui-test', password='test-only-pass-123', email='ui@example.invalid')
        self.staff = Member.objects.create_user(username='staff-test',email='staff-test@example.invalid', password='test-only-pass-123', is_staff=True)
        self.admin = Member.objects.create_superuser(username='admin-test', password='test-only-pass-123', email='admin@example.invalid')

    def test_public_pages_and_shared_shell(self):
        routes=['/','/login/','/register/','/performances/','/performance/demo-iu/','/booking/',
            '/booking/checkout/','/notices/','/events/','/events/detail/?id=1','/nft/',
            '/nft/guide/','/nft/payment/?id=1','/nft/complete/?id=1',
            '/help/faq/','/help/terms/','/help/privacy/','/api/login/','/api/register/']
        for route in routes:
            with self.subTest(route=route):
                res=self.client.get(route)
                self.assertEqual(res.status_code,200)
                self.assertContains(res,'class="site-header"',count=1)
                self.assertContains(res,'class="site-footer"',count=1)

    def test_signup_terms_and_password_confirmation(self):
        self.client.post('/register/', {'stage':'information','username':'blocked','password':'abcdef1234'})
        self.assertFalse(Member.objects.filter(username='blocked').exists())
        self.client.post('/register/', {'stage':'terms','terms':'on','privacy':'on','age':'on'})
        res=self.client.post('/register/', {'stage':'information','username':'new-user','password':'abcdef1234',
            'password_confirm':'abcdef1234','first_name':'테스트','email':'new@example.invalid'})
        self.assertRedirects(res,'/register/complete/')
        self.assertTrue(Member.objects.get(username='new-user').check_password('abcdef1234'))

    def test_login_csrf_and_safe_redirect(self):
        client=Client(enforce_csrf_checks=True)
        self.assertEqual(client.post('/api/auth/login/',data=json.dumps({'login_id':'ui-test','password':'test-only-pass-123'}),content_type='application/json').status_code,403)
        client.get('/login/')
        csrf=client.cookies['csrftoken'].value
        res=client.post('/api/auth/login/',data=json.dumps({'login_id':'ui-test','password':'test-only-pass-123'}),content_type='application/json',HTTP_X_CSRFTOKEN=csrf)
        self.assertEqual(res.status_code,200)
        self.assertEqual(res.json()['data']['role'],'USER')
        res=self.client.post('/login/?next=https://example.invalid', {'username':'ui-test','password':'test-only-pass-123'})
        self.assertEqual(res.url,'/')

    def test_member_pages(self):
        self.assertEqual(self.client.get('/mypage/').status_code,302)
        self.client.force_login(self.member)
        for section in ['profile','reservations','tickets','coupons','interests','nft','password','notifications']:
            self.assertEqual(self.client.get('/mypage/'+section+'/').status_code,200)

    def test_staff_admin_boundaries_and_adapters(self):
        self.client.force_login(self.member)
        self.assertEqual(self.client.get('/api/admin/members/').status_code,403)
        self.assertEqual(self.client.post('/api/staff/performances/',{}).status_code,403)
        self.client.force_login(self.staff)
        self.assertEqual(self.client.get('/api/admin/dashboard/overview/').status_code,403)
        self.assertEqual(self.client.get('/api/staff/notices/').status_code,200)
        self.client.force_login(self.admin)
        self.assertEqual(self.client.get('/api/admin/dashboard/overview/').status_code,200)
        res=self.client.post('/api/admin/staff/',data=json.dumps({'login_id':'issued-staff','name':'직원','email':'staff@example.invalid','password':'test-staff-password'}),content_type='application/json')
        self.assertEqual(res.status_code,201)
        self.assertTrue(Member.objects.get(username='issued-staff').is_staff)
        res=self.client.patch(f'/api/admin/members/{self.member.pk}/status/',data=json.dumps({'member_status':'SUSPENDED'}),content_type='application/json')
        self.assertEqual(res.status_code,200)
        self.assertIsNone(self.client.login(username='ui-test',password='test-only-pass-123') or None)

    def payment_data(self):
        self.client.get('/booking/checkout/')
        return dict(date=DATES[0]['id'],grade='VIP',seats=json.dumps([next(k for k,v in SEATS.items() if v['grade']=='VIP' and v['status']=='available')]),
             discount='youth',method='신용카드',card=CARDS[0],installment='일시불',approval_code='DEMO',
             terms_finance='on',terms_privacy='on',terms_provider='on',attempt=self.client.session['payment_attempt'])

    def test_mock_payment_receipt_and_duplicate_submit(self):
        data=self.payment_data()
        res=self.client.post('/booking/mock-pay/',data)
        self.assertRedirects(res,'/booking/complete/')
        first=self.client.session['payment_receipt']
        self.assertEqual(first['total'],154000-30800+2000)
        self.client.post('/booking/mock-pay/',data)
        self.assertEqual(first['code'],self.client.session['payment_receipt']['code'])
        data['discount']='none'
        self.assertEqual(self.client.post('/booking/mock-pay/',data).url,'/booking/checkout/')

    def test_payment_rejects_invalid_seats_card_and_attempt(self):
        data=self.payment_data()
        for changes in [{'seats':'["1-1"]'},{'card':''},{'seats':'["2-5","2-5"]'},{'approval_code':'invalid'},{'terms_finance':''}]:
            with self.subTest(changes=changes):
                self.assertFalse(MockPaymentForm({**data,**changes}).is_valid())
        self.assertEqual(self.client.post('/booking/mock-pay/',{**data,'attempt':'forged'}).url,'/booking/checkout/')
        self.assertNotIn('payment_receipt',self.client.session)

    def test_filters_and_map_without_key(self):
        self.assertContains(self.client.get('/performances/?q=IU'),'IU 2026')
        self.assertContains(self.client.get('/performances/?q=NO-MATCH'),'검색 조건에 맞는 공연이 없습니다.')
        with self.settings(KAKAO_MAP_JS_KEY=''):
            res=self.client.get('/booking/')
            self.assertEqual(res.status_code,200)
            self.assertContains(res,'lt-venue-config')

    def test_staff_catalog_notice_and_admin_dashboard_flow(self):
        self.client.force_login(self.staff)
        def post(url, data):
            res = self.client.post(url, data=json.dumps(data), content_type='application/json')
            self.assertEqual(res.status_code, 201, res.content)
            return res.json()['data']
        performance = post('/api/staff/performances/', dict(performance_name='검증 공연',
            genre='CONCERT', venue_name='서울 공연장', address='서울', base_price=10000, total_seats=2))
        pk = performance['performance_id']
        schedule = post(f'/api/staff/performances/{pk}/schedules/', dict(performance_date='2026-11-15',
            start_time='19:00', end_time='21:00', sale_start_at='2026-10-01T10:00:00+09:00',
            sale_end_at='2026-11-15T18:00:00+09:00'))
        post(f"/api/staff/schedules/{schedule['schedule_id']}/seats/", {'seats': [
            dict(seat_number=n, seat_grade='VIP', seat_price=10000) for n in ('A1','A2')]})
        res = self.client.patch(f'/api/staff/performances/{pk}/',
            data=json.dumps({'performance_status':'PUBLISHED'}), content_type='application/json')
        self.assertEqual(res.status_code, 200)
        self.assertContains(self.client.get('/performances/'), '검증 공연')
        self.assertContains(self.client.get(f'/performance/{pk}/'), '서울 공연장')
        notice = post('/api/staff/notices/', dict(notice_type='NOTICE', title='검증 공지', content='공지 본문', is_published=True))
        self.assertContains(self.client.get('/notices/'), '검증 공지')
        self.assertEqual(self.client.delete(f"/api/staff/notices/{notice['notice_id']}/").status_code, 200)
        from notices.models import Notice
        self.assertFalse(Notice.objects.filter(pk=notice["notice_id"]).exists())
        self.client.force_login(self.admin)
        res = self.client.get(f'/api/admin/dashboard/performances/{pk}/')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()['data']['total_available'], 2)
