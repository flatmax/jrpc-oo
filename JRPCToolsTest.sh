#!/usr/bin/env bash
rm -rf cert.client; mkdir -p cert.client
openssl req -newkey rsa:2048 -new -nodes -x509 -days 365 -keyout cert.client/key.pem -out cert.client/cert.pem
rm -rf cert.server; mkdir -p cert.server; ln -s cert.server cert
openssl req -newkey rsa:2048 -new -nodes -x509 -days 365 -keyout cert.server/server.key -out cert.server/server.crt
./install.sh
echo
echo don\'t forget to run ./JRPCToolsTest.js
echo
polymer serve -P https/1.1 --hostname 0.0.0.0 --key cert.client/key.pem --cert cert.client/cert.pem
