"""Service identity mapped to the existing member table, never auth_user."""
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.hashers import check_password
from django.db import models
from django.utils import timezone


class MemberRole(models.TextChoices):
    MEMBER = 'USER', '회원'
    STAFF = 'STAFF', '직원'
    ADMIN = 'ADMIN', '관리자'


class MemberManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra):
        if not username or not email:
            raise ValueError('아이디와 이메일은 필수입니다.')
        staff = extra.pop('is_staff', False)
        superuser = extra.pop('is_superuser', False)
        active = extra.pop('is_active', True)
        extra.setdefault('role', MemberRole.ADMIN if superuser else MemberRole.STAFF if staff else MemberRole.MEMBER)
        extra.setdefault('member_status', 'ACTIVE' if active else 'SUSPENDED')
        user = self.model(username=username, email=self.normalize_email(email), **extra)
        user.set_password(password)
        user.full_clean()
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra):
        # Explicit provisioning API only; never invoked to repair existing accounts.
        extra.update(is_staff=True, is_superuser=True)
        return self.create_user(username, email, password, **extra)


class Member(AbstractBaseUser):
    id = models.AutoField(primary_key=True, db_column='member_id')
    username = models.CharField(max_length=50, unique=True, db_column='login_id')
    first_name = models.CharField(max_length=50, db_column='name', blank=True)
    phone_number = models.CharField(max_length=20, db_column='phone', null=True, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=[('M', '남'), ('F', '여')], null=True, blank=True)
    email = models.EmailField(max_length=100, unique=True)
    password = models.CharField(max_length=255)
    role = models.CharField(max_length=20, choices=MemberRole.choices, default=MemberRole.MEMBER)
    date_joined = models.DateTimeField(db_column='joined_at', default=timezone.now)
    member_status = models.CharField(max_length=20, default='ACTIVE')
    # Existing member has no last_login column. Django must not write one on login.
    last_login = None
    objects = MemberManager()
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    class Meta:
        db_table = 'member'

    @property
    def member_id(self):
        return self.pk

    @property
    def is_active(self):
        return self.member_status == 'ACTIVE'

    @property
    def is_staff(self):
        return self.is_active and self.role in (MemberRole.STAFF, MemberRole.ADMIN)

    @property
    def is_superuser(self):
        return self.is_active and self.role == MemberRole.ADMIN

    def get_full_name(self):
        return self.first_name

    def get_short_name(self):
        return self.first_name or self.username

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    def has_perm(self, perm, obj=None):
        # Django admin/auth_user permission recovery is explicitly out of scope.
        return False

    def has_module_perms(self, app_label):
        return False
