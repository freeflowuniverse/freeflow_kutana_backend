FROM nginx
COPY requirements.txt requirements.txt

RUN apt update && apt install -y python3 python3-dev python3-pip gcc libssl-dev python-gevent libcairo2-dev pkg-config
RUN CFLAGS="-I/usr/local/opt/openssl/include" LDFLAGS="-L/usr/local/opt/openssl/lib" UWSGI_PROFILE_OVERRIDE=ssl=true pip3 install uwsgi==2.0.18 -Iv
RUN pip3 install -r requirements.txt
RUN pip3 install gevent==1.4.0

COPY . /usr/share/nginx/
COPY nginx.conf /etc/nginx/conf.d/default.conf

COPY services.sh /services.sh
RUN chmod +x /services.sh

WORKDIR /usr/share/nginx/

CMD /./services.sh