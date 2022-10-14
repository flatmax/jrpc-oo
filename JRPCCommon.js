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

"use strict";

if (typeof module !== 'undefined' && typeof module.exports !== 'undefined'){  // nodejs
  var ExposeClass = require("./ExposeClass.js")
  var JRPC = require('jrpc');
  var LitElement=class {};
} else {  // browser
  var ExposeClass = Window.ExposeClass;
  var LitElement = Window.LitElement; // load in the correct class for the browser
}

class JRPCCommon extends LitElement {
  /** Instansiate a new remote. It gets added to the array of remotes
  @return the new remote
  */
  newRemote(){
    let remote;
    if (typeof Window === 'undefined') // nodejs
      remote = new JRPC({ remoteTimeout: this.remoteTimeout }); // setup the remote
    else // browser
      remote = new Window.JRPC({ remoteTimeout: this.remoteTimeout }); // setup the remote
    if (this.remote==null)
      this.remote = [remote];
    else
      this.remote.push(remote);
    return remote;
  }

  /** expose classes and handle the setting up of remote's functions
  @param remote the remote to setup
  @param ws the websocket for transmission
  */
  setupRemote(remote, ws){
    remote.setTransmitter(this.transmit.bind(ws)); // Let JRPC send requests and responses continuously
    if (this.classes)
      this.classes.forEach((c) => {
        remote.expose(c);
      });
    remote.upgrade();

    remote.call('system.listComponents', [], (err, result) => {
      if (err) {
        console.log(err);
        console.log('Something went wrong when calling system.listComponents !');
      } else // setup the functions for overloading
        this.setupFns(Object.keys(result), remote);
    });
  }

  /** Transmit a message or queue of messages to the server.
  Bind the web socket to this method for calling this.send
  @param msg the message to send
  @param next the next to execute
  */
  transmit(msg, next){
  	try {
  	  this.send(msg);
  	  return next(false);
  	} catch (e) {
      console.log(e);
  	  return next(true);
  	}
  }

  /** Setup functions for calling on the server. It allows you to call server['class.method'](args) in your code.
  If the last argument is a callback, it will be called when the remote call returns. It can have zero
  arguments if not expecting a result, 1 if you only want the result, or 2 for a normal error,result callback.
  If you don't provide a callback, the return values from the function call will execute this['class.method'](returnArgs) here.
  @param fnNames The functions to make available on the server
  @param remote The remote to call
  */
  setupFns(fnNames, remote){
     let self=this;
     fnNames.forEach(fnName => {
      if (this.server==null)
        this.server={};

      this.server[fnName] = function (params) {
        if (typeof(arguments[arguments.length-1]) === 'function') {
          // The last argument is a function, so use it as the result callback instead of the default named method
          let callback = arguments[arguments.length-1];
          let args = {args: Array.from(arguments).slice(0,-1)};
          switch (callback.length) {
            case 0:    // Caller doesn't want a result
              remote.call(fnName, args, (err, result) => {
                if (err) {
                  console.log('Error when calling remote function : '+fnName);
                  console.log(err);
                } else {
                  callback();
                }
              });
              break;
            case 1:    // Callback takes a single arg, so provide default error handling
              remote.call(fnName, args, (err, result) => {
                if (err) {
                  console.log('Error when calling remote function : '+fnName);
                  console.log(err);
                } else {
                  callback(result);
                }
              });
              break;
            case 2:    // Standard err, result callback
              remote.call(fnName, args, (err, result) => { callback(err, result) });
              break;
            default:   // oops
              console.log('Error: too many arguments in callback to : '+fnName);
              console.log('Expecting 0 (no result), 1 (result only), or 2 (error, result):');
              console.log(callback);
              break;
          }
        } else {
          // Callback not provided, so construct one that calls a static named function
          remote.call(fnName, {args : Array.from(arguments)}, (err, result) => {
            if (err) {
              console.log('Error when calling remote function : '+fnName);
              console.log(err);
            } else // call the overloaded function
             if (self.constructor.name === 'JRPCServer') // nodejs
               if (this[fnName]==null)
                 console.log("function not defined Error : "+fnName+" is not in your element, please define this function.");
               else
                 this[fnName](result);
             else // browser
              if (self[fnName]==null)
                console.log("function not defined Error : "+fnName+" is not in your element, please define this function.");
              else
                self[fnName](result);
          });
        }
      };
    });
    this.setupDone();
  }

  /** This function is called once the client has been contacted and the server functions are
  set up.
  You should overload this function to get a notification once the 'server' variable is ready
  for use.
  */
  setupDone(){}

  /** Add a class to the JRPC system. All functions in the class are exposed for use.
  \param c The class to expose for use in the JRPC system.
  \param objName If name is specified, then use it rather then the constructor's name to prepend the functions.
  */
  addClass(c, objName){
    c.getServer = () => {return this.server;} // give the class a method to get the server back to handle callbacks
    let exposeClass=new ExposeClass();
    let jrpcObj=exposeClass.exposeAllFns(c, objName); // get a js-JRPC friendly function object
    if (this.classes == null)
      this.classes = [jrpcObj];
    else
      this.classes.push(jrpcObj);

    if (this.remote!=null) // update all existing remotes
      this.remote.forEach(function(remote){
        remote.expose(jrpcObj); // expose the functions from the class
        remote.upgrade();  // Handshake extended capabilities
      });
  }
}

if (typeof module !== 'undefined' && typeof module.exports !== 'undefined')
    module.exports = JRPCCommon;
  else
    Window.JRPCCommon = JRPCCommon;
