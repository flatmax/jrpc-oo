#!/usr/bin/env bash
ps ax | grep JRPCServerTestConcurrent.js | grep -v grep | awk '{print $1}' | xargs kill &> /dev/null
sleep 0.1

./JRPCServerTestConcurrent.js &
sleep 0.1
./tests/Client1.js &
./tests/Client2.js
