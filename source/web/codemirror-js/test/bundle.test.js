// Runs the committed bundle in jsdom and exercises the API that CodeMirrorEditorWidget calls.
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { JSDOM } from 'jsdom';

const bundle = readFileSync(new URL(
	'../../web/src/main/resources/org/geogebra/web/full/gui/util/locus-codemirror.js', import.meta.url), 'utf8');

function load() {
	const dom = new JSDOM('<!doctype html><div id="host"></div>', { runScripts: 'outside-only',
		pretendToBeVisual: true });
	const { window } = dom;
	// jsdom has no layout; CodeMirror only needs these to exist
	window.document.createRange = () => ({
		setStart() {}, setEnd() {}, getClientRects: () => [], getBoundingClientRect: () => new window.DOMRect()
	});
	window.eval(bundle);
	return window;
}

test('the bundle defines window.GeoGebraCodeMirror.createEditor', () => {
	const window = load();
	assert.equal(typeof window.GeoGebraCodeMirror.createEditor, 'function');
});

test('editor API: value, change listener, cursor, replace, destroy', () => {
	const window = load();
	const changes = [];
	const host = window.document.getElementById('host');
	const editor = window.GeoGebraCodeMirror.createEditor(host,
		{ value: 'ggbApplet.setValue("a", 3)', onChange: (v) => changes.push(v) });
	for (const name of ['destroy', 'focus', 'getValue', 'setValue', 'refresh', 'getCursorPosition',
		'setCursorPosition', 'replaceText', 'getCursorPixelPosition']) {
		assert.equal(typeof editor[name], 'function', name);
	}
	assert.equal(editor.getValue(), 'ggbApplet.setValue("a", 3)');
	assert.ok(host.querySelector('.cm-editor'), 'editor DOM');
	assert.ok(host.querySelector('.cm-lineNumbers'), 'line numbers');
	editor.setCursorPosition(9);
	assert.equal(editor.getCursorPosition(), 9);
	// what insertCommand does for a chip
	const pos = editor.getCursorPosition();
	editor.replaceText(pos, pos, 'X()');
	editor.setCursorPosition(pos + 2);
	assert.equal(editor.getValue(), 'ggbAppletX().setValue("a", 3)');
	assert.equal(editor.getCursorPosition(), 11);
	assert.equal(changes[changes.length - 1], 'ggbAppletX().setValue("a", 3)');
	editor.setValue('SetValue(a, 1)');
	assert.equal(editor.getValue(), 'SetValue(a, 1)');
	editor.replaceText(-5, 1000, 'x');
	assert.equal(editor.getValue(), 'x');
	editor.refresh();
	const rect = editor.getCursorPixelPosition();
	assert.equal(typeof rect.left, 'number');
	assert.equal(typeof rect.bottom, 'number');
	editor.destroy();
	assert.equal(host.querySelector('.cm-editor'), null);
});

test('JavaScript is highlighted', async () => {
	const window = load();
	const host = window.document.getElementById('host');
	window.GeoGebraCodeMirror.createEditor(host, { value: 'var x = "text"; // note' });
	await new Promise((resolve) => setTimeout(resolve, 50));
	const spans = [...host.querySelectorAll('.cm-line span')].map((s) => s.className);
	assert.ok(spans.length >= 3, 'highlighted tokens: ' + spans.join(' '));
});
