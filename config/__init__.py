# mysqlclient(C 확장, 컴파일 필요) 대신 순수 파이썬 드라이버인 PyMySQL을 쓸 때의 표준 shim.
# 팀원 전원의 OS/빌드 환경이 다를 수 있어(Windows/mac/Linux 혼재) mysqlclient보다
# 설치 실패 가능성이 훨씬 낮다. PyMySQL이 설치되어 있지 않아도(=SQLite만 쓰는 상황)
# 서버가 죽지 않도록 방어한다.
try:
    import pymysql

    pymysql.install_as_MySQLdb()
except ImportError:
    pass
