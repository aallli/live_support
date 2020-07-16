# live_support

1- sudo apt-get update && sudo apt-get -y upgrade
2- sudo apt-get install python3 && sudo apt-get install python3-pip && sudo apt-get install libpq-dev
3- sudo pip3 install virtualenv
4- Create virtual environment: virtualenv venv
5- Clone source: git clone https://github.com/aallli/live_support.git
6- Activate virtualenv: source venv/bin/activate
7- pip install -r requirements.txt

NOTE: Set environment variable for database access: 

    export ALLOWED_HOSTS='[Server IP]'

8- Install postgresql:

    sudo apt-get install postgresql postgresql-contrib
    sudo usermod -aG sudo postgres

9- Switch over to the postgres account on your server by typing:
    
    sudo -i -u postgres

10- Create database named sadesa: sudo -u postgres createdb

    sudo -u postgres createdb live_support

11- Set postgres password: 
    
    sudo -u postgres psql postgres
    \password postgres
    \q
    exit 

12- Caution: Allow remote access to postgres:
    
    Add to /etc/postgresql/9.5/main/postgresql.conf : #listen_addresses = '*'
    Add to /etc/postgresql/9.5/main/pg_hba.conf : host all all 0.0.0.0/0 trust
    systemctl restart postgresql

NOTE: Set environment variable for database access: 

    export DATABASES_PASSWORD='[Database password]'

12- python manage.py migrate

14- Install redis:

    deactivate
    sudo apt-get install docker
    sudo docker run -p 6379:6379 -d redis:5 

NOTE: If docker fails due to sanction issues, try this:

    sudo apt-get update
    sudo apt-get install redis-server
 
15- To autostart redis, open configurations file:

    sudo nano /etc/redis/redis.conf

16- Find and replace this statement:

    supervised no

to:

    supervised systemd

17- Start and check redis:

    sudo systemctl restart redis.service
    sudo systemctl status redis.service

18- Test channel layer can communicate with Redis:

    source ../venv/bin/activate
    python manage.py shell
    >>> import channels.layers
    >>> channel_layer = channels.layers.get_channel_layer()
    >>> from asgiref.sync import async_to_sync
    >>> async_to_sync(channel_layer.send)('test_channel', {'type': 'hello'})
    >>> async_to_sync(channel_layer.receive)('test_channel')
    {'type': 'hello'}

19- test if gunicorn can serve application: gunicorn --bind 0.0.0.0:8888 live_support.wsgi
20- groupadd --system www-data
21- useradd --system --gid www-data --shell /bin/bash --home-dir /home/[user]/live_support/live_support live_support
22- usermod -aG sudo live_support
23- chown -R live_support:www-data /home/[user]/live_support/live_support
24- chmod -R g+w /home/[user]/live_support/live_support

Configure Gunicorn:
25- sudo nano /etc/systemd/system/gunicorn-live_support.service
26- add:
    
    [Unit]
    Description=gunicorn daemon
    After=network.target
    
    [Service]
    User=live_support
    Group=www-data
    WorkingDirectory=/home/[user]/live_support/live_support
    EnvironmentFile=/etc/gunicorn-live_support.env
    ExecStart=/home/[user]/live_support/venv/bin/gunicorn --access-logfile - --workers 3 --bind unix:/home/[user]/live_support/live_support/live_support.sock live_support.wsgi:application
    
    [Install]
    WantedBy=multi-user.target
        
27- sudo nano /etc/gunicorn-live_support.env
28- Add followings:
    
    DEBUG=0
    DEPLOY=1
    ALLOWED_HOSTS='[server ip]'
    CHANNEL_LAYERS_HOSTS='[redis server]',
    ADMIN_TEL='[admin tel]'
    ADMIN_EMAIL='[admin email]'
    DAPHNE_HOST='[Daphne host]',
    CORS_ORIGIN_WHITELIST='[CORS white list]'
    
29- sudo systemctl start gunicorn-live_support
30- sudo systemctl enable gunicorn-live_support
31- Check if 'live_support.sock' file exists: ls /home/[user]/live_support/live_support
32- sudo nano /etc/nginx/conf.d/proxy_params
33- Add followings:

    proxy_set_header Host $http_host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;

