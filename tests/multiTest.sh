#!/usr/bin/env bash

if [ -f tests//JRPCServerTestConcurrent.js ]; then
  pushd tests
fi

if [ ! -d cert ]; then
  rm -rf cert; mkdir -p cert
  openssl req -newkey rsa:2048 -new -nodes -x509 -days 365 -keyout cert/server.key -out cert/server.crt
fi

ps ax | grep JRPCServerTestConcurrent.js | grep -v grep | awk '{print $1}' | xargs kill &> /dev/null
sleep 0.1

./JRPCServerTestConcurrent.js &
sleep 0.1
./Client1.js &
./Client2.js
popd
