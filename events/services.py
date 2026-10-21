from django.db import transaction
from .models import Event, EventReward, EventRewardType


def is_reservation_eligible(event, reservation):
    return reservation.schedule.performance_id == event.performance_id and reservation.reservation_status == 'CONFIRMED'


@transaction.atomic
def record_event_reward(member, event, reward_type, reward_value):
    # Production has no composite UNIQUE: serialize using the existing parent PK.
    Event.objects.select_for_update().only('event_id').get(pk=event.pk)
    existing = EventReward.objects.filter(event=event, member=member, reward_type=reward_type).order_by('pk').first()
    if existing:
        return existing, False
    return EventReward.objects.create(event=event, member=member, reward_type=reward_type, reward_value=reward_value), True


def grant_event_reward(member, event, reservation=None):
    # A participation record is not an external point transfer or blockchain mint.
    return record_event_reward(member, event, EventRewardType.DONATION_POINT, '0')[0]
