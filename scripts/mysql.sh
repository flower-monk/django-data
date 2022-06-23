#!/bin/bash
container=`docker ps -a | grep mysql-data | wc -l`
if [[ ${container} -ne 0 ]];then
  docker rm -f mysql-data
fi
docker run -itd --name mysql-data -p 3306:3306 -e MYSQL_ROOT_PASSWORD=passwd mysql
