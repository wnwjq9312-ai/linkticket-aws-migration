import io
import json
import tempfile
from PIL import Image
from django.test import TestCase, Client, override_settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from datetime import timedelta
from accounts.models import Member
from catalog.models import Performance, PerformanceSchedule, Seat
from reservations.models import Reservation, ReservationSeat
from tickets.services import issue_ticket
from events.models import DigitalCollectible, CollectibleFavorite, Event
from notices.models import Notice
from payments.booking_context import resolve_booking
from payments.mock_data import SEATS, PRICING

class PhaseTwoTests(TestCase):
    def setUp(self):
        self.user=Member.objects.create_user(username='owner',email='owner@example.invalid',password='test-password-42')
        self.other=Member.objects.create_user(username='other',email='other@example.invalid',password='test-password-42')
        self.staff=Member.objects.create_user(username='staff',email='staff@example.invalid',password='test-password-42',is_staff=True)
        self.show=Performance.objects.create(performance_name='공연 A',genre='CONCERT',venue_name='공연장 A',address='서울',base_price=100000,total_seats=160,performance_status='PUBLISHED')
        self.schedule=PerformanceSchedule.objects.create(performance=self.show,performance_date='2026-12-20',start_time='19:00',end_time='21:00',sale_start_at=timezone.now(),sale_end_at=timezone.now()+timedelta(days=20))
        self.reservation=Reservation.objects.create(member=self.user,schedule=self.schedule,reservation_code='PRIVATE-RESERVATION-A',total_amount=100000,reservation_status='CONFIRMED')
        seat=Seat.objects.create(schedule=self.schedule,seat_number='A1',seat_grade='VIP',seat_price=100000)
        rs=ReservationSeat.objects.create(reservation=self.reservation,seat=seat,price=100000)
        self.ticket,self.token=issue_ticket(rs)
        self.nft=DigitalCollectible.objects.create(member=self.user,performance=self.show,source_reservation=self.reservation,collectible_name='공연 A 기념 NFT',collectible_code='NFT-A',collectible_status='ISSUED')

    def payment(self,show_id):
        ctx=resolve_booking(show_id)
        self.client.get('/booking/checkout/',{'performance':show_id})
        data=dict(performance_id=show_id,date=ctx['dates'][0]['id'],grade='VIP',seats='["2-5"]',discount='none',method='간편결제',approval_code='DEMO',terms_finance='on',terms_privacy='on',terms_provider='on',attempt=self.client.session['payment_attempt'])
        if ctx.get('schedule_seats'):
            # UI3 now uses persisted seats for DB performances, rather than mock IDs.
            data['seats']=json.dumps([next(iter(ctx['schedule_seats'][data['date']]))])
        response=self.client.post('/booking/mock-pay/',data)
        self.assertEqual(response.url,'/booking/complete/')
        receipt=self.client.session['payment_receipt']
        self.assertEqual(receipt['title'],ctx['performance']['title'])
        self.assertEqual(receipt['venue'],ctx['performance']['venue'])
        self.assertEqual(receipt['total'],ctx['prices']['VIP']+2000)
        self.assertContains(self.client.get(response.url),ctx['performance']['title'])
        return receipt

    def test_three_performances_and_history_keep_identity(self):
        self.client.force_login(self.user)
        receipts=[self.payment(i) for i in ['demo-iu','demo-1','demo-2']]
        self.assertEqual(len({r['title'] for r in receipts}),3)
        page=self.client.get('/mypage/reservations/')
        for receipt in receipts:
            self.assertContains(page,receipt['title'])
            self.assertContains(self.client.get('/booking/complete/',{'receipt':receipt['code']}),receipt['title'])

    def test_database_schedule_and_calendar_data(self):
        second=PerformanceSchedule.objects.create(performance=self.show,performance_date='2026-12-20',start_time='21:30',end_time='23:00',sale_start_at=timezone.now(),sale_end_at=timezone.now()+timedelta(days=10))
        response=self.client.get('/booking/',{'performance':self.show.pk,'schedule':second.pk})
        self.assertEqual(response.context['mock_config']['initialSchedule'],str(second.pk))
        self.assertEqual(len(response.context['mock_config']['calendar']),2)
        self.assertEqual(response.context['mock_config']['seats'],SEATS)
        self.assertEqual(len(SEATS),160)
        receipt=self.payment(str(self.show.pk))
        self.assertEqual(receipt['schedule_id'],self.schedule.pk)
        self.assertEqual(self.client.get('/booking/?performance=invalid').status_code,404)

    def test_nft_favorite_is_account_scoped_and_persistent(self):
        url=f'/nft/{self.nft.pk}/favorite/'
        self.assertEqual(self.client.post(url,{'favorite':'1'}).status_code,302)
        self.client.force_login(self.user)
        for _ in range(2): self.client.post(url,{'favorite':'1'})
        self.assertEqual(CollectibleFavorite.objects.count(),1)
        fresh=Client();fresh.force_login(self.user)
        self.assertContains(fresh.get('/nft/?tab=favorites'),self.nft.collectible_name)
        fresh.force_login(self.other)
        self.assertNotContains(fresh.get('/nft/?tab=favorites'),self.nft.collectible_name)
        self.client.post(url,{'favorite':'0'})
        self.assertFalse(CollectibleFavorite.objects.exists())

    def test_reservation_ticket_nft_links_and_owner_privacy(self):
        self.client.force_login(self.user)
        page=self.client.get('/mypage/reservations/')
        for text in [self.reservation.reservation_code,self.ticket.ticket_code,self.nft.collectible_name]: self.assertContains(page,text)
        self.assertContains(self.client.get(f'/nft/{self.nft.pk}/'),self.reservation.reservation_code)
        self.client.force_login(self.other)
        self.assertNotContains(self.client.get(f'/nft/{self.nft.pk}/'),self.reservation.reservation_code)
        self.assertNotContains(self.client.get('/mypage/nft/'),self.nft.collectible_name)

    def nft_data(self):
        return dict(collectible_name='등록 테스트 NFT',performance=self.show.pk,member=self.user.pk,source_reservation=self.reservation.pk,ticket=self.ticket.pk,collectible_status='ISSUED')

    def test_staff_upload_registration_and_user_visibility(self):
        self.client.force_login(self.user)
        self.assertEqual(self.client.post('/staff/nft/',self.nft_data()).status_code,302)
        self.assertEqual(DigitalCollectible.objects.count(),1)
        self.client.force_login(self.staff)
        image=io.BytesIO();Image.new('RGB',(12,12),'blue').save(image,format='PNG')
        with tempfile.TemporaryDirectory() as folder,override_settings(MEDIA_ROOT=folder):
            response=self.client.post('/staff/nft/',{**self.nft_data(),'image':SimpleUploadedFile('test.png',image.getvalue(),content_type='image/png')})
            self.assertEqual(response.status_code,302)
            item=DigitalCollectible.objects.get(collectible_name='등록 테스트 NFT')
            self.assertTrue(item.image_path.startswith('nft/'))
            self.assertEqual(item.source_reservation,self.reservation)
            self.assertContains(self.client.get('/nft/'),item.collectible_name)
            self.client.force_login(self.user)
            self.assertContains(self.client.get('/mypage/nft/'),item.collectible_name)

    def test_upload_rejects_fake_image_and_mismatched_owner(self):
        self.client.force_login(self.staff)
        response=self.client.post('/staff/nft/',{**self.nft_data(),'image':SimpleUploadedFile('fake.png',b'<script>bad</script>',content_type='image/png')})
        self.assertEqual(response.status_code,200)
        self.assertEqual(DigitalCollectible.objects.count(),1)
        self.client.post('/staff/nft/',{**self.nft_data(),'member':self.other.pk})
        self.assertEqual(DigitalCollectible.objects.count(),1)

    def test_notice_crud_uses_same_records_on_home_and_public_pages(self):
        self.assertFalse(Notice.objects.exists())
        self.assertContains(self.client.get('/'),'등록된 공지가 없습니다.')
        self.client.force_login(self.staff)
        response=self.client.post('/api/staff/notices/',json.dumps(dict(notice_type='NOTICE',title='실제 공지',content='공지 내용',is_published=True)),content_type='application/json')
        pk=response.json()['data']['notice_id']
        for url in ['/','/notices/',f'/notices/{pk}/']:self.assertContains(self.client.get(url),'실제 공지')
        self.assertEqual(self.client.get(f'/api/staff/notices/{pk}/').status_code,200)
        response=self.client.patch(f'/api/staff/notices/{pk}/',json.dumps({'title':'수정된 공지'}),content_type='application/json')
        self.assertEqual(response.status_code,200)
        self.assertContains(self.client.get('/'),'수정된 공지')
        self.assertGreater(Notice.objects.get(pk=pk).view_count,0)
        self.client.delete(f'/api/staff/notices/{pk}/')
        self.assertNotContains(self.client.get('/'),'수정된 공지')
        self.assertEqual(self.client.get(f'/notices/{pk}/').status_code,404)

    def test_distinct_events_and_removed_membership(self):
        for title in ['첫 번째 이벤트','두 번째 이벤트']:
            event=Event.objects.create(performance=self.show,event_name=title,event_type='안내',event_start=timezone.now(),event_end=timezone.now()+timedelta(days=2),event_status='ACTIVE')
            self.assertContains(self.client.get(f'/events/detail/?id={event.pk}'),title)
        self.assertNotContains(self.client.get('/events/'),'event-card__like')
        self.client.force_login(self.user)
        self.assertNotContains(self.client.get('/mypage/'),'멤버십')
        self.assertRedirects(self.client.get('/mypage/membership/'),'/mypage/')
