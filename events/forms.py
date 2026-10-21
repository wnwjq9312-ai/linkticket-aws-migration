from uuid import uuid4
from pathlib import Path
from django import forms
from django.conf import settings
from common.storage import nft_storage
from accounts.models import Member
from reservations.models import Reservation
from tickets.models import Ticket
from .models import DigitalCollectible

class CollectibleRegistrationForm(forms.ModelForm):
    metadata_url = forms.URLField(label="메타데이터 URL (선택)",required=False,max_length=255)
    image = forms.ImageField(label='NFT 이미지', required=False, help_text='PNG, JPEG, WebP / 최대 5MB')
    ticket = forms.ModelChoiceField(label='연결 티켓 (선택)', queryset=Ticket.objects.select_related('reservation_seat__reservation'), required=False)
    class Meta:
        model = DigitalCollectible
        fields = ['collectible_name','performance','member','source_reservation','collectible_status','metadata_url']
        labels = {'collectible_name':'NFT 제목','performance':'연결 공연','member':'대상 회원 / 소유자','source_reservation':'연결 예매','collectible_status':'발급 상태','metadata_url':'메타데이터 URL (선택)'}
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['source_reservation'].queryset = Reservation.objects.select_related('member','schedule__performance')
        self.fields['source_reservation'].label_from_instance = lambda row: f'{row.reservation_code} · {row.member.username} · {row.schedule.performance.performance_name}'
        self.fields['ticket'].label_from_instance = lambda row: f'{row.ticket_code} · {row.get_ticket_status_display()}'
        self.fields['member'].label_from_instance = lambda row: f'{row.get_full_name() or row.username} ({row.username})'

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image and not settings.NFT_UPLOADS_ENABLED:
            raise forms.ValidationError('NFT 신규 이미지 업로드는 현재 준비 중입니다.')
        if image and (image.size > 5*1024*1024 or image.image.format not in ['PNG','JPEG','WEBP']):
            raise forms.ValidationError('5MB 이하의 PNG, JPEG, WebP 이미지를 선택해주세요.')
        return image
    def clean(self):
        data = super().clean()
        reservation = data.get('source_reservation')
        ticket = data.get('ticket')
        if ticket:
            linked = ticket.reservation_seat.reservation
            if reservation and reservation != linked:
                self.add_error('ticket','티켓과 예매가 일치하지 않습니다.')
            reservation = linked
            data['source_reservation'] = linked
        if reservation and (reservation.member != data.get('member') or reservation.schedule.performance != data.get('performance')):
            self.add_error('source_reservation','소유자·공연이 연결 예매와 일치해야 합니다.')
        return data
    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.source_ticket = self.cleaned_data.get('ticket')
        instance.collectible_code = 'NFT-' + uuid4().hex.upper()
        image = self.cleaned_data.get('image')
        if image:
            suffix = {'PNG':'.png','JPEG':'.jpg','WEBP':'.webp'}[image.image.format]
            instance.image_path = nft_storage().save('nft/'+uuid4().hex+suffix, image)
        if commit:
            instance.save()
        return instance
