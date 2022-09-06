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
 
import {JrpcClient} from '../jrpc-client.js';
import '@material/mwc-button';

/** This class inherits from JrpcElement and implements
the response functions. i.e. when a function is called on the server
the functions defined in this element are called in response.
*/
export class LocalJrpc extends JrpcClient {
  constructor() {
    super();
    this.remoteTimeout = 300;
  }

  /** server variable is ready to use.
  Create a button for each of the available functions.
  */
  setupDone() {
    Object.keys(this.server).forEach(fn => {
      let btn=document.createElement('mwc-button');
      btn.raised=true; btn.elevation=10;
      btn.onclick=this.server[fn];
      btn.textContent=fn;
      this.shadowRoot.appendChild(btn);
    });
    // add a button to test argument passing
    let btn=document.createElement('mwc-button');
    btn.raised=true; btn.elevation=10;
    btn.onclick=this.testArgPass;
    btn.textContent='testClass.fn2 arg test';
    this.shadowRoot.appendChild(btn);
    // add a button to test no argument passing
    btn=document.createElement('mwc-button');
    btn.raised=true; btn.elevation=10;
    btn.onclick=this.testNoArgPass;
    btn.textContent='testClass.fn1 no arg test';
    this.shadowRoot.appendChild(btn);

    btn=document.createElement('mwc-button');
    btn.raised=true; btn.elevation=10;
    btn.onclick=this.startEchoChamber.bind(this);
    btn.textContent='startEcho';
    this.shadowRoot.appendChild(btn);
  }

  remoteIsUp(){
    console.log('LocalJrpc::remoteIsUp')
    this.addClass(this);
  }

  /** This method test passing arguments to the server
  */
  testArgPass() {
    var lj = document.querySelector('local-jrpc');
    if (lj.server['testClass.fn2']!=null)
      lj.server['testClass.fn2'](1, {0: 'test', 1: [ 1 ,2], 2: 'this function'});
    else
      console.log('expected the server to expose a class testClass with function fn2 but couldn\'t find it');
  }

  /** This method test no passing arguments to the server
  */
  testNoArgPass() {
    var lj = document.querySelector('local-jrpc');
    if (lj.server['testClass.fn1']!=null)
      lj.server['testClass.fn1']();
    else
      console.log('expected the server to expose a class testClass with function fn1 but couldn\'t find it');
  }

  /** This function is defined on the server, when we call
  this.server['testClass.fn1']()
  This function will be called to process the server's response.
  */
  'testClass.fn1'(params) {
    console.log('local-client : response from the server :')
    console.log('local-jrpc : testClass.fn1 : params = '+JSON.stringify(params, null, 2))
  }

  // Don't define this function to force jrpc-client to react to a missing function
  // 'testClass.fn2'(params){
  //   console.log('local-client : response from the server :')
  //   console.log('local-jrpc : testClass.fn2 : params = '+JSON.stringify(params, null, 2))
  // }

  /** This function is defined on the server, when we call
  this.server.system.listComponents()
  This function will be called to process the server's response.
  */
  'system.listComponents'(params) {
    console.log('local-jrpc : system.listComponents : params = '+JSON.stringify(params, null, 2))
  }

  startEchoChamber(){
    this.echoBack('you are in an echo chamber');
  }

  echoBack(args){
    console.log('echoBack '+args)
    if (this.server['testClass.echoBack']!=null)
      this.server['testClass.echoBack']('this is the browser saying echo');
    else
      console.log('expected the server to expose a class testClass with function echoBack but couldn\'t find it');
    return 'echoBack returned you this';
  }

  'testClass.echoBack'(args){
    console.log('testClass.echoBack returned:');
    console.log(args);
  }
}

window.customElements.define('local-jrpc', LocalJrpc);
