/*
 * Locus rich text: keyboard, IME and clipboard input through a hidden textarea.
 * Copyright (c) 2026 Locus contributors, EUPL 1.2.
 *
 * The textarea holds the selected plain text, fully selected, so that the browser's
 * own copy, cut and text input work (the approach of Carota, MIT, Daniel Earwicker).
 */
import { isTerminator } from './model.js';

/** Rich copy of the last text copied from any Locus editor on this page. */
let richClipboard = null;

export function createTextArea(document) {
	const wrapper = document.createElement('div');
	wrapper.className = 'murokTextArea';
	wrapper.setAttribute('style', 'overflow: hidden; position: absolute; height: 0; top: 0');
	const textarea = document.createElement('textarea');
	for (const [name, value] of [['autocorrect', 'off'], ['autocapitalize', 'off'],
		['spellcheck', 'false'], ['tabindex', '0'], ['aria-label', 'Text']]) {
		textarea.setAttribute(name, value);
	}
	textarea.setAttribute('style', 'position: absolute; padding: 0; width: 1000px; height: 1em;'
		+ ' outline: none; font-size: 4px; border: 0; resize: none; opacity: 0;');
	wrapper.appendChild(textarea);
	return { wrapper, textarea };
}

export class TextInput {
	/**
	 * @param {HTMLTextAreaElement} textarea
	 * @param {object} host optional callbacks:
	 *   navigate(direction, doc) -> boolean: move out of the document (tables),
	 *   escape(doc): Escape key
	 */
	constructor(textarea, host) {
		this.textarea = textarea;
		this.host = host || {};
		this.doc = null;
		this.content = '';
		this.composing = false;
		this.preferredX = null;
		textarea.addEventListener('keydown', (e) => this.onKeyDown(e));
		textarea.addEventListener('input', () => this.onInput());
		textarea.addEventListener('beforeinput', (e) => this.onBeforeInput(e));
		textarea.addEventListener('compositionstart', () => {
			this.composing = true;
		});
		textarea.addEventListener('compositionend', (e) => {
			this.composing = false;
			this.onInput(e.data);
		});
		textarea.addEventListener('copy', (e) => this.onCopy(e, false));
		textarea.addEventListener('cut', (e) => this.onCopy(e, true));
		textarea.addEventListener('paste', (e) => this.onPaste(e));
	}

	attach(doc) {
		this.doc = doc;
		this.preferredX = null;
		this.sync();
	}

	detach() {
		this.doc = null;
	}

	isFocused() {
		const root = this.textarea.getRootNode ? this.textarea.getRootNode() : document;
		return this.textarea.isConnected && root.activeElement === this.textarea;
	}

	focus() {
		if (this.textarea.isConnected) {
			this.textarea.focus({ preventScroll: true });
			this.sync();
		}
	}

	/** Puts the selected text into the textarea and selects it. */
	sync() {
		if (!this.doc || this.composing) {
			return;
		}
		this.content = this.doc.selectedRange().plainText();
		this.textarea.value = this.content;
		if (this.isFocused()) {
			this.textarea.select();
		}
	}

	onInput(composed) {
		if (!this.doc || this.composing) {
			return;
		}
		const value = typeof composed === 'string' ? composed : this.textarea.value;
		if (value !== this.content) {
			this.doc.typeText(value);
		}
		this.sync();
	}

	onBeforeInput(e) {
		if (!this.doc || this.composing) {
			return;
		}
		switch (e.inputType) {
		case 'deleteContentBackward':
		case 'deleteWordBackward':
			e.preventDefault();
			this.doc.deleteBackward(e.inputType === 'deleteWordBackward');
			this.sync();
			break;
		case 'deleteContentForward':
		case 'deleteWordForward':
			e.preventDefault();
			this.doc.deleteForward(e.inputType === 'deleteWordForward');
			this.sync();
			break;
		case 'insertLineBreak':
		case 'insertParagraph':
			e.preventDefault();
			this.doc.newline(e.inputType === 'insertLineBreak');
			this.sync();
			break;
		default:
		}
	}

	onCopy(e, cut) {
		if (!this.doc) {
			return;
		}
		const range = this.doc.selectedRange();
		const text = range.plainText();
		if (!text) {
			return;
		}
		richClipboard = { text, runs: range.save() };
		if (e.clipboardData) {
			e.clipboardData.setData('text/plain', text);
			e.preventDefault();
		}
		if (cut) {
			this.doc.deleteSelection();
			this.sync();
		}
	}

	onPaste(e) {
		if (!this.doc || !e.clipboardData) {
			return;
		}
		e.preventDefault();
		const text = e.clipboardData.getData('text/plain');
		if (richClipboard && text === richClipboard.text) {
			// keep formatting when pasting text copied from a Locus editor
			const filtered = this.doc.insertFilters.reduce(
				(value, filter) => (value === null || value === undefined ? value : filter(value)), text);
			if (filtered === text) {
				this.doc.insert(richClipboard.runs);
				this.sync();
				return;
			}
		}
		this.doc.typeText(text, 'insert');
		this.sync();
	}

	caretX(doc) {
		const layout = doc.layout();
		return layout.caret(doc.focusPosition ?? doc.selection.end).x;
	}

	/** New caret position for a navigation key, or null if the key leaves the document. */
	target(key, doc, ctrl) {
		const layout = doc.layout();
		const focus = doc.focusPosition ?? doc.selection.end;
		const max = doc.maxCaret;
		switch (key) {
		case 'ArrowLeft':
			if (focus === 0) {
				return null;
			}
			return ctrl ? doc.wordStart(focus) : doc.validPosition(focus - 1, -1);
		case 'ArrowRight':
			if (focus >= max) {
				return null;
			}
			return ctrl ? doc.wordEnd(focus) : doc.validPosition(focus + 1, 1);
		case 'ArrowUp':
		case 'ArrowDown': {
			const line = layout.lineIndexOf(focus);
			const next = line + (key === 'ArrowUp' ? -1 : 1);
			if (next < 0 || next >= layout.lines.length) {
				return null;
			}
			if (this.preferredX === null) {
				this.preferredX = layout.caret(focus).x;
			}
			return doc.validPosition(layout.ordinalInLine(next, this.preferredX), 1);
		}
		case 'Home':
			if (ctrl) {
				return 0;
			}
			return doc.validPosition(layout.lines[layout.lineIndexOf(focus)].start, 1);
		case 'End':
			if (ctrl) {
				return max;
			}
			return layout.ordinalInLine(layout.lineIndexOf(focus), Infinity);
		case 'PageUp':
			return 0;
		case 'PageDown':
			return max;
		default:
			return undefined;
		}
	}

	onKeyDown(e) {
		const doc = this.doc;
		if (!doc || this.composing || e.isComposing || e.keyCode === 229) {
			return;
		}
		const ctrl = e.ctrlKey || e.metaKey;
		const key = e.key;
		let handled = true;
		if (!['ArrowUp', 'ArrowDown'].includes(key)) {
			this.preferredX = null;
		}
		const navigation = this.target(key, doc, ctrl);
		if (navigation !== undefined) {
			const { start, end } = doc.selection;
			if (navigation === null) {
				if (!e.shiftKey && this.host.navigate && this.host.navigate(key, doc)) {
					e.preventDefault();
					e.stopPropagation();
					return;
				}
				if (!e.shiftKey && start !== end) {
					const p = key === 'ArrowLeft' || key === 'ArrowUp' ? start : end;
					doc.select(p, p);
				} else if (key === 'ArrowUp' || key === 'ArrowDown') {
					const p = key === 'ArrowUp' ? 0 : doc.maxCaret;
					if (e.shiftKey) {
						doc.extendTo(p);
					} else {
						doc.select(p, p);
					}
				}
			} else if (e.shiftKey) {
				doc.extendTo(navigation);
			} else if (start !== end && !ctrl && (key === 'ArrowLeft' || key === 'ArrowRight')) {
				const p = key === 'ArrowLeft' ? start : end;
				doc.select(p, p);
			} else {
				doc.select(navigation, navigation);
			}
		} else {
			switch (key) {
			case 'Backspace':
				doc.deleteBackward(ctrl);
				break;
			case 'Delete':
				doc.deleteForward(ctrl);
				break;
			case 'Enter':
				doc.newline(e.shiftKey);
				break;
			case 'Escape':
				// let the application see Escape as well
				e.preventDefault();
				doc.fireEscape();
				if (this.host.escape) {
					this.host.escape(doc);
				}
				return;
			case 'Tab':
				handled = !!(this.host.navigate && this.host.navigate(e.shiftKey ? 'ShiftTab' : 'Tab', doc));
				break;
			default:
				handled = ctrl && !e.altKey && this.shortcut(key.toLowerCase(), e.shiftKey, doc);
			}
		}
		if (handled) {
			e.preventDefault();
			e.stopPropagation();
			this.sync();
		}
	}

	shortcut(key, shift, doc) {
		switch (key) {
		case 'a':
			doc.select(0, doc.maxCaret);
			return true;
		case 'b':
			doc.toggleFormat('bold');
			return true;
		case 'i':
			doc.toggleFormat('italic');
			return true;
		case 'u':
			doc.toggleFormat('underline');
			return true;
		case 'z':
			doc.performUndo(shift);
			return true;
		case 'y':
			doc.performUndo(true);
			return true;
		default:
			return false;
		}
	}
}

/** Word selection helper for double click that ignores terminators. */
export function wordRange(doc, position) {
	const chars = doc.model.chars;
	if (isTerminator(chars[position]) && position > 0) {
		return doc.wordRangeAt(position - 1);
	}
	return doc.wordRangeAt(position);
}
