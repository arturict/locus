// Layout tests with the fake measure: 10 px per character, 16 px per line.
import test from 'node:test';
import assert from 'node:assert/strict';
import { RichText } from '../src/richtext.js';
import { useFakeMeasure } from './helpers.js';

useFakeMeasure();

function doc(runs, width) {
	const d = new RichText();
	d.setWidth(width);
	d.load(runs);
	return d;
}

test('words wrap at the width, trailing spaces stay on the line', () => {
	const d = doc([{ text: 'Hello world foo bar' }], 120);
	const lines = d.layout().lines.map((l) => [l.start, l.end]);
	// "Hello world " (12 chars = 120 px) fits, "foo bar" goes to line 2
	assert.deepEqual(lines, [[0, 12], [12, 20]]);
	assert.equal(d.frame.height, 32);
});

test('a word wider than the line is broken between characters', () => {
	const d = doc([{ text: 'abcdefghij' }], 45);
	assert.deepEqual(d.layout().lines.map((l) => [l.start, l.end]), [[0, 4], [4, 8], [8, 11]]);
});

test('newlines end lines and the final newline adds no empty line', () => {
	assert.equal(doc([{ text: 'a\nb' }], 300).frame.height, 32);
	assert.equal(doc([{ text: 'a\n\n' }], 300).frame.height, 32);
	assert.equal(doc([], 300).frame.height, 16);
});

test('caret positions and hit testing', () => {
	const d = doc([{ text: 'Hello world foo bar' }], 120);
	const layout = d.layout();
	assert.deepEqual(layout.caret(3), { x: 30, y: 0, h: 16, line: 0 });
	assert.deepEqual(layout.caret(12), { x: 0, y: 16, h: 16, line: 1 });
	assert.equal(d.byCoordinate(0, 0).ordinal, 0);
	assert.equal(d.byCoordinate(26, 5).ordinal, 3);
	assert.equal(d.byCoordinate(1, 20).ordinal, 12);
	assert.equal(d.byCoordinate(500, 20).ordinal, 19);
	// right of a wrapped line: before its trailing space
	assert.equal(d.byCoordinate(119, 5).ordinal, 11);
});

test('alignment offsets lines', () => {
	const d = doc([{ text: 'ab\n', align: 'center' }, { text: 'cd', align: 'right' }], 100);
	const [first, second] = d.layout().lines;
	assert.equal(first.glyphs[0].x, 40);
	assert.equal(second.glyphs[0].x, 80);
});

test('list items are indented and numbered', () => {
	const d = doc([{ text: 'one\ntwo' }], 300);
	d.switchListTo(d.documentRange(), 'number');
	const lines = d.layout().lines;
	assert.equal(lines.length, 2);
	assert.deepEqual(lines.map((l) => l.marker.text), ['1.', '2.']);
	assert.ok(lines[0].glyphs.find((g) => g.ch === 'o').x >= 20);
	// caret after the list start code is at the item text
	d.select(0, 0);
	assert.equal(d.selection.start, 1);
});

test('urls are found under the pointer', () => {
	const d = doc([{ text: 'go ' }, { text: 'here', url: 'https://example.org' }], 300);
	assert.equal(d.urlByCoordinate(45, 5), 'https://example.org');
	assert.equal(d.urlByCoordinate(5, 5), '');
});

test('selection rectangles cover the selected characters', () => {
	const d = doc([{ text: 'Hello world foo bar' }], 120);
	assert.deepEqual(d.layout().rects(2, 14), [{ x: 20, y: 0, w: 100, h: 16 }, { x: 0, y: 16, w: 20, h: 16 }]);
});
