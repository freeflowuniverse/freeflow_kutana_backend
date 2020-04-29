install:
	cp ./config/freeflow_config_example.py ./config/freeflow_config.py
	sudo apt update && sudo apt install -y python3 python3-pip gcc libssl-dev python-gevent
	CFLAGS="-I/usr/local/opt/openssl/include" LDFLAGS="-L/usr/local/opt/openssl/lib" UWSGI_PROFILE_OVERRIDE=ssl=true sudo pip3 install uwsgi -Iv
	sudo pip3 install -r requirements.txt
	sudo pip3 install gevent==1.4.0

flask-run:
	export FLASK_DEBUG=1 && python3 app.py

server-run:
	uwsgi --disable-logging --http :5000 --gevent 1000 --http-websockets --master --wsgi-file app.py --callable app

docker-run:
	docker rm -f ffc_backend_api || true
	docker rm -f ffc_backend_redis || true
	export DOCKER_IMAGE_TAG=local && export CI_COMMIT_TAG=v1.0.0 && docker-compose build
	export DOCKER_IMAGE_TAG=local && export CI_COMMIT_TAG=v1.0.0 && docker-compose up -d