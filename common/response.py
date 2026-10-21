"""
표준 API 응답 포맷
참조: 개발 기능 명세서 v2.0 13.1절

모든 뷰는 Response를 직접 만들지 말고 이 두 헬퍼를 통해서만 응답한다.
"""
from rest_framework.response import Response


def success_response(data=None, status=200):
    return Response({"success": True, "data": data if data is not None else {}}, status=status)


def error_response(error_code: str, message: str, status: int):
    return Response({"success": False, "error_code": error_code, "message": message}, status=status)
