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

var crypto = {};
if (typeof module !== 'undefined' && typeof module.exports !== 'undefined'){  // nodejs
  var ExposeClass = require("./ExposeClass.js");
  crypto = require('crypto');
  if (!crypto.randomUUID)
    crypto.randomUUID = ()=>{return crypto.randomBytes(32).toString('base64');};
  var JRPC = require('jrpc');
  var LitElement=class {};
} else {  // browser
  crypto = self.crypto;
  var ExposeClass = Window.ExposeClass;
  var LitElement = Window.LitElement; // load in the correct class for the browser
}

/** Call remotes in two different ways :
To call one remote :
  this.remote[uuid].rpcs[fnName](args)
  .then((...)=>{...})
  .catch(...)

To call all remotes :
  this.call[fnName](args)
  .then((...)=>{...})
  .catch(...)
*/
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
    remote.uuid = crypto.randomUUID();
    if (this.remotes==null)
      this.remotes = {};
    this.remotes[remote.uuid]=remote;
    return remote;
  }

  /** Function called by the WebSocket once 'connection' is fired
  \param ws The web socket created by the web socket server (in the case of node)
  */
  createRemote(ws){
    let remote = this.newRemote();
    this.remoteIsUp();

    if (this.ws) { // browser version of ws
      ws=this.ws;
      this.ws.onclose =  function (evMsg) {this.rmRemote(evMsg, remote.uuid)}.bind(this);
      this.ws.onmessage = (evMsg) => { remote.receive(evMsg.data); };
    } else { // node version of ws
      ws.on('close', (evMsg, buf)=>this.rmRemote.bind(this)(evMsg, remote.uuid));
      ws.on('message', function(data, isBinary) {
        const msg = isBinary ? data : data.toString(); // changes for upgrade to v8
        remote.receive(msg);
      });
    }

    this.setupRemote(remote, ws);
    return remote;
  }

  /** Overload this to execute code when the remote comes up
  */
  remoteIsUp() {
    console.log('JRPCCommon::remoteIsUp')
  }

  /** Remove the remote
  @param uuid The uuid of the remote to remove
  */
  rmRemote(e, uuid){
    // console.log(uuid)
    // console.log('before')
    // console.log(this.remotes)
    // console.log(this.server)

    // NOTE : this.server to be removed in the future.
    if (this.server) // remove the methods in the remote from the server
      if (this.remotes[uuid])
        if (this.remotes[uuid].rpcs)
          Object.keys(this.remotes[uuid].rpcs).forEach((fn) => {if (this.server[fn]) delete this.server[fn]});

    if (Object.keys(this.remotes).length)
      delete this.remotes[uuid];

    if (this.call && Object.keys(this.remotes).length){
      let remainingFns = []
      for (const remote in this.remotes)
        if (this.remotes[remote].rpcs)
          remainingFns = remainingFns.concat(Object.keys(this.remotes[remote].rpcs))
      if (this.call) {
        let existingFns = Object.keys(this.call);
        for (let n=0; n<existingFns.length; n++)
          if (remainingFns.indexOf(existingFns[n]) < 0)
            delete this.call[existingFns[n]];
      }
    } else
      this.call={}; // reset the call all object

    // console.log('after')
    // console.log('this.call after')
    // console.log(this.call)
    // console.log('this.remotes')
    // console.log(this.remotes)
    // console.log(this.server)
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
  The return values from the function call will execute this['class.method'](returnArgs) here.
  @param fnNames The functions to make available on the server
  @param remote The remote to call
  */
  setupFns(fnNames, remote){
     let self=this;
     fnNames.forEach(fnName => {
      if (remote.rpcs==null) // each remote holds its own rpcs
        remote.rpcs={};

      // each remote's rpcs will hold the functino to call and returns a promise
      remote.rpcs[fnName] = function (params) {
        return new Promise((resolve, reject) => {
          remote.call(fnName, {args : Array.from(arguments)}, (err, result) => {
              if (err) {
                console.log('Error when calling remote function : '+fnName);
                reject(err);
              } else // resolve
                resolve(result);
          });
        });
      };

      // the call structure is to call all remotes
      if (this.call == null) // server holds all remote's rpcs
        this.call={};
      if (this.call[fnName]==null){ // first time in use
        this.call[fnName] = (...args) => {
            let promises = [];
            let rems = [];
            for (const remote in this.remotes){
              if (this.remotes[remote].rpcs[fnName] != null){ // store promises as [uuid : function, ...]
                rems.push(remote);
                promises.push(this.remotes[remote].rpcs[fnName](...args));
              }
            }
            return Promise.all(promises).then((data) => {
              let p = {};
              rems.forEach((v,n)=> p[v]=data[n]);
              return p;
            });
        }
      }

      //////////////////////////////////////////////////
      // For backwards compat - START TO BE REMOVED IN FUTURE
      // if server has a spare spot for that fnName, use it
      // otherwise error out in use (we don't know whot to talk to)
      if (this.server == null) // server holds all remote's rpcs
        this.server={};
      if (this.server[fnName]==null){ // first time in use
        // console.log(fnName+' not in server');
        // note this code should be the same as remote.rpcs[fnName]
        // replicating code here to ensure we don't mess with the orignal
        // remote.rpcs[fnNAme] reference if the else case is triggered in future
        this.server[fnName] = function (params) {
          return new Promise((resolve, reject) => {
            remote.call(fnName, {args : Array.from(arguments)}, (err, result) => {
                if (err) {
                  console.log('Error when calling remote function : '+fnName);
                  reject(err);
                } else // resolve
                  resolve(result);
            });
          });
        };
      } else { // some other remote already uses this fnName, error out
        console.log(fnName+' in server, rejecting calls');
        this.server[fnName] = function (params) {
          return new Promise((resolve, reject) => {
            reject(new Error('More then one remote has this RPC, not sure who to talk to : '+fnName));
          });
        }
      }
      // For backwards compat - END TO BE REMOVED IN FUTURE
      //////////////////////////////////////////////////
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
    c.getRemotes = () => {return this.remotes;} // give the class a method to get the remotes
    c.getCall = () => {return this.call;} // give the class a method to get the call methods back to handle callbacks too all remotes
    // NOTE : getServer will be removed in future
    c.getServer = () => {return this.server;} // give the class a method to get the server back to handle callbacks
    let exposeClass=new ExposeClass();
    let jrpcObj=exposeClass.exposeAllFns(c, objName); // get a js-JRPC friendly function object
    if (this.classes == null)
      this.classes = [jrpcObj];
    else
      this.classes.push(jrpcObj);

    if (this.remotes!=null) // update all existing remotes
      for (const [uuid, remote] of Object.entries(this.remotes)) {
        remote.expose(jrpcObj); // expose the functions from the class
        remote.upgrade();  // Handshake extended capabilities
      }
  }
}

if (typeof module !== 'undefined' && typeof module.exports !== 'undefined')
    module.exports = JRPCCommon;
  else
    Window.JRPCCommon = JRPCCommon;
