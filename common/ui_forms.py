from django import forms
from django.utils import timezone
from accounts.models import Member
from events.models import Event

class ProfileForm(forms.ModelForm):
    def clean_birth_date(self):
        value = self.cleaned_data.get('birth_date')
        if value and value > timezone.localdate():
            raise forms.ValidationError('생년월일은 오늘 이후일 수 없습니다.')
        return value

    class Meta:
        model = Member
        fields = ['first_name', 'phone_number', 'birth_date', 'gender']
        labels = {'first_name':'이름', 'phone_number':'휴대폰', 'birth_date':'생년월일', 'gender':'성별'}
        widgets = {'birth_date':forms.DateInput(attrs={'type':'date'})}

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['event_name','performance','event_type','content','image','event_start','event_end','event_status']
        labels = {'event_name':'이벤트 제목','performance':'연결 공연','event_type':'카테고리','content':'내용','image':'대표 이미지','event_start':'시작','event_end':'종료','event_status':'상태'}
        widgets = {name:forms.DateTimeInput(attrs={'type':'datetime-local'},format='%Y-%m-%dT%H:%M') for name in ['event_start','event_end']}
    def clean(self):
        data=super().clean()
        if data.get('event_start') and data.get('event_end') and data['event_end'] <= data['event_start']:
            self.add_error('event_end','종료는 시작 이후여야 합니다.')
        return data
