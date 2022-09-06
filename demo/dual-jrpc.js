import { JrpcClient } from '../jrpc-client.js';

class DualJrpc extends JrpcClient {
  setupDone() {
    console.log('Server connected : ', this.serverURI)
  }

  'JRPCToolsDuoTest.TestBashSyncProc'() {
    console.log('TestBashSyncProc callback from the server ', this.serverURI)
  }

  'JRPCToolsDuoTest.TestBashAsyncProc'() {
    console.log('TestBashAsyncProc callback from the server ', this.serverURI)
  }

  'JRPCToolsDuoTest.TestJsSyncProc'() {
    console.log('TestJsSyncProc callback from the server ', this.serverURI)
  }
}

window.customElements.define('dual-jrpc', DualJrpc);
