
# LINKTICKET AWS WEB Configuration
# HTTPS is terminated by the AWS ALB.

upstream linkticket_was {
    server ${WAS_HOST}:8082;
    keepalive 16;
}

server {
    listen 80;
    server_name _;

    client_max_body_size 6m;

    location = /health {
        access_log off;
        default_type text/plain;
        return 200 "ok";
    }

    location /static/ {
        alias /var/www/linkticket/;
        autoindex off;
    }

    location /media/ {
        return 503;
    }

    location /nft-media/ {
        return 503;
    }

    location / {
        proxy_pass http://linkticket_was;

        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $http_x_forwarded_proto;

        proxy_connect_timeout 5s;
        proxy_read_timeout 60s;

        proxy_next_upstream error timeout;
    }
}
