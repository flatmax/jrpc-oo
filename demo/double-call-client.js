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

import {JRPCClient} from '../jrpc-client.js';
import '@material/mwc-button';

/** This class inherits from JRPCClient and implements
the double call test functionality.
*/
export class DoubleCallClient extends JRPCClient {
  constructor() {
    super();
    this.remoteTimeout = 300;
    this.debug = false;
    this.callbackCount = 0;
    console.log('constructor')
  }

  /** server variable is ready to use.
  Create buttons for testing double call functionality.
  */
  setupDone() {
    console.log('setupDone')
    // Create container for buttons and output
    const container = document.createElement('div');
    container.style.padding = '20px';
    container.style.fontFamily = 'Arial, sans-serif';
    
    // Title
    const title = document.createElement('h2');
    title.textContent = 'Double Call Test Client';
    title.style.color = '#333';
    container.appendChild(title);
    
    // Button for simple button press test
    const btnPress = document.createElement('mwc-button');
    btnPress.raised = true;
    btnPress.elevation = 10;
    btnPress.onclick = this.testButtonPress.bind(this);
    btnPress.textContent = 'Test Button Press';
    btnPress.style.margin = '10px';
    container.appendChild(btnPress);
    
    // Button for double call test
    const btnDoubleCall = document.createElement('mwc-button');
    btnDoubleCall.raised = true;
    btnDoubleCall.elevation = 10;
    btnDoubleCall.onclick = this.testDoubleCall.bind(this);
    btnDoubleCall.textContent = 'Test Double Call';
    btnDoubleCall.style.margin = '10px';
    container.appendChild(btnDoubleCall);
    
    // Button to get server status
    const btnStatus = document.createElement('mwc-button');
    btnStatus.raised = true;
    btnStatus.elevation = 10;
    btnStatus.onclick = this.getServerStatus.bind(this);
    btnStatus.textContent = 'Get Server Status';
    btnStatus.style.margin = '10px';
    container.appendChild(btnStatus);
    
    // Button to reset counter
    const btnReset = document.createElement('mwc-button');
    btnReset.raised = true;
    btnReset.elevation = 10;
    btnReset.onclick = this.resetCounter.bind(this);
    btnReset.textContent = 'Reset Counter';
    btnReset.style.margin = '10px';
    container.appendChild(btnReset);
    
    // Output area
    this.outputArea = document.createElement('div');
    this.outputArea.style.marginTop = '20px';
    this.outputArea.style.padding = '10px';
    this.outputArea.style.border = '1px solid #ccc';
    this.outputArea.style.backgroundColor = '#f9f9f9';
    this.outputArea.style.minHeight = '200px';
    this.outputArea.style.whiteSpace = 'pre-wrap';
    this.outputArea.style.fontFamily = 'monospace';
    container.appendChild(this.outputArea);
    
    this.shadowRoot.appendChild(container);
    
    this.logOutput('Client setup complete. Ready for testing.');
  }

  /** Overloading JRPCClient::serverChanged to print out the websocket address
  */
  serverChanged(){
    console.log('Make sure ws url = '+this.serverURI+' has browser security clearance');
    console.log('to do this, goto '+this.serverURI.replace('wss','https')+' in a new browser tab replacing the wss for https\n do this each time the local cert changes or times out');
    super.serverChanged();
  }

  /** JRPCClient::setupSkip calls this overload on websocket connection errors
  */
  setupSkip(){
    super.setupSkip();
    console.log('is JRPCServerTestDoubleCall.py running ?')
    console.log('is the ws url cleared with the browser for access ?')
    this.logOutput('Connection failed. Check if server is running and browser has security clearance.');
  }

  remoteIsUp(){
    console.log('DoubleCallClient::remoteIsUp')
    this.addClass(this);
    this.logOutput('Connected to server successfully.');
  }

