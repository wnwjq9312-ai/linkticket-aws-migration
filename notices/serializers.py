from rest_framework import serializers

from .models import Notice


class NoticeTypeField(serializers.ChoiceField):
    """Keep the frontend API codes while respecting the existing DB constraint."""
    codes = {'NOTICE':'공지', 'EVENT':'이벤트', 'GUIDE':'안내', 'MAINTENANCE':'점검'}

    def __init__(self, **kwargs):
        super().__init__(choices=list(self.codes.items()), **kwargs)

    def to_internal_value(self, data):
        if data in self.codes.values():
            return data
        return self.codes[super().to_internal_value(data)]

    def to_representation(self, value):
        return next((code for code, label in self.codes.items() if label == value), value)


class NoticeSerializer(serializers.ModelSerializer):
    notice_type = NoticeTypeField(required=False)

    class Meta:
        model = Notice
        fields = ["notice_id", "notice_type", "title", "content", "is_published", "published_at", "view_count", "created_at", "image"]
        read_only_fields = ["notice_id", "view_count", "created_at"]
