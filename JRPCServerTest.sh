#!/usr/bin/env bash

# Check if no_wss argument is provided
USE_WSS=true
if [ "$1" = "no_wss" ]; then
  USE_WSS=false
fi

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

if [ "$USE_WSS" = true ]; then
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

  # serve the app with web-dev-server using WSS
  npx wds
else
  echo
  echo Starting server without WSS...
  echo Don\'t forget to run ./JRPCTServerTest.js
  echo

  # serve the app with web-dev-server without WSS
  npx wds --node-resolve --watch --app-index demo/index-no-wss.html --port 8081 --config web-dev-server.config.no_wss.mjs
fi

# Copyright (c) 2016-2018 The flatmax-elements Authors. All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
#    * Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
#    * Redistributions in binary form must reproduce the above
# copyright notice, this list of conditions and the following disclaimer
# in the documentation and/or other materials provided with the
# distribution.
#    * Neither the name of Flatmax Pty Ltd nor the names of its
# contributors may be used to endorse or promote products derived from
# this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
