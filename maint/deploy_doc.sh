#!/bin/sh

SERVER_IP=192.168.1.82
DEVSRC=~/desktop/doc_output/console
scp -r $DEVSRC/* root@$SERVER_IP:/apps/nginx_cide/home/nginx_cide/www/mibiot-console/
