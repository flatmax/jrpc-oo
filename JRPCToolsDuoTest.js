#! /usr/bin/env node
/**
 * Test class to demoing dual jrpc server
 */

"use strict";
const JRPCTools = require('./JRPCTools');

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
let JrpcServer=new JRPCTools.JRPCServer(9000, 300, ssl);
JrpcServer.addClass(firstTest);
// Run second instance on port 9001
let JrpcServer2=new JRPCTools.JRPCServer(9001, 300, ssl);
JrpcServer2.addClass(duoTest);

console.log("Server is listening");
