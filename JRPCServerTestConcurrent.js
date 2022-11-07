#! /usr/bin/env node
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

'use strict';

let JRPCServer = require('./JRPCServer');

/** The functions for this test class will automatically be extracted for use with jrpc*/
class TestClass {
  constructor(){
    this.test=1;
    this.i=0;
  }
  fn1(args){
    console.log('this is fn1');
    console.log('got args')
    console.log(arguments)
    console.log('args='+args)
    return 'this is fn1';
  }

//   runMultiCall(jrpcServer) {
//     console.log('runMultiCall : enter')
//     this.multiClientTest(jrpcServer)
// //    setTimeout(this.multiClientTest.bind(this)(jrpcServer), 1000)
//   }

  multiClientTest(jrpcServer){
    // console.log(jrpcServer)
    console.log('multiClientTest : enter')
    jrpcServer.call['TestClass.uniqueFn1'](this.i, 'hi there 1')
    .then((res) => {
      if (Object.keys(res).length>1) // testing
        throw new Error('Expected only one remote to be called');
      let i;
      Object.keys(res).forEach(v=> {
        console.log('remote : '+v+' returns '+res[v])
        i=res[v];
      });
      return jrpcServer.call['TestClass.uniqueFn2'](i, 'hi there 2')
    }).then((res) => {
      if (Object.keys(res).length>1) // testing
        throw new Error('Expected only one remote to be called');
      let i;
      Object.keys(res).forEach(v=> {
        console.log('remote : '+v+' returns '+res[v])
        i=res[v];
      });
      return jrpcServer.call['TestClass.commonFn'](i, 'comon Fn');
    }).then((data)=> {
      console.log('commonFn returns')
      console.log(data)
    }).catch((e) => {
      console.log('multiClientTest : error ')
      console.error(e)
    });
  }
}

let jrpcServer=new JRPCServer.JRPCServer(9000);
let tc = new TestClass;
jrpcServer.addClass(tc); // setup the class for remote use over the network
// console.log(jrpcServer)
// throw new Error('her2')
setTimeout(tc.multiClientTest.bind(tc), 250, jrpcServer)
//tc.runMultiCall(jrpcServer);
