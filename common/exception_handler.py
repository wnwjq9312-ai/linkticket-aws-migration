"""
DRF 커스텀 예외 핸들러: LinkTicketError를 13.1절 표준 에러 포맷으로 변환한다.
settings.py에 등록:

    REST_FRAMEWORK = {
        "EXCEPTION_HANDLER": "common.exception_handler.linkticket_exception_handler",
    }
"""
from rest_framework.views import exception_handler as drf_exception_handler

from .exceptions import LinkTicketError
from .response import error_response


def linkticket_exception_handler(exc, context):
    if isinstance(exc, LinkTicketError):
        return error_response(exc.error_code, exc.message, exc.status_code)
    return drf_exception_handler(exc, context)
