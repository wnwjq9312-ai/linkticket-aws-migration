from django.db import models


class PerformanceGenreField(models.CharField):
    """Existing MariaDB stores Korean genre labels; Python/API keeps stable codes."""
    labels = dict(CONCERT='콘서트', MUSICAL='뮤지컬', FESTIVAL='페스티벌', PLAY='연극',
                  CLASSICAL='클래식', FANMEETING='팬미팅', EXHIBITION_ETC='전시/기타')

    def from_db_value(self, value, expression, connection):
        return next((code for code, label in self.labels.items() if value == label), value)

    def get_prep_value(self, value):
        value = super().get_prep_value(value)
        return self.labels.get(value, value)
