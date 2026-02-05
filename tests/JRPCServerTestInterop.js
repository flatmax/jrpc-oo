#! /usr/bin/env node
/**
 * Interop test: JS server that calls methods on connected Python clients.
 * 
 * Usage:
 *   node tests/JRPCServerTestInterop.js
 *   # Then connect Python client
 */

"use strict";

const JRPCServer = require('../JRPCServer');

class TestClass {
  constructor() {
    this.test = 1;
  }

  fn1(args) {
    console.log('JS Server: fn1 called with:', args);
    return 'this is fn1 from JS';
  }

  fn2(arg1, arg2) {
    console.log('JS Server: fn2 called with:', arg1, arg2);
    return arg1;
  }

  fn3(args) {
    console.log('JS Server: fn3 called with:', args);
    return 'this is fn3 from JS';
  }
}

// Track test results
let testsPassed = 0;
let testsFailed = 0;

async function runClientTests(server) {
  console.log('');
  console.log('Running JS Server → Python Client tests...');
  console.log('------------------------------------------');
  
  // Wait a moment for client setup to complete
  await new Promise(resolve => setTimeout(resolve, 1000));
  
  // Test 1: Call python_echo on client
  try {
    if (server.call['PythonTestClient.python_echo']) {
      console.log('Test: Calling PythonTestClient.python_echo("hello")...');
      const results = await server.call['PythonTestClient.python_echo']('hello from JS server');
      console.log('  Results:', JSON.stringify(results));
      
      let found = false;
      for (const [uuid, result] of Object.entries(results)) {
        if (result && result.includes('python_echo')) {
          console.log(`  ✓ Client ${uuid.substring(0, 8)}... returned: ${result}`);
          testsPassed++;
          found = true;
        }
      }
      if (!found) {
        console.log('  ✗ No valid response from python_echo');
        testsFailed++;
      }
    } else {
      console.log('  ✗ python_echo method not available');
      testsFailed++;
    }
  } catch (err) {
    console.log('  ✗ Error calling python_echo:', err.message);
    testsFailed++;
  }
  
  // Test 2: Call get_client_type on client
  try {
    if (server.call['PythonTestClient.get_client_type']) {
      console.log('Test: Calling PythonTestClient.get_client_type()...');
      const results = await server.call['PythonTestClient.get_client_type']();
      console.log('  Results:', JSON.stringify(results));
      
      let found = false;
      for (const [uuid, result] of Object.entries(results)) {
        if (result === 'python') {
          console.log(`  ✓ Client ${uuid.substring(0, 8)}... identified as: ${result}`);
          testsPassed++;
          found = true;
        }
      }
      if (!found) {
        console.log('  ✗ No client returned "python"');
        testsFailed++;
      }
    } else {
      console.log('  ✗ get_client_type method not available');
      testsFailed++;
    }
  } catch (err) {
    console.log('  ✗ Error calling get_client_type:', err.message);
    testsFailed++;
  }
  
  // Test 3: Call method with complex args
  try {
    if (server.call['PythonTestClient.echo_data']) {
      console.log('Test: Calling PythonTestClient.echo_data({key: "value", num: 42})...');
      const results = await server.call['PythonTestClient.echo_data']({key: 'value', num: 42});
      console.log('  Results:', JSON.stringify(results));
      
      let found = false;
      for (const [uuid, result] of Object.entries(results)) {
        if (result && result.key === 'value' && result.num === 42) {
          console.log(`  ✓ Client ${uuid.substring(0, 8)}... echoed data correctly`);
          testsPassed++;
          found = true;
        }
      }
      if (!found) {
        console.log('  ✗ No valid echo_data response');
        testsFailed++;
      }
    } else {
      console.log('  ✗ echo_data method not available');
      testsFailed++;
    }
  } catch (err) {
    console.log('  ✗ Error calling echo_data:', err.message);
    testsFailed++;
  }
  
  console.log('------------------------------------------');
  console.log(`JS→Python tests: ${testsPassed} passed, ${testsFailed} failed`);
  
  if (testsFailed === 0 && testsPassed > 0) {
    console.log('JS_SERVER_CLIENT_CALLS_OK');
  }
  
  // Exit after tests
  setTimeout(() => process.exit(testsFailed > 0 ? 1 : 0), 2000);
}

// Start server
const tc = new TestClass();
const server = new JRPCServer.JRPCServer(9000, 60, false); // No SSL for testing
server.addClass(tc);

console.log('JS Interop Test Server started on ws://127.0.0.1:9000');
console.log('Waiting for Python client connection...');

// Override setupDone to trigger tests when client connects
const originalSetupDone = server.setupDone.bind(server);
server.setupDone = function() {
  originalSetupDone();
  console.log('Client connected and setup complete');
  runClientTests(server);
};
