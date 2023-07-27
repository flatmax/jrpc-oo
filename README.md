jrpc-oo Expose objects over the network using the JSON-RPC 2.0 protocol.

Using the objects and webcompoenents, you can have two entities linked by a web-socket execute eachother over the network using the JSON-RPC 2.0 protocol. This could be a browser and nodejs, or two browsers.

# run the webapp demo :

First install the requirements :
```
npm install
```

## setup the nodejs side

```
./JRPCServerTest.js
```

## setup the webapp

To setup run the webapp (answer defaults to the key generation question) :
```
npm start
```
Now clear cert issues in the browser go to the following url to clear the websocket port 9000 : https://0.0.0.0:9000

Now finally run the demo in the webapp : https://0.0.0.0:8081

## in the webapp

You will see the class TestClass functions exposed as buttons. Press some buttons and look at the nodejs side/browser console to see function executions and returned arguments.

## integrate into your apps

Have a look at the jrpc-lit-node repo for an example of integration.

# run the nodejs demo :

First install the requirements :
```
npm install
```
## run the server
```
./JRPCServerTest.js
```
## run the clients in parallel and test

```
./tests/multiTest.sh

```
