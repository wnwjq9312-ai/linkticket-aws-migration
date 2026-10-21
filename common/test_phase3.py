import io
import json
import tempfile
from datetime import timedelta
from PIL import Image
from django.test import TestCase, override_settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from accounts.models import Member
from catalog.models import Performance, PerformanceSchedule, Seat
from events.models import Event, DigitalCollectible
from notices.models import Notice
from payments.booking_context import resolve_booking
from payments.forms import MockPaymentForm
from . import test_phase2

def upload(name='sample.png'):
    data=io.BytesIO();Image.new('RGB',(32,32),'purple').save(data,'PNG')
    return SimpleUploadedFile(name,data.getvalue(),content_type='image/png')

class PhaseThreeTests(TestCase):
    def setUp(self):
        test_phase2.PhaseTwoTests.setUp(self)
        self.admin=Member.objects.create_superuser(username='admin',email='admin@example.invalid',password='test-password-42')
        self.media=tempfile.TemporaryDirectory()
        self.override=override_settings(MEDIA_ROOT=self.media.name);self.override.enable()
        self.addCleanup(self.media.cleanup);self.addCleanup(self.override.disable)

    def test_uploaded_performance_image_and_coordinates_reach_public_pages(self):
        self.client.force_login(self.staff)
        response=self.client.patch(f'/api/staff/performances/{self.show.pk}/',json.dumps({'latitude':'37.520000','longitude':'127.120000'}),content_type='application/json')
        self.assertEqual(response.status_code,200)
        response=self.client.post('/api/staff/performances/',{'performance_name':'미디어 공연','genre':'CONCERT','venue_name':'장소','address':'서울 송파구','base_price':1000,'total_seats':2,'image':upload(),'performance_status':'PUBLISHED'})
        self.assertEqual(response.status_code,201,response.content)
        row=Performance.objects.get(pk=response.json()['data']['performance_id'])
        self.assertContains(self.client.get(f'/performance/{row.pk}/'),row.image.url)
        self.assertContains(self.client.get('/performances/'),row.image.url)
        venue=self.client.get(f'/performance/{self.show.pk}/venue/').json()
        self.assertEqual(venue['latitude'],37.52)
        self.assertEqual(venue['address'],'서울')
        self.assertNotIn('key',venue)

    def test_image_and_coordinate_validation(self):
        self.client.force_login(self.staff)
        response=self.client.patch(f'/api/staff/performances/{self.show.pk}/',json.dumps({'latitude':91,'longitude':0}),content_type='application/json')
        self.assertEqual(response.status_code,400)
        response=self.client.post('/api/staff/performances/',{'performance_name':'bad','genre':'CONCERT','venue_name':'v','address':'a','base_price':1,'total_seats':1,'image':SimpleUploadedFile('bad.png',b'not an image',content_type='image/png')})
        self.assertEqual(response.status_code,400)

    def test_every_schedule_date_is_searchable_and_paginated(self):
        PerformanceSchedule.objects.create(performance=self.show,performance_date='2027-01-02',start_time='19:00',end_time='21:00',sale_start_at=timezone.now(),sale_end_at=timezone.now()+timedelta(days=20))
        self.assertContains(self.client.get('/performances/?date=2027-01-02'),self.show.performance_name)
        for i in range(14):Performance.objects.create(performance_name=f'페이지 공연 {i}',genre='CONCERT',venue_name='v',address='서울',base_price=1,total_seats=1,performance_status='PUBLISHED')
        response=self.client.get('/performances/?page=2&region=서울')
        self.assertEqual(response.context['shows'].number,2)
        self.assertEqual(len(response.context['shows']),3)
        self.assertContains(response,'region=%EC%84%9C%EC%9A%B8')

    def test_event_content_image_and_admin_permissions(self):
        self.client.force_login(self.staff)
        self.assertEqual(self.client.get('/dashboard/events/').status_code,403)
        self.client.force_login(self.admin)
        response=self.client.post('/dashboard/events/',{'event_name':'별도 이벤트','performance':self.show.pk,'event_type':'팬 이벤트','content':'공연 설명과 다른 실제 내용','image':upload(),'event_start':'2026-10-01T10:00','event_end':'2026-12-01T10:00','event_status':'ACTIVE'})
        self.assertEqual(response.status_code,302)
        event=Event.objects.get(event_name='별도 이벤트')
        page=self.client.get('/events/detail/',{'id':event.pk})
        self.assertContains(page,event.content);self.assertContains(page,event.image.url)
        for i in range(8):Event.objects.create(performance=self.show,event_name=f'event{i}',event_type='팬 이벤트',event_start=timezone.now(),event_end=timezone.now()+timedelta(days=1))
        page=self.client.get('/events/?category=팬 이벤트&page=2')
        self.assertEqual(page.context['events'].number,2)
        self.assertEqual(len(page.context['events']),3)

    def test_notice_image_crud_same_database(self):
        self.client.force_login(self.staff)
        response=self.client.post('/api/staff/notices/',{'title':'사진 공지','content':'내용','notice_type':'NOTICE','is_published':'true','image':upload()})
        self.assertEqual(response.status_code,201,response.content)
        notice=Notice.objects.get(pk=response.json()['data']['notice_id'])
        self.assertContains(self.client.get(f'/notices/{notice.pk}/'),notice.image.url)

    def test_nft_persists_selected_ticket_and_owner_only_display(self):
        self.client.force_login(self.staff)
        response=self.client.post('/staff/nft/',{'collectible_name':'티켓 연결 NFT','performance':self.show.pk,'member':self.user.pk,'source_reservation':self.reservation.pk,'ticket':self.ticket.pk,'collectible_status':'ISSUED','metadata_url':'https://example.invalid/metadata.json','image':upload()})
        self.assertEqual(response.status_code,302)
        nft=DigitalCollectible.objects.get(collectible_name='티켓 연결 NFT')
        self.assertEqual(nft.source_ticket_id,self.ticket.pk)
        self.client.force_login(self.other)
        self.assertNotContains(self.client.get(response.url),self.ticket.ticket_code)
        self.client.force_login(self.user)
        self.assertContains(self.client.get(response.url),self.ticket.ticket_code)

    def test_db_seat_status_and_server_price_validation(self):
        Seat.objects.create(schedule=self.schedule,seat_number='A2',seat_grade='VIP',seat_price=120000,seat_status='BLOCKED')
        context=resolve_booking(str(self.show.pk));key=str(self.schedule.pk)
        seats=context['schedule_seats'][key]
        self.assertEqual(len(seats),2)
        self.assertEqual(sorted(s['price'] for s in seats.values()),[100000,120000])
        self.client.get('/booking/checkout/',{'performance':self.show.pk})
        data=dict(performance_id=str(self.show.pk),date=key,grade='VIP',seats=json.dumps([str(self.ticket.reservation_seat.seat_id)]),discount='none',method='간편결제',approval_code='DEMO',terms_finance='on',terms_privacy='on',terms_provider='on',attempt=self.client.session['payment_attempt'])
        self.assertEqual(self.client.post('/booking/mock-pay/',data).url,'/booking/complete/')
        self.assertEqual(self.client.session['payment_receipt']['subtotal'],100000)
        data['seats']=json.dumps([str(self.schedule.seats.get(seat_number='A2').pk)])
        self.assertFalse(MockPaymentForm(data,booking_context=context).is_valid())
        data['seats']='["2-5"]'
        self.assertFalse(MockPaymentForm(data,booking_context=context).is_valid())
        self.show.performance_name='변경된 이름';self.show.save()
        self.assertContains(self.client.get('/booking/complete/'),'공연 A')
        self.assertEqual(self.ticket.reservation_seat.seat.seat_status,'AVAILABLE')

    def test_ticket_ownership_and_invalid_qr(self):
        self.client.force_login(self.other)
        self.assertEqual(self.client.get(f'/api/tickets/{self.ticket.ticket_code}/').status_code,404)
        self.assertEqual(self.client.post(f'/api/reservations/{self.reservation.pk}/cancel/').status_code,404)
        self.client.force_login(self.staff)
        self.assertEqual(self.client.post('/api/staff/tickets/verify/',{'qr_token':'not-a-valid-ticket'}).status_code,404)

    def test_profile_and_ticket_page_use_member_data(self):
        self.client.force_login(self.user)
        response=self.client.post('/mypage/',{'first_name':'검증 회원','phone_number':'010-0000-0000','birth_date':'2000-01-02','gender':'F'})
        self.assertEqual(response.status_code,302)
        self.user.refresh_from_db();self.assertEqual(self.user.first_name,'검증 회원')
        self.assertContains(self.client.get('/tickets/'),self.ticket.ticket_code)
        self.client.force_login(self.other)
        self.assertNotContains(self.client.get('/tickets/'),self.ticket.ticket_code)

    def test_owned_and_favorite_nft_pages_grow_with_database(self):
        from events.models import CollectibleFavorite
        rows=DigitalCollectible.objects.bulk_create([DigitalCollectible(member=self.user,performance=self.show,collectible_name=f'기념 NFT {i}',collectible_code=f'PAGE-NFT-{i}',collectible_status='ISSUED') for i in range(25)])
        CollectibleFavorite.objects.bulk_create([CollectibleFavorite(member=self.user,collectible=row) for row in rows])
        self.client.force_login(self.user)
        for url,key in [('/nft/?tab=owned&page=2','items'),('/nft/?tab=favorites&page=2','items'),('/mypage/nft/?page=2','collectibles')]:
            response=self.client.get(url)
            self.assertEqual(response.context[key].number,2)
            self.assertEqual(len(response.context[key]),12)
            self.assertContains(response,'aria-current="page"')
