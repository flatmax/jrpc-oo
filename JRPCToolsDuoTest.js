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

/**
 * Test class to demoing dual jrpc server
 */

"use strict";
const JRPCServer = require('./JRPCServer');

const execSync = require("child_process").execSync;
const { exec } = require("child_process");

class JRPCToolsDuoTest {
  /**
   * Node call synchronise exec child process
   * Execute multiple bash scrips :
   * printout 'hello world'
   * then sleep 3 seconds before printout the current active path
   *
   * this case block the next process
   */
  TestBashSyncProc() {
    return new Promise(resolve => {
      return resolve(execSync('echo "hello world" && sleep 3 && pwd',{stdio: 'inherit'}));
    });
  }

  /**
   * Node call asynchronise exec child process
   * Execute multiple bash scrips :
   * printout 'hello world'
   * then sleep 3 seconds before printout the current active path
   */
  TestBashAsyncProc() {
    let bs = exec('echo "hello world" && sleep 3 && pwd');
    bs.stdout.on('data', (data) => {
      console.log(data.toString());
    });
    return new Promise(resolve => {
      bs.on('exit', () => {
        return resolve();
      });
    })
  }

  /**
   * return a promise
   * printout a text after 5s
   */
  asyncProc() {
    return new Promise((resolve)=>{
      setTimeout(()=>{
        console.log("hello")
        resolve();
      }, 5000)
    })
  }
  /**
   * Test a JS sync process
   */
  async TestJsSyncProc() {
    await this.asyncProc(); // convert async to sync process
    return console.log("It should be printed after hello")
  }
}

let firstTest = new JRPCToolsDuoTest;
let duoTest = new JRPCToolsDuoTest;

let ssl=false;
// Run first instance on port 9000
let JrpcServer=new JRPCServer.JRPCServer(9000, 300, ssl);
JrpcServer.addClass(firstTest);
// Run second instance on port 9001
let JrpcServer2=new JRPCServer.JRPCServer(9001, 300, ssl);
JrpcServer2.addClass(duoTest);

console.log("Server is listening");
