from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    def to_internal_value(self, data):
        data = data.copy()
        if data.get('birth_date') == '':
            data['birth_date'] = None
        if data.get('gender') == '':
            data['gender'] = None
        return super().to_internal_value(data)

    class Meta:
        model = User
        fields = ['username', 'password', 'first_name', 'email', 'phone_number', 'birth_date', 'gender']

    def validate(self, data):
        for field in ('marketing_agree',):
            if self.initial_data.get(field) not in (None, '', False, 'false', 'False', '0'):
                raise serializers.ValidationError({field: '추가 회원정보 저장은 준비 중입니다.'})
        return data

    def validate_birth_date(self, value):
        if value and value > timezone.localdate():
            raise serializers.ValidationError('생년월일은 오늘 이후일 수 없습니다.')
        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            phone_number=validated_data.get('phone_number', ''),
            birth_date=validated_data.get('birth_date'),
            gender=validated_data.get('gender') or None,
        )
        return user

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("이미 사용 중인 이메일입니다.")
        return value

    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("비밀번호는 8자 이상이어야 합니다.")
        return value
