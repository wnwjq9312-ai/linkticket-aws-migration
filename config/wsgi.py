"""
운영에서는 Gunicorn이 이 module:callable(`config.wsgi:application`)을 기동한다.
로컬 화면 확인은 `python manage.py runserver`만으로 충분하며 이 파일은 쓰지 않는다.
"""
import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

application = get_wsgi_application()
