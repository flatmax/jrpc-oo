import resolve from '@rollup/plugin-node-resolve';
import commonjs from '@rollup/plugin-commonjs';
import replace from '@rollup/plugin-replace';

export default {
  input: 'jrpc-client.js',
  output: {
    file: 'dist/bundle.js',
    format: 'es',
    inlineDynamicImports: true,
    exports: 'named'
  },
  plugins: [
    resolve({
      browser: true,
      preferBuiltins: false,
      mainFields: ['browser', 'module', 'main'],
      dedupe: ['jrpc'], // Explicitly include jrpc
    }),
    replace({
      'require("crypto")': '({})', // Replace with an empty object
      'require("timers")': '({})', // Replace with an empty object
      'require("./ExposeClass.js")': '({})', // Already bundled inline
      'require(\'jrpc\')': '({})', // Already bundled inline via JRPCExport
      preventAssignment: true, // Important to avoid accidental assignments
    }),
  ]
};