  /** Test simple button press functionality
  */
  testButtonPress() {
    this.logOutput('>>> Testing button press...');
    
    if (this.server['DoubleCallTestClass.button_press_handler'] != null) {
      const message = `Button pressed at ${new Date().toLocaleTimeString()}`;
      
      this.server['DoubleCallTestClass.button_press_handler'](message)
      .then((result) => {
        this.logOutput('<<< Button press response:');
        this.logOutput(JSON.stringify(result, null, 2));
      })
      .catch((e) => {
        this.logOutput('Error: ' + e.message);
        console.error(e);
      });
    } else {
      this.logOutput('Error: DoubleCallTestClass.button_press_handler method not found');
    }
  }

  /** Test double call functionality
  */
  testDoubleCall() {
    this.logOutput('>>> Testing double call...');
    
    if (this.server['DoubleCallTestClass.double_call_test'] != null) {
      const firstParam = `First parameter ${Date.now()}`;
      const secondParam = { 
        type: 'test_data', 
        timestamp: new Date().toISOString(),
        random: Math.random()
      };
      
      this.logOutput(`Sending: ${firstParam}, ${JSON.stringify(secondParam)}`);
      
      this.server['DoubleCallTestClass.double_call_test'](firstParam, secondParam)
      .then((result) => {
        this.logOutput('<<< Double call immediate response:');
        this.logOutput(JSON.stringify(result, null, 2));
        this.logOutput('Waiting for server callback...');
      })
      .catch((e) => {
        this.logOutput('Error: ' + e.message);
        console.error(e);
      });
    } else {
      this.logOutput('Error: DoubleCallTestClass.double_call_test method not found');
    }
  }

  /** Get server status
  */
  getServerStatus() {
    this.logOutput('>>> Getting server status...');
    
    if (this.server['DoubleCallTestClass.get_status'] != null) {
      this.server['DoubleCallTestClass.get_status']()
      .then((result) => {
        this.logOutput('<<< Server status:');
        this.logOutput(JSON.stringify(result, null, 2));
      })
      .catch((e) => {
        this.logOutput('Error: ' + e.message);
        console.error(e);
      });
    } else {
      this.logOutput('Error: DoubleCallTestClass.get_status method not found');
    }
  }

  /** Reset server counter
  */
  resetCounter() {
    this.logOutput('>>> Resetting server counter...');
    
    if (this.server['DoubleCallTestClass.reset_counter'] != null) {
      this.server['DoubleCallTestClass.reset_counter']()
      .then((result) => {
        this.logOutput('<<< Reset response:');
        this.logOutput(JSON.stringify(result, null, 2));
      })
      .catch((e) => {
        this.logOutput('Error: ' + e.message);
        console.error(e);
      });
    } else {
      this.logOutput('Error: DoubleCallTestClass.reset_counter method not found');
    }
  }

  /** Client callback method that the server can call
  */
  client_callback(param1, param2, param3) {
    this.callbackCount++;
    
    this.logOutput('*** SERVER CALLBACK RECEIVED ***');
    this.logOutput(`Callback #${this.callbackCount}`);
    this.logOutput(`Param 1: ${param1}`);
    this.logOutput(`Param 2: ${param2}`);
    this.logOutput(`Param 3: ${param3}`);
    
    // Return response to server
    const response = {
      status: 'callback_received',
      callback_count: this.callbackCount,
      received_at: new Date().toISOString(),
      echo_param1: param1,
      echo_param2: param2,
      echo_param3: param3
    };
    
    this.logOutput('Sending callback response to server...');
    
    return response;
  }

  /** Helper method to log output to the display area
  */
  logOutput(message) {
    if (this.outputArea) {
      const timestamp = new Date().toLocaleTimeString();
      this.outputArea.textContent += `[${timestamp}] ${message}\n`;
      this.outputArea.scrollTop = this.outputArea.scrollHeight;
    }
    console.log(message);
  }
}

window.customElements.define('double-call-client', DoubleCallClient);
