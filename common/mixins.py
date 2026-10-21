"""
참조: 개발 기능 명세서 v2.0 13.1절(표준 응답 포맷)

버그 수정 배경: `common/response.py`의 success_response/error_response로 직접 Response를
만드는 커스텀 APIView들은 처음부터 `{"success": true, "data": ...}` 봉투를 지켰지만,
DRF의 `generics.ListAPIView`/`CreateAPIView`/`RetrieveAPIView`/`UpdateAPIView`/
`ListCreateAPIView`를 그대로 상속한 뷰들은 `list()`/`create()`/`retrieve()`/`update()`가
내부적으로 `Response(serializer.data)`를 직접 만들어 반환하기 때문에 이 봉투를 타지
않고 raw `serializer.data`가 그대로 나갔다(예: 공연 등록 API가
`{"performance_id": 1, ...}`를 그대로 반환 — `{"success": true, "data": {...}}`가 아님).
프론트엔드의 `frontend/shared/api.js`는 모든 응답이 이 봉투를 따른다고 가정하고
`res.data`를 언랩하므로, 방치하면 이 API들만 화면에서 조용히 깨진다.

해결: 각 뷰의 로직(쿼리셋/시리얼라이저/권한)은 전혀 건드리지 않고, 상속 목록 맨 앞에
이 믹스인만 추가한다. `finalize_response`는 DRF가 뷰 메서드가 반환한 Response를 실제로
렌더링하기 직전에 항상 거치는 지점이라, 여기서 2xx 응답의 `.data`만 한 번 더 감싸면
기존 커스텀 APIView들이 쓰는 success_response와 완전히 동일한 모양이 된다.
"""
from rest_framework.response import Response


class EnvelopeMixin:
    """DRF generics.*APIView 응답을 프로젝트 표준 봉투로 감싼다.

    사용법: 반드시 generics.*APIView보다 앞에 와야 한다(MRO상 이 클래스의
    finalize_response가 먼저 호출되고, 그 안에서 super()로 DRF 본래 동작을 이어간다).
        class FooListView(EnvelopeMixin, generics.ListAPIView): ...
    """

    def finalize_response(self, request, response, *args, **kwargs):
        if isinstance(response, Response) and 200 <= response.status_code < 300:
            response.data = {"success": True, "data": response.data}
        return super().finalize_response(request, response, *args, **kwargs)
