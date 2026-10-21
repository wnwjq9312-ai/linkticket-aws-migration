from uuid import uuid4
from django import forms
from django.db import transaction
from accounts.models import Member
from common.storage import nft_storage
from .models import NftItem, Event, EventRewardType


class NftRegistrationForm(forms.ModelForm):
    submission = forms.UUIDField(initial=uuid4, widget=forms.HiddenInput)
    image = forms.ImageField(label='NFT 이미지')

    class Meta:
        model = NftItem
        fields = ['nft_name', 'artist_name', 'performance', 'member', 'nft_status', 'metadata_url']
        labels = {'nft_name': 'NFT 이름', 'artist_name': '아티스트', 'performance': '공연', 'member': '받을 회원', 'nft_status': '발급 상태', 'metadata_url': '메타데이터 URL (선택)'}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['member'].required = True
        self.fields['member'].queryset = Member.objects.filter(member_status='ACTIVE')

    def clean_image(self):
        image = self.cleaned_data['image']
        if image.size > 5 * 1024 * 1024 or image.image.format not in ('PNG', 'JPEG', 'WEBP'):
            raise forms.ValidationError('5MB 이하 PNG/JPEG/WebP 이미지를 사용해주세요.')
        return image

    def clean(self):
        data = super().clean()
        if data.get('submission'):
            existing = NftItem.objects.filter(token_id='UI-' + data['submission'].hex).first()
            if existing and any(getattr(existing, field) != data.get(field) for field in ('member', 'performance', 'nft_name', 'artist_name')):
                raise forms.ValidationError('이미 사용된 등록 번호입니다. 새 등록 화면을 열어주세요.')
        return data

    @transaction.atomic
    def save(self, commit=True):
        if not commit:
            raise ValueError('NFT issuance requires a committed transaction')
        Member.objects.select_for_update().get(pk=self.cleaned_data['member'].pk)
        token = 'UI-' + self.cleaned_data['submission'].hex
        existing = NftItem.objects.filter(token_id=token).first()
        if existing:
            return existing
        item = super().save(commit=False)
        image = self.cleaned_data['image']
        suffix = {'PNG': '.png', 'JPEG': '.jpg', 'WEBP': '.webp'}[image.image.format]
        name = nft_storage().save(uuid4().hex + suffix, image)
        item.image_path = '/nft_images/' + name
        item.token_id = token
        item.save()
        return item


class RewardGrantForm(forms.Form):
    event = forms.ModelChoiceField(Event.objects.all(), label='이벤트')
    member = forms.ModelChoiceField(Member.objects.filter(member_status='ACTIVE'), label='받을 회원')
    reward_type = forms.ChoiceField(choices=[(EventRewardType.DONATION_POINT, '기부 포인트 지급 기록'), (EventRewardType.TICKET_SUPPORT, '티켓 지원 기록')], label='보상 종류')
    reward_value = forms.CharField(max_length=255, label='보상 내용')