34- If gunicorn.service file is changed, run:

    sudo systemctl daemon-reload
    sudo systemctl restart gunicorn-live_support

35- Install gettext:

    apt-get update
    apt-get upgrade
    apt-get install
    apt-get install gettext

36- Compile messages for i18N:
    
    source ../venv/bin/activate
    django-admin compilemessages -f (if translation is needed)

37- Collect static files: (Create static and uploads directory if needed)
 
    python manage.py collectstatic
      
38- Install supervisor:

    sudo apt install supervisor
    
    
39- Configure supervisor:

    sudo nano /etc/supervisor/conf.d/live_support.conf

40- Add these code:

    [fcgi-program:asgi]
    environment =
        DEBUG=0,
        ALLOWED_HOSTS='[Allowed hosts]',
        CHANNEL_LAYERS_HOSTS='[Channel layer host]',
        DAPHNE_HOST='[Daphne host]',
        CORS_ORIGIN_WHITELIST='[CORS White list]'
    
    # TCP socket used by Nginx backend upstream
    socket=tcp://[Servre ip]:8080
    
    # Directory where your site's project files are located
    directory=/home/[user]/live_support/live_support
    
    # Each process needs to have a separate socket file, so we use process_num
    # Make sure to update "live_support.asgi" to match your project name
    command=/home/[user]/live_support/venv/bin/daphne -u /run/daphne/daphne%(process_num)d.sock --fd 0 --access-log - --proxy-headers live_support.asgi:application
    
    # Number of processes to startup, roughly the number of CPUs you have
    numprocs=4
    
    # Give each process a unique name so they can be told apart
    process_name=asgi%(process_num)d
    
    # Automatically start and recover processes
    autostart=true
    autorestart=true
    
    # Choose where you want your log to go
    stdout_logfile=/home/[user]/live_support/log/asgi.log
    redirect_stderr=true
    
41 - Create the run directory for the sockets referenced:

    sudo mkdir /run/daphne/
    
42- Change the owner settings of the run directory:

    sudo chown -R live_support:www-data /run/daphne/

43- Have supervisor reread and update its jobs:

    sudo supervisorctl reread
    sudo supervisorctl update


Configure Nginx:
44- create keys and keep them in /root/certs/live_support/:
    
    openssl req -new -newkey rsa:4096 -x509 -sha256 -days 365 -nodes -out /root/certs/live_support/live_support.crt -keyout /root/certs/live_support/live_support.key

45- Restrict the key’s permissions so that only root can access it:
    
    sudo chmod 400 /root/certs/live_support/live_support.key

46- Install nginx:

    deactivate
    apt update
    apt install nginx

47- Run nginx:

    sudo systemctl daemon-reload
    sudo systemctl start nginx
    sudo systemctl enable nginx
  
48- Configure nginx:

    sudo nano /etc/nginx/conf.d/live_support.conf

49- Add:
    
    upstream channels-backend {
        server 192.168.115.241:8080;
    }
    
    server {
        listen       8888;
        server_name  192.168.115.241;
    
        location = /favicon.ico { access_log off; log_not_found off; }
    
        error_page 502 /502.html;
        location /502.html {
            root /home/[user]/live_support/live_support/static/errors;
            internal;
        }
    
        error_page 503 504 507 508 /50x.html;
        location /50x.html {
            root /home/[user]/live_support/live_support/static/errors;
            internal;
        }
    
        location /static/ {
            root /home/[user]/live_support/live_support;
        }
    
        location /ws/ {
            try_files $uri @proxy_to_app;
        }
    
        location / {
            include proxy_params;
            proxy_pass http://unix:/home/[user]/live_support/live_support/live_support.sock;
        }
    
        location @proxy_to_app {
            proxy_pass http://channels-backend;
    
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
    
            proxy_redirect off;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Host $server_name;
        }
    }

50- Test your Nginx configuration for syntax errors by typing: 

    sudo /usr/sbin/nginx -t

51- Restart nginx:

    sudo service nginx reload    
    sudo service nginx status
