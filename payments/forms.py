from django import forms
from .mock_data import DATES, PRICING, CARDS, SEATS
from .mock_services import METHODS, INSTALLMENTS

class MockPaymentForm(forms.Form):
    date = forms.ChoiceField(choices=[(d['id'], d['id']) for d in DATES])
    grade = forms.ChoiceField(choices=[(g, g) for g in PRICING])
    seats = forms.JSONField()
    discount = forms.ChoiceField(choices=[(x, x) for x in ('none', 'youth', 'coupon')])
    method = forms.ChoiceField(choices=[(m, m) for m in METHODS], error_messages={'required': '결제수단을 선택해주세요.'})
    card = forms.ChoiceField(required=False, choices=[(c, c) for c in CARDS])
    installment = forms.ChoiceField(required=False, choices=[(i, i) for i in INSTALLMENTS])
    approval_code = forms.CharField(max_length=20, error_messages={'required': '테스트 승인 코드 DEMO를 입력해주세요.'})
    terms_finance = forms.BooleanField(required=True)
    terms_privacy = forms.BooleanField(required=True)
    terms_provider = forms.BooleanField(required=True)
    attempt = forms.CharField(max_length=64)

    def __init__(self, *args, booking_context=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.booking_context = booking_context or {}
        self.seat_data = SEATS
        if booking_context:
            self.fields['grade'].choices = [(g,g) for g in booking_context['prices']]
            schedules = booking_context.get('schedule_seats',{})
            if schedules:
                self.seat_data = schedules.get(str(self.data.get('date','')), {})
            self.fields['date'].choices = [(d['id'], d['day']) for d in booking_context['dates']]

    def clean_seats(self):
        seats = self.cleaned_data['seats']
        if not isinstance(seats, list) or not 1 <= len(seats) <= 4:
            raise forms.ValidationError('좌석을 1~4개 선택해주세요.')
        if any(not isinstance(s, str) or s not in self.seat_data for s in seats):
            raise forms.ValidationError('올바른 좌석을 선택해주세요.')
        if len(set(seats)) != len(seats):
            raise forms.ValidationError('중복 좌석은 선택할 수 없습니다.')
        for seat in seats:
            if seat not in self.seat_data or self.seat_data[seat]['status'] != 'available':
                raise forms.ValidationError('선택할 수 없는 좌석입니다.')
        return seats

    def clean_approval_code(self):
        value = self.cleaned_data['approval_code']
        if value != 'DEMO':
            raise forms.ValidationError('테스트 승인 코드는 DEMO입니다.')
        return value

    def clean(self):
        data = super().clean()
        if data.get('grade') and data.get('seats'):
            if any(self.seat_data[seat]['grade'] != data['grade'] for seat in data['seats']):
                self.add_error('seats', '선택한 등급의 좌석만 예매할 수 있습니다.')
        if data.get('method') == '신용카드':
            if not data.get('card'):
                self.add_error('card', '카드사를 선택해주세요.')
            if not data.get('installment'):
                self.add_error('installment', '할부 개월을 선택해주세요.')
        return data

