#!/bin/sh

SERVER_IP=192.168.3.192
DEVSRC=~/desktop/doc_output/console
scp -r $DEVSRC/* root@$SERVER_IP:/www/mibiot-console/
