from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'password', 'first_name', 'email', 'phone_number', 'birth_date', 'gender', 'marketing_agree']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            first_name=validated_data.get('first_name', ''),
            phone_number=validated_data.get('phone_number', ''),
            birth_date=validated_data.get('birth_date', None),
            gender=validated_data.get('gender', ''),
            marketing_agree=validated_data.get('marketing_agree', False) 
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("이미 사용 중인 이메일입니다.")
        return value

    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("비밀번호는 8자 이상이어야 합니다.")
        return value