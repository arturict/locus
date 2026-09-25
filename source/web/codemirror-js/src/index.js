/*
 * Locus script editor: CodeMirror 6 behind the global API that
 * CodeMirrorEditorWidget (source/web/web) calls.
 * Copyright (c) 2026 Locus contributors, EUPL 1.2.
 * CodeMirror (c) Marijn Haverbeke and others, MIT licence, https://codemirror.net
 */
import { defaultKeymap, history, historyKeymap } from '@codemirror/commands';
import { javascript } from '@codemirror/lang-javascript';
import { bracketMatching, defaultHighlightStyle, indentOnInput, syntaxHighlighting }
	from '@codemirror/language';
import { EditorState } from '@codemirror/state';
import { drawSelection, EditorView, highlightActiveLine, highlightActiveLineGutter, keymap,
	lineNumbers } from '@codemirror/view';

// Locus design tokens (docs/design.md)
const theme = EditorView.theme({
	'&': {
		fontSize: '14px',
		border: '1px solid #d6dade',
		borderRadius: '6px',
		backgroundColor: '#ffffff',
		color: '#1c2024',
		minHeight: '120px'
	},
	'&.cm-focused': {
		outline: '2px solid #0e7c86',
		outlineOffset: '-1px'
	},
	'.cm-scroller': {
		fontFamily: 'ui-monospace, "Noto Sans Mono", Menlo, Consolas, monospace',
		lineHeight: '1.4'
	},
	'.cm-content': {
		minHeight: '120px'
	},
	'.cm-gutters': {
		backgroundColor: '#f4f6f7',
		color: '#5b6470',
		borderRight: '1px solid #d6dade',
		borderRadius: '6px 0 0 6px'
	},
	'.cm-activeLine': {
		backgroundColor: 'rgba(226, 243, 244, 0.5)'
	},
	'.cm-activeLineGutter': {
		backgroundColor: '#e2f3f4'
	},
	'&.cm-focused .cm-selectionBackground, .cm-selectionBackground, ::selection': {
		backgroundColor: 'rgba(14, 124, 134, 0.25)'
	}
});

function toRect(coords) {
	return new DOMRect(coords.left, coords.top, coords.right - coords.left, coords.bottom - coords.top);
}

/**
 * @param {Element} element host element
 * @param {{value?: string, onChange?: function(string)}} options
 */
export function createEditor(element, options) {
	const settings = options || {};
	const onChange = typeof settings.onChange === 'function' ? settings.onChange : null;
	const view = new EditorView({
		parent: element,
		state: EditorState.create({
			doc: settings.value || '',
			extensions: [
				lineNumbers(),
				highlightActiveLineGutter(),
				history(),
				drawSelection(),
				indentOnInput(),
				bracketMatching(),
				highlightActiveLine(),
				syntaxHighlighting(defaultHighlightStyle, { fallback: true }),
				javascript(),
				EditorView.lineWrapping,
				EditorView.contentAttributes.of({ 'aria-label': 'Script', spellcheck: 'false' }),
				keymap.of([...defaultKeymap, ...historyKeymap]),
				theme,
				EditorView.updateListener.of((update) => {
					if (update.docChanged && onChange) {
						onChange(update.state.doc.toString());
					}
				})
			]
		})
	});

	const clamp = (position) => Math.max(0, Math.min(Number(position) || 0, view.state.doc.length));

	return {
		view,
		destroy() {
			view.destroy();
		},
		focus() {
			view.focus();
		},
		getValue() {
			return view.state.doc.toString();
		},
		setValue(text) {
			view.dispatch({ changes: { from: 0, to: view.state.doc.length, insert: text || '' } });
		},
		refresh() {
			view.requestMeasure();
		},
		getCursorPosition() {
			return view.state.selection.main.head;
		},
		setCursorPosition(position) {
			const p = clamp(position);
			view.dispatch({ selection: { anchor: p }, scrollIntoView: true });
		},
		replaceText(from, to, text) {
			const start = clamp(from);
			const end = Math.max(start, clamp(to));
			view.dispatch({ changes: { from: start, to: end, insert: text || '' } });
		},
		getCursorPixelPosition() {
			const coords = view.coordsAtPos(view.state.selection.main.head);
			return coords ? toRect(coords) : view.contentDOM.getBoundingClientRect();
		}
	};
}

const api = { createEditor };
if (typeof window !== 'undefined') {
	window.GeoGebraCodeMirror = api;
}
export default api;
