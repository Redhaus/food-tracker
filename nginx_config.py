server {
    # listen on root and anything that comes in
    location / {
        # redirect on local machine to localhost
       proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}