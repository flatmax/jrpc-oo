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
JRPCTools = require('./JRPCTools');

/** The functions for this test class will automatically be extracted for use with jrpc*/
class TestClass {
  constructor(){
    this.test=1;
  }
  fn1(args){
    console.log('this is fn1');
    console.log('got args')
    console.log(arguments)
    console.log('args='+args)
    return 'this is fn1';
  }

  fn2(arg1, arg2){
    console.log('fn2');
    console.log('arg1 :');
    console.log(JSON.stringify(arg1, null, 2))
    console.log('');
    console.log('arg2 :');
    console.log(JSON.stringify(arg2, null, 2))
    return arg1;
  }

  get server(){return this.getServer();}

  echoBack(args){
    console.log('echoBack '+args)
    setTimeout(this.server['LocalJRPC.echoBack'].bind(this),1000, 'nodejs responding');
    return 'nodejs returning done';
  }

  'LocalJRPC.echoBack'(args){
    console.log('echoBack returns');
    console.log(JSON.stringify(args, null, 2));
  }

  echoBackWithCallback(callback, arg){
    console.log('echoBackWithCallback');
    console.log(arg);
    // Call the provided callback by name, with 1 sec delay and 2 args on the callback
    setTimeout(() => this.server[callback]('echo from nodejs with 2-arg anon callback for return', (err, result) => {
      if (err) {
        console.log('Got error: ');
        console.log(err);
      } else {
        console.log('in 2-arg callback, got return result from client: '+result);
      }
    }), 1000);
    // Call the provided callback by name, with 2 sec delay and 1 arg on the callback
    setTimeout(() => this.server[callback]('echo from nodejs with 1-arg anon callback for return', (result) => {
      console.log('in 1-arg callback, got return result from client: '+result);
    }), 2000);
    // Call the provided callback by name, with 3 sec delay and 0 args on the callback
    setTimeout(() => this.server[callback]('echo from nodejs with 0-arg anon callback for return', () => {
      // normally we just leave this empty, as if we are not looking at the return result we don't care about the response
      // For testing, however, print that the call did return
      console.log('in 0-arg callback, got return from client');
    }), 3000);

    // This is the result that gets returned from this call
    return 'nodejs returning done';
  }
}

class TestClass2 extends TestClass {
  fn3(args){
      console.log(JSON.stringify(args, null, 2));
      return 'this is fn3';
  }
}

tc2=new TestClass2; // this class will be used over js-JRPC

// start the server and add the class.
var JrpcServer=new JRPCTools.JRPCServer(9000); // start a server on port 9000
JrpcServer.addClass(tc2); // setup the class for remote use over the network
