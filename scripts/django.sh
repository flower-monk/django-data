#!/bin/bash

update_flag=$1
container=`docker ps -a | grep django-app | wc -l`
if [[ ${container} -ne 0 ]];then
  docker rm -f django-app
fi

cd /home/project/django-data/
if [[ ${update_flag} == 'update' ]];then
    git pull
fi
if [[ ${update_flag} == 'clone' ]];then
    git clone  git@github.com:flower-monk/django-data.git
fi
docker run \
--name django-app \
-v /home/project/django-data:/usr/src/app \
-w /usr/src/app \
-p 8000:8000 \
--privileged=true \
-d python:3.9 \
bash -c "pip install --no-index --find-links=./packages/ -r requirements.txt && python3 manage.py runserver 0.0.0.0:8000 && sleep 50000"



docker logs -f django-app
