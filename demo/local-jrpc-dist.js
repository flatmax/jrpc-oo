/**
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
 */

import {JRPCClient} from '../dist/bundle.js';
import '@material/mwc-button';

/** This class inherits from JrpcElement and implements
the response functions. i.e. when a function is called on the server
the functions defined in this element are called in response.
*/
export class LocalJRPC extends JRPCClient {
  constructor() {
    super();
    this.remoteTimeout = 300;
  }

  /** server variable is ready to use.
  Create a button for each of the available functions.
  */
  setupDone() {
    // add a button to test argument passing
    let btn=document.createElement('mwc-button');
    btn.raised=true; btn.elevation=10;
    btn.onclick=this.testArgPass;
    btn.textContent='TestClass.fn2 arg test';
    this.shadowRoot.appendChild(btn);
    // add a button to test no argument passing
    btn=document.createElement('mwc-button');
    btn.raised=true; btn.elevation=10;
    btn.onclick=this.testNoArgPass;
    btn.textContent='TestClass.fn1 no arg test';
    this.shadowRoot.appendChild(btn);

    btn=document.createElement('mwc-button');
    btn.raised=true; btn.elevation=10;
    btn.onclick=this.startEchoChamber.bind(this);
    btn.textContent='startEcho';
    this.shadowRoot.appendChild(btn);
  }

  /** Overloading JRPCCLient::serverChanged to print out the websocket address
  */
  serverChanged(){
      console.log('Make sure ws url = '+this.serverURI+' has browser serurity clearance');
      console.log('to do this, goto '+this.serverURI.replace('wss','https')+' in a new browser tab replacing the wss for https\n do this each time the local cert changes or times out');
      super.serverChanged();
  }

  /** JRPCClient::setupSkip calls this overload on websocket connection errors
  */
  setupSkip(){
    super.setupSkip();
    console.log('is JRPC-OO.node.js running ?')
    console.log('is the ws url cleared with the browser for access ?')
  }

  remoteIsUp(){
    console.log('LocalJRPC::remoteIsUp')
    this.addClass(this);
  }

  /** This method test passing arguments to the server
  */
  testArgPass() {
    var lj = document.querySelector('local-jrpc');
    if (lj.server['TestClass.fn2']!=null)
      lj.server['TestClass.fn2'](1, {0: 'test', 1: [ 1 ,2], 2: 'this function'})
      .then((result)=>{
        console.log(result);
      })
      .catch((e)=>{console.error(e.message)});
    else
      console.log('expected the server to expose a class TestClass with function fn2 but couldn\'t find it');
  }

  /** This method test no passing arguments to the server
  */
  testNoArgPass() {
    var lj = document.querySelector('local-jrpc');
    if (lj.server['TestClass.fn1']!=null)
      lj.server['TestClass.fn1']()
      .then((result)=>{
        console.log(result);
      })
      .catch((e)=>{console.error(e.message)});
    else
      console.log('expected the server to expose a class TestClass with function fn1 but couldn\'t find it');
  }

  startEchoChamber(){
    this.echoBack('you are in an echo chamber');
  }

  echoBack(args){
    console.log('echoBack '+args)
    if (this.server['TestClass.echoBack']!=null)
      this.server['TestClass.echoBack']('this is the browser saying echo')
      .then((args)=> {
        console.log('TestClass.echoBack returned:');
        console.log(JSON.stringify(args, null, 2));
      })
    else
      console.log('expected the server to expose a class TestClass with function echoBack but couldn\'t find it');
    return 'echoBack returned you this';
  }
}

window.customElements.define('local-jrpc', LocalJRPC);
