import { spawn } from 'child_process';
import svelte from 'rollup-plugin-svelte';
import commonjs from '@rollup/plugin-commonjs';
import terser from '@rollup/plugin-terser';
import resolve from '@rollup/plugin-node-resolve';
import livereload from 'rollup-plugin-livereload';
import css from 'rollup-plugin-css-only';
import replace from '@rollup/plugin-replace';
import dotenv from 'dotenv';

const production = !process.env.ROLLUP_WATCH;

// Cargar variables de entorno desde .env
dotenv.config();

function serve() {
	let server;

	function toExit() {
		if (server) server.kill(0);
	}

	return {
		writeBundle() {
			if (server) return;
			server = spawn('npm', ['run', 'start', '--', '--dev'], {
				stdio: ['ignore', 'inherit', 'inherit'],
				shell: true
			});

			process.on('SIGTERM', toExit);
			process.on('exit', toExit);
		}
	};
}

export default {
	input: 'src/main.js',
	output: {
		sourcemap: true,
		format: 'iife',
		name: 'app',
		file: 'public/build/bundle.js'
	},
	plugins: [
		svelte({
			compilerOptions: {
				// enable run-time checks when not in production
				dev: !production
			}
		}),
		// we'll extract any component CSS out into
		// a separate file - better for performance
		css({ output: 'bundle.css' }),

		// Reemplazar variables de entorno en el código
		replace({
			preventAssignment: true,
			values: (()=>{
				let geoserverUrlValue = process.env.GEOSERVER_URL || 'http://localhost:8087/geoserver/wms';
				// Remove leading/trailing quotes if they exist, to prevent double quoting by JSON.stringify
				if (typeof geoserverUrlValue === 'string' && geoserverUrlValue.length > 1 && geoserverUrlValue.startsWith('"') && geoserverUrlValue.endsWith('"')) {
					geoserverUrlValue = geoserverUrlValue.substring(1, geoserverUrlValue.length - 1);
				}
				let apiUrlValue = process.env.API_URL || 'http://localhost:7070/api';
				if (typeof apiUrlValue === 'string' && apiUrlValue.length > 1 && apiUrlValue.startsWith('"') && apiUrlValue.endsWith('"')) {
					apiUrlValue = apiUrlValue.substring(1, apiUrlValue.length - 1);
				}
				return {
					'__API_URL__': JSON.stringify(apiUrlValue),
					'__GEOSERVER_URL__': JSON.stringify(geoserverUrlValue)
				};
			})()
		}),

		// If you have external dependencies installed from
		// npm, you'll most likely need these plugins. In
		// some cases you'll need additional configuration -
		// consult the documentation for details:
		// https://github.com/rollup/plugins/tree/master/packages/commonjs
		resolve({
			browser: true,
			dedupe: ['svelte'],
			exportConditions: ['svelte']
		}),
		commonjs(),

		// In dev mode, call `npm run start` once
		// the bundle has been generated
		!production && serve(),

		// Watch the `public` directory and refresh the
		// browser on changes when not in production
		!production && livereload('public'),

		// If we're building for production (npm run build
		// instead of npm run dev), minify
		production && terser()
	],
	watch: {
		clearScreen: false
	}
};
