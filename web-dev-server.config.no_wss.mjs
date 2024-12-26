// import { hmrPlugin, presets } from '@open-wc/dev-server-hmr';

/** Use Hot Module replacement by adding --hmr to the start command */
const hmr = process.argv.includes('--hmr');

export default /** @type {import('@web/dev-server').DevServerConfig} */ ({
  open: true,
  appIndex: 'demo/index.html',
  watch: !hmr,
  /** Resolve bare module imports */
  nodeResolve: true,
  protocol: "http",
  hostname: "0.0.0.0",
  port: 8081,
});
