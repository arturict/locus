// Bundles src/ with QuickJS into the script that the GWT app injects (see README.md).
// `node build.mjs --check` fails if the committed bundle is out of date.
import { build } from 'esbuild';
import { readFileSync, writeFileSync } from 'node:fs';

const output = new URL('../web-common/src/main/resources/org/geogebra/web/html5/main/scripting/locus-quickjs.js',
	import.meta.url);
const banner = '/* Locus JavaScript sandbox. EUPL 1.2. Source: source/web/quickjs-js.'
	+ ' Contains quickjs-emscripten (c) Jake Teton-Landis, MIT, and QuickJS (c) Fabrice Bellard'
	+ ' and Charlie Gordon, MIT, compiled to WebAssembly. */';

const result = await build({
	entryPoints: [new URL('./src/index.js', import.meta.url).pathname],
	bundle: true,
	format: 'iife',
	target: 'es2020',
	minify: true,
	legalComments: 'none',
	banner: { js: banner },
	write: false
});
const code = result.outputFiles[0].text;
if (process.argv.includes('--check')) {
	let current = '';
	try {
		current = readFileSync(output, 'utf8');
	} catch (e) {
		// missing file counts as outdated
	}
	if (current !== code) {
		console.error('locus-quickjs.js is out of date: run npm run build');
		process.exit(1);
	}
	console.log('locus-quickjs.js is up to date');
} else {
	writeFileSync(output, code);
	console.log(`wrote ${output.pathname} (${code.length} bytes)`);
}
