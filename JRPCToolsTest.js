#! /usr/bin/env node
/**
 * Test the paraeq classes in js and C++
 *
 * Copyright 2017 Flatmax Pty Ltd
 * Restricted proprietary licence.
 * You have no rights to this file, if you have this file you may not use it
 * you will delete it immediately. You have no rights to alter this file or give
 * it to anyone else be they an individual, group or company.
 */

JRPCTools = require('./JRPCTools');

/** The functions for this test class will automatically be extracted for use with jrpc*/
class testClass {
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
    setTimeout(this.server['LocalJrpc.echoBack'].bind(this),1000, 'nodejs responding');
    return 'nodejs returning done';
  }

  'LocalJrpc.echoBack'(args){
    console.log('echoBack returns');
    console.log(args);
  }
}

class testClass2 extends testClass {
  fn3(args){
      console.log(args);
      return 'this is fn3';
  }
}

tc2=new testClass2; // this class will be used over js-JRPC

// start the server and add the class.
var JrpcServer=new JRPCTools.JRPCServer(9000); // start a server on port 9000
JrpcServer.addClass(tc2); // setup the class for remote use over the network
