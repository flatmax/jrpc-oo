jrpc-oo Expose objects over the network using the JSON-RPC 2.0 protocol.

Using the objects and webcompoenents, you can have two entities linked by a web-socket execute eachother over the network using the JSON-RPC 2.0 protocol. This could be a browser and nodejs, many browsers or many nodejs instances.

# Example
On one side of the network create a server listening on port 9000. Then add a TestClass to the JRPCServer. For example in nodejs :
```javascript
JRPCServer = require('./JRPCServer');

/** The functions for this test class will automatically be extracted for use with jrpc*/
class TestClass {
  fn2(arg1, arg2){
    console.log('fn2');
    console.log('arg1 :');
    console.log(JSON.stringify(arg1, null, 2))
    console.log('');
    console.log('arg2 :');
    console.log(JSON.stringify(arg2, null, 2))
    return arg1;
  }
}

let tc=new TestClass; // this class will be executed over the network using JRPC2

// start the server and add the class.
var JrpcServer=new JRPCServer.JRPCServer(9000); // start a server on port 9000
JrpcServer.addClass(tc); // setup the class for remote use over the network
```

On the other side of the network create a client which auto-connects to port 9000. In the browser, create a button which calls TestClass::fn2 on the server. Here is example code for the browser  :
```javascript
import {JRPCClient} from '../jrpc-client.js';
import '@material/mwc-button';

/** This class inherits from JrpcClient.
*/
export class LocalJRPC extends JRPCClient {
  /** Once the webcomponent is ready, connect to the server on port 9000
  */
  firstUpdated() {
    this.serverURI="wss://0.0.0.0:9000";
  }

  /** setupDone is called once connected and the server is ready to use.
  Create a button for each for the function call.
  */
  setupDone() {
    // add a button to test argument passing
    let btn=document.createElement('mwc-button');
    btn.raised=true; btn.elevation=10;
    btn.onclick=this.testArgPass;
    btn.textContent='TestClass.fn2 arg test';
    this.shadowRoot.appendChild(btn);
  }

  /** Call class TestClass method fn2 here. This method tests passing arguments to the server.
  */
  testArgPass() {
    this.call['TestClass.fn2'](1, {0: 'test', 1: [ 1 ,2], 2: 'this function'})
    .then((result)=>{
      console.log(result);
    })
    .catch((e)=>{console.error(e.message)});
  }
}

window.customElements.define('local-jrpc', LocalJRPC);
```

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
