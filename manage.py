#!/usr/bin/env python
"""로컬 개발/화면 확인용 Django 관리 스크립트."""
import os
import sys


def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Django를 불러오지 못했습니다. 가상환경을 활성화하고 "
            "`pip install -r requirements.txt`를 먼저 실행했는지 확인하세요."
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
