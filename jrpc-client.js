/*
Copyright 2017 Flatmax Pty Ltd
You don't have rights to this code unless you are part of Flatmax Pty Ltd.
To have access to this code you must have written consent from Matt Flax @ Flatmax.
If you have found this code, remove it and destroy it immediately. You have no
rights to give it to others in any way, you may not alter it. This license will stay
in place.
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
export class JrpcClient extends JRPCCommon {
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
      this.ws.addEventListener('open', this.createRemote.bind(this), this);
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

  /** When a new websocket exists, setup the JRPC remote to handle message.
  Also, call the server asking for all available functions to be reported.
  */
  createRemote(ev) {
    let remote = this.newRemote();
    this.remoteIsUp();

    this.ws.onmessage = (evMsg) => { remote.receive(evMsg.data); };
    this.setupRemote(remote, this.ws);
  }

  /** Report if we are connected to a server or not
  @return true if connected to a server
  */
  isConnected() {
    return this.server != null && this.server != {};
  }

  /** Overload this to execute code when the remote comes up
  */
  remoteIsUp() {
    console.log('JRPCClient::remoteIsUp')
  }

  /** This function is called once websocket refused / get error
  */
  setupSkip() {
    this.dispatchEvent(new CustomEvent('skip'))
  }

  setupDone() {
    this.dispatchEvent(new CustomEvent('done'))
  }
}

if(!window.customElements.get('jrpc-client')) { window.customElements.define('jrpc-client', JrpcClient); }
