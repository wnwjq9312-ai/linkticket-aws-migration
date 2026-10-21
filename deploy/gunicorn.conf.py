import os

bind = os.environ['GUNICORN_BIND']
if bind not in ('10.10.2.2:8000', '10.10.2.4:8080'):
    raise RuntimeError('Unexpected WAS bind address')
workers = int(os.environ.get('GUNICORN_WORKERS', '3'))
timeout = 60
accesslog = '-'
errorlog = '-'
capture_output = True
forwarded_allow_ips = '10.10.4.101,10.10.4.102'
