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
 
import { LitElement } from 'lit';
import {JrpcClient} from './jrpc-client.js'

/** This JRPC client is used t fire events notifying of the server's presence.
Also indicates to the scanning process when to delete this object.
*/
class JrpcDispatchClient extends JrpcClient {
  /** overload the JrpcClient's setupdone method to fire the event
  */
  setupDone(){
    super.setupDone();
    // We must close the connection once it found
    // for something reason, it's hard for the client to create new connection if the scanner was not closed
    this.ws.close();
    console.log('firing for '+this.serverURI);
    window.dispatchEvent(new CustomEvent('JRPCClientFound',{detail:this.serverURI}))
    this.scanner.deleteMe(this.serverURI);
  }

  /** Servers which aren't found should be removed as well.
  */
  wsError(ev){
    super.wsError(ev);
    this.scanner.deleteMe(this.serverURI);
  }
}
window.customElements.define('jrpc-dispatch-client', JrpcDispatchClient);


/**
  This element scans a network for compliant JRPC servers
  */
export class JrpcScanner extends LitElement {
  static get properties() {
    return {
      port: { type: Number }, // This is the port number to search on the networks for
      wss: { type: Boolean }
    };
  }

  constructor() {
    super();
    this.port = 9000;
    this.wss = false;
  }

  /** Once connected, scan all networks.
  */
  firstUpdated() {
    this.servers=new Array(255);
    this.scanNetworks();
  }

  /** Scan for all networks connected to this unit. Scan for JRPC servers on each network.
  */
  scanNetworks() {
    this.findLocalIp(false).then( ips => {
      ips.forEach( ip =>  this.scanForJrpcServer(ip));
    });
  }

  /** Given an ip address, find the network and create/execute 255 JRPC servers
  \param ip The ip address which contains the network
  */
  scanForJrpcServer(ip) {
    if (ip.split(':').length>1){ // don't process ipv6 addresses
      console.log('non ipv4 address found (not processing) '+ip);
      return;
    }
    // https://groups.google.com/forum/?utm_medium=email&utm_source=footer#!msg/discuss-webrtc/6stQXi72BEU/twDfpwQ4DAAJ
    // chrome mDNS technique
    if (ip.split('-').length>1){ // don't process ipv6 addresses
      console.log('mDNS found '+ip);
      return;
    }

    let net=ip.split('.');
    net[3]=''+0;
    let netName=net.join('.');
    console.log(netName)
    this.servers[netName]=new Array(256);
    this.servers[netName][0]=null;
    for (let i=1; i<256; i++){
      net[3]=''+i;
      this.servers[netName][i]=new JrpcDispatchClient();
      this.servers[netName][i].scanner=this;
      if (this.wss)
        this.servers[netName][i].serverURI="wss://"+net.join('.')+":"+this.port+"/";
      else
        this.servers[netName][i].serverURI="ws://"+net.join('.')+":"+this.port+"/";
      this.servers[netName][i].serverChanged();
    }
  }

  /** delete the JRPC server based on uri
  \param whichOne The ws uri to use to parse to the object for deletion
  */
  deleteMe(whichOne) {
    console.log('deleteMe '+whichOne)
    let i=whichOne.split(':')[1].split('.')[3];
    let net=whichOne.split('/')[2].split(':')[0].split('.');
    net[3]=''+0;
    net=net.join('.');
    this.servers[net][i]=null;
  }

  /** Find all local IP addresses.
  */
  findLocalIp() {
    return new Promise( (resolve, reject) => {
      window.RTCPeerConnection = window.RTCPeerConnection
                              || window.mozRTCPeerConnection
                              || window.webkitRTCPeerConnection;

      if ( typeof window.RTCPeerConnection == 'undefined' )
          return reject('WebRTC not supported by browser');

      let pc = new RTCPeerConnection();
      let ips = [];

      pc.createDataChannel("");
      pc.createOffer()
       .then(offer => pc.setLocalDescription(offer))
       .catch(err => reject(err));
      pc.onicecandidate = event => {
          if ( !event || !event.candidate ) {
              // All ICE candidates have been sent.
              if ( ips.length == 0 )
                  return reject('WebRTC disabled or restricted by browser');

              return resolve(ips);
          }

          let parts = event.candidate.candidate.split(' ');
          let [base,componentId,protocol,priority,ip,port,,type,...attr] = parts;
          let component = ['rtp', 'rtpc'];

          if ( ! ips.some(e => e == ip) )
              ips.push(ip);
      };
    } );
  }
}
window.customElements.define('jrpc-scanner', JrpcScanner);
