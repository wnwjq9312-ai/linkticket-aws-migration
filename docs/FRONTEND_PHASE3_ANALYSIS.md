# UI3 통합 분석 및 변경 계획

기준: main 6e6f247, 기존 통합 8f5580a. 기존 frontend 원본과 2차 통합은 보존한다.

## 구조와 데이터 경계
accounts(회원/세션), catalog(공연/회차/좌석), reservations(예매/Redis 선점), payments(Mock 및 기존 DB 결제 서비스), tickets(해시 QR 검표), coupons, events(이벤트/NFT), notices, dashboard, common(UI 어댑터) 구조다. templates/base.html과 includes, static/linkticket 및 payments의 지도/좌석 구현을 재사용한다. 실제 PG, Redis 설치, 인프라 배포는 이번 변경에 포함하지 않는다.

## 시안 → 화면 매핑
|UI3 번호|Template / URL|데이터|
|---|---|---|
|01|operations/staff.html /staff/#notices|Notice, 기존 CRUD API|
|02|ui/detail.html /performance/{id}/|Performance, PerformanceSchedule (파일명은 이벤트상세지만 내용은 공연 상세)|
|03|ui/auth.html /register/|Member, RegisterSerializer|
|04|operations/staff.html /staff/|Performance/Schedule/Seat|
|05,07,11|payment/*.html /booking/, /booking/checkout/, /booking/complete/|기존 Mock 폼/영수증 + 공연·회차 데이터|
|06|ui/nft_detail.html /nft/{id}/|DigitalCollectible, Reservation, Ticket|
|08|ui/performances.html /performances/|공개 공연, 필터, Paginator|
|09,13|ui/notice_detail.html, notices.html /notices/|Notice 동일 DB|
|10|ui/auth.html /login/|기존 세션 로그인, OAuth 미설정 표시|
|12|ui/home.html /|공연/공지|
|14|ui/mypage.html /mypage/reservations/|현재 회원 예매/티켓, 별도 Mock 이력|
|15|operations/admin.html /dashboard/|기존 통계 및 관리 API|
|16,19|ui/nfts.html, mypage.html /nft/, /mypage/nft/|NFT 및 회원별 찜|
|17|operations/nft_form.html /staff/nft/|기존 NFT 등록 폼|
|18|ui/events.html /events/|Event|

## 확인한 차이 및 최소 변경
- Performance에 이미지/좌표, Event에 자체 내용/이미지, Notice에 이미지가 없어 선택적 필드를 추가한다. 기존 레코드는 빈 값 유지, 삭제/초기화 없음.
- NFT 티켓 선택이 예매에만 저장되던 부분을 선택적 source_ticket FK로 보완한다.
- 공통 이미지 URL, 페이지네이션, 모든 날짜 입력의 달력, 기존 Kakao 모달의 공연별 설정을 재사용한다.
- 직원 공연/공지 업로드와 이벤트 관리 폼을 연결한다. 목록 API의 기존 배열 계약은 유지하고 관리 화면에 실제 행 페이지 분할을 적용한다.
- DB 공연 날짜 필터는 전체 회차 기준으로 수정한다. 등록된 DB 좌석이 있으면 해당 회차 좌석/가격/상태를 사용하되 Mock 결제는 실제 좌석을 확정하지 않는다.
- QR 미등록 토큰 500과 다른 회원 티켓 조회를 필요한 범위에서 수정한다.

## 작업 순서
선택적 필드/검증 → UI 데이터 연결/공통 컴포넌트 → UI3 레이아웃 → 기능 및 반응형 회귀 → 보고서/커밋. 기존 API 이름과 서비스 시그니처, 마이그레이션은 보존한다.
