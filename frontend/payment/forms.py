import re
from django import forms
from .mock_data import DATES, PRICING, CARDS, SEATS
from .mock_services import METHODS, INSTALLMENTS

class MockPaymentForm(forms.Form):
    date = forms.ChoiceField(choices=[(d['id'], d['id']) for d in DATES])
    grade = forms.ChoiceField(choices=[(g, g) for g in PRICING])
    seats = forms.JSONField()
    discount = forms.ChoiceField(choices=[(x, x) for x in ('none', 'youth', 'coupon')])
    method = forms.ChoiceField(choices=[(m, m) for m in METHODS], error_messages={'required': '寃곗젣?섎떒???좏깮?댁＜?몄슂.'})
    card = forms.ChoiceField(required=False, choices=[(c, c) for c in CARDS])
    installment = forms.ChoiceField(required=False, choices=[(i, i) for i in INSTALLMENTS])
    approval_code = forms.CharField(max_length=20, error_messages={'required': '?뚯뒪???뱀씤 肄붾뱶 DEMO瑜??낅젰?댁＜?몄슂.'})
    terms_finance = forms.BooleanField(required=True)
    terms_privacy = forms.BooleanField(required=True)
    terms_provider = forms.BooleanField(required=True)
    attempt = forms.CharField(max_length=64)

    def clean_seats(self):
        seats = self.cleaned_data['seats']
        if not isinstance(seats, list) or not 1 <= len(seats) <= 4:
            raise forms.ValidationError('醫뚯꽍??1~4留??좏깮?댁＜?몄슂.')
        if any(not isinstance(s, str) or not re.fullmatch(r'[1-9][0-9]?-[1-9][0-9]?', s) for s in seats):
            raise forms.ValidationError('?щ컮瑜?醫뚯꽍???좏깮?댁＜?몄슂.')
        if len(set(seats)) != len(seats):
            raise forms.ValidationError('以묐났 醫뚯꽍? ?좏깮?????놁뒿?덈떎.')
        for seat in seats:
            if seat not in SEATS or SEATS[seat]['status'] != 'available':
                raise forms.ValidationError('?좏깮?????녿뒗 醫뚯꽍?낅땲??')
        return seats

    def clean_approval_code(self):
        value = self.cleaned_data['approval_code']
        if value != 'DEMO':
            raise forms.ValidationError('?뚯뒪???뱀씤 肄붾뱶??DEMO?낅땲??')
        return value

    def clean(self):
        data = super().clean()
        if data.get('grade') and data.get('seats'):
            if any(SEATS[seat]['grade'] != data['grade'] for seat in data['seats']):
                self.add_error('seats', '?좏깮???깃툒???랁븯??醫뚯꽍留??덈ℓ?????덉뒿?덈떎.')
        if data.get('method') == '?좎슜移대뱶':
            if not data.get('card'):
                self.add_error('card', '移대뱶?щ? ?좏깮?댁＜?몄슂.')
            if not data.get('installment'):
                self.add_error('installment', '?좊? 媛쒖썡???좏깮?댁＜?몄슂.')
        return data

