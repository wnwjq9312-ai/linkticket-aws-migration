import io
import tempfile
from uuid import uuid4
from PIL import Image
from django.test import TestCase, override_settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import connection
from django.utils import timezone
from accounts.models import Member
from catalog.models import Performance
from .models import Event, NftItem, EventReward
from .nft_forms import NftRegistrationForm
from .services import record_event_reward


class ScopedUploadTests(TestCase):
    def setUp(self):
        self.owner = Member.objects.create(username='owner', email='owner@example.test')
        self.other = Member.objects.create(username='other', email='other@example.test')
        self.show = Performance.objects.create(performance_name='scope', venue_name='test', address='test', base_price=1, total_seats=1, genre='CONCERT')

    def image(self):
        stream = io.BytesIO()
        Image.new('RGB', (2, 2), 'blue').save(stream, 'PNG')
        return SimpleUploadedFile('test.png', stream.getvalue(), content_type='image/png')

    def test_genre_existing_db_mapping(self):
        with connection.cursor() as cursor:
            cursor.execute('SELECT genre FROM performance WHERE performance_id=%s', [self.show.pk])
            self.assertEqual(cursor.fetchone()[0], '콘서트')
        self.show.refresh_from_db()
        self.assertEqual(self.show.genre, 'CONCERT')

    def test_nft_repeat_owner_and_image(self):
        with tempfile.TemporaryDirectory() as root, override_settings(NFT_UPLOADS_ENABLED=True, NFT_MEDIA_ROOT=root, NFT_MEDIA_URL='/nft_images/', NFT_NFS_MOUNT=None):
            data = dict(nft_name='Scoped NFT', artist_name='test', member=self.owner.pk, performance=self.show.pk, nft_status='ISSUED', submission=str(uuid4()))
            ids = []
            for _ in range(2):
                form = NftRegistrationForm(data, {'image': self.image()})
                self.assertTrue(form.is_valid(), form.errors)
                ids.append(form.save().pk)
            self.assertEqual(ids[0], ids[1])
            self.assertEqual(NftItem.objects.count(), 1)
            item = NftItem.objects.get()
            self.client.force_login(self.owner)
            self.assertEqual(self.client.get('/nft/%s/' % item.pk).status_code, 200)
            response = self.client.get(item.image_path)
            self.assertEqual(response.status_code, 200)
            response.close()
            self.assertContains(self.client.get('/mypage/nft/'), 'Scoped NFT')
            self.client.force_login(self.other)
            self.assertEqual(self.client.get(item.image_path).status_code, 404)
            self.assertEqual(self.client.get('/nft/%s/' % item.pk).status_code, 404)
            self.assertNotContains(self.client.get('/mypage/nft/'), 'Scoped NFT')

    def test_reward_repeat_and_privacy(self):
        event = Event.objects.create(performance=self.show, event_name='Scoped reward', event_type='test', event_start=timezone.now(), event_end=timezone.now())
        first, created = record_event_reward(self.owner, event, 'TICKET_SUPPORT', 'test reward')
        second, repeated = record_event_reward(self.owner, event, 'TICKET_SUPPORT', 'must not overwrite')
        self.assertTrue(created)
        self.assertFalse(repeated)
        self.assertEqual(first.pk, second.pk)
        self.assertEqual(EventReward.objects.get().reward_value, 'test reward')
        self.client.force_login(self.owner)
        self.assertContains(self.client.get('/mypage/rewards/'), 'test reward')
        self.client.force_login(self.other)
        self.assertNotContains(self.client.get('/mypage/rewards/'), 'test reward')
