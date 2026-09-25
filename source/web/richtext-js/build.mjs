// Bundles src/ into the script that the GWT app injects (see README.md).
// `node build.mjs --check` fails if the committed bundle is out of date.
import { build } from 'esbuild';
import { readFileSync, writeFileSync } from 'node:fs';

const output = new URL('../carota-web/src/main/resources/org/geogebra/web/richtext/impl/locus-richtext.js',
	import.meta.url);
const banner = '/* Locus rich text editor. EUPL 1.2. Source: source/web/richtext-js.'
	+ ' Based on the design of Carota (c) 2013 Daniel Earwicker, MIT licence. */';

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
		console.error('locus-richtext.js is out of date: run npm run build');
		process.exit(1);
	}
	console.log('locus-richtext.js is up to date');
} else {
	writeFileSync(output, code);
	console.log(`wrote ${output.pathname} (${code.length} bytes)`);
}
