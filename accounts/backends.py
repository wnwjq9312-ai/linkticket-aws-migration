"""Service authentication without implicit upgrades of stored password hashes."""
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.hashers import check_password, make_password


class ExistingMemberBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        model = get_user_model()
        username = username if username is not None else kwargs.get(model.USERNAME_FIELD)
        if username is None or password is None:
            return None
        try:
            user = model._default_manager.get_by_natural_key(username)
        except model.DoesNotExist:
            make_password(password)
            return None
        # No setter: authentication must not rewrite an existing password hash.
        if check_password(password, user.password) and self.user_can_authenticate(user):
            return user
        return None

    def user_can_authenticate(self, user):
        return user.member_status == 'ACTIVE'

    def get_user(self, user_id):
        try:
            user = get_user_model().objects.get(pk=user_id)
        except get_user_model().DoesNotExist:
            return None
        return user if self.user_can_authenticate(user) else None
