FROM ubuntu:18.04

RUN apt update && apt upgrade -y
RUN apt install -y curl gnupg vim nano screen

RUN curl -L https://nginx.org/keys/nginx_signing.key | apt-key add -

RUN echo "deb https://nginx.org/packages/mainline/ubuntu/ bionic nginx" | tee tee /etc/apt/sources.list.d/nginx.list
RUN echo "deb-src https://nginx.org/packages/mainline/ubuntu/ bionic nginx" | tee tee /etc/apt/sources.list.d/nginx.list

RUN apt update && apt install -y nginx

COPY requirements.txt requirements.txt

RUN apt update && apt install -y python3 python3-pip gcc libssl-dev python-gevent
RUN CFLAGS="-I/usr/local/opt/openssl/include" LDFLAGS="-L/usr/local/opt/openssl/lib" UWSGI_PROFILE_OVERRIDE=ssl=true pip3 install uwsgi -Iv
RUN pip3 install -r requirements.txt
RUN pip3 install gevent==1.4.0

COPY . /usr/share/nginx/
COPY nginx.conf /etc/nginx/sites-available/default

COPY services.sh /services.sh
RUN chmod +x /services.sh

WORKDIR /usr/share/nginx/

CMD /./services.sh