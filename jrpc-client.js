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

import './ExposeClass';
import './ExportLit';
import './JRPCExport';
import './JRPCCommon';
let JRPCCommon = Window.JRPCCommon;

/**
  * `jrpc-client`
  * js-jrpc element
  * This element exposes all js-jrpc functions on a compliant server.
  * When the server responds to the first call upon connecting, local functions are
  * created which match the server's functions. If the local functions are called with
  * JSON params, then the server is called.
  * Inheriting parents must define the functions which the server exposes, which will
  * be called once the server responds.
  * @customElement
  * @litelement
  * @demo demo/index.html
  */
export class JRPCClient extends JRPCCommon {
  static get properties() {
    return {
      serverURI: { type: String },
      ws: { type: Object }, // web socket
      server: { type: Object }, // server functions
      remoteTimeout: { type: Number }
    };
  }

  constructor() {
    super();
    this.remoteTimeout = 60;
  }

  updated(changedProps) {
    if (changedProps.has('serverURI')) {
      if (this.serverURI && this.serverURI != "undefined") {
        this.serverChanged()
      }
    }
  }

  /** When the serverIP is set, connect to the new server's websocket
  */
  serverChanged() {
    if (this.ws != null) // get rid of an old server
      delete this.ws;

    // Try to catch the error once ws init failed
    try {
      this.ws = new WebSocket(this.serverURI);
      // set the wss reference to this
      console.assert(this.ws.parent == null, 'wss.parent already exists, this needs upgrade.')
      this.ws.addEventListener('open', this.createRemote.bind(this));
      this.ws.addEventListener('error', this.wsError.bind(this));
    } catch (e) {
      this.serverURI = "";
      if (e.message && e.message.indexOf("Failed to construct 'WebSocket'") >= 0)
        alert (e.message)
      this.setupSkip(e)
    }
  }

  /** When a new websocket doesn't exists, return error
  */
  wsError(ev) {
    this.setupSkip(ev);
  }

  /** Report if we are connected to a server or not
  @return true if connected to a server
  */
  isConnected() {
    return this.server != null && this.server != {};
  }

  /** This function is called if the websocket is refused or gets an error
  */
  setupSkip() {
    this.dispatchEvent(new CustomEvent('skip'))
  }

  setupDone() {
    this.dispatchEvent(new CustomEvent('done'))
  }
}

if(!window.customElements.get('jrpc-client')) { window.customElements.define('jrpc-client', JRPCClient); }
