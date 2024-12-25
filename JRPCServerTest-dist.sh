#!/usr/bin/env bash
function certConfig() {
echo "
# --- no modifications required below ---
[ req ]
default_bits = 2048
default_md = sha256
prompt = no
encrypt_key = no
distinguished_name = dn
req_extensions = req_ext

[ dn ]
C = AU
ST=Some-State
L=Sydney
O = Flatmax
OU=testing
emailAddress=flatmax@flatmax.org
CN = buildroot.deqxbox

[ req_ext ]
subjectAltName = DNS:buildroot.deqxbox" > ./cert/server.cnf
}

if [ ! -d cert.client ]; then
  rm -rf cert.client; mkdir -p cert.client
  certConfig
  openssl req -new -nodes -x509 -days 3650 -config ./cert/server.cnf -keyout ./cert.client/server.key -out ./cert.client/server.crt
  chmod 600 ./cert.client/server.key
fi
if [ ! -d cert.server ]; then
  rm -rf cert.server; mkdir -p cert.server; ln -s cert.server cert
  openssl req -newkey rsa:2048 -new -nodes -x509 -days 365 -keyout cert.server/server.key -out cert.server/server.crt
fi

echo
echo Don\'t forget to run ./JRPCTServerTest.js
echo Don\'t forget to open https://0.0.0.0:9000 in the browser to clear security issues as we are using wss with locally generated certs.
echo

npx wds --config web-dev-server.config.mjs --app-index demo/index-dist.html
