from rest_framework import serializers

from .models import DigitalCollectible, Event, EventReward


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ["event_id", "performance", "event_name", "event_type", "event_start", "event_end", "event_status", "content", "image"]


class EventRewardSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventReward
        fields = ["reward_id", "event", "member", "reward_type", "reward_value", "issued_at"]


class DigitalCollectibleSerializer(serializers.ModelSerializer):
    class Meta:
        model = DigitalCollectible
        fields = ["collectible_id", "collectible_name", "collectible_code", "image_path", "collectible_status", "issued_at"]
