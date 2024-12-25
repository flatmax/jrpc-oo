import resolve from '@rollup/plugin-node-resolve';
import commonjs from '@rollup/plugin-commonjs';

export default {
  input: 'jrpc-client.js',
  output: {
    file: 'dist/bundle.js',
    format: 'es',
    inlineDynamicImports: true
  },
  plugins: [
    resolve({
      browser: true,
      preferBuiltins: true,
      mainFields: ['browser', 'module', 'main'],
      moduleDirectories: ['node_modules'],
      resolveOnly: [
        'jrpc/jrpc.min.js',
        'lit'
      ]
    }),
    commonjs({
      transformMixedEsModules: true,
      ignore: ['crypto', 'timers'],
      include: [
        'node_modules/**',
        'node_modules/jrpc/jrpc.min.js'
      ]
    })
  ]
};
