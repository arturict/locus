/*
 * Locus rich text: the text box editor (`murok.editor.create`).
 * Copyright (c) 2026 Locus contributors, EUPL 1.2.
 */
import { createTextArea, TextInput, wordRange } from './input.js';
import { RichText } from './richtext.js';

/**
 * Pointer position in the local, untransformed coordinates of `element`, relative to
 * its content box. offsetX/offsetY already undo CSS transforms (rotation, scale).
 */
export function localPoint(element, event) {
	let x = event.offsetX;
	let y = event.offsetY;
	let target = event.target;
	while (target && target !== element && target.offsetParent !== undefined) {
		x += target.offsetLeft || 0;
		y += target.offsetTop || 0;
		target = target.offsetParent;
	}
	const style = element.ownerDocument.defaultView.getComputedStyle(element);
	return {
		x: x - (parseFloat(style.paddingLeft) || 0) - (parseFloat(style.borderLeftWidth) || 0),
		y: y - (parseFloat(style.paddingTop) || 0) - (parseFloat(style.borderTopWidth) || 0)
	};
}

/** Paints a document into a canvas of its own (when the host does not paint it). */
export function paintInto(canvas, width, height, draw) {
	const ratio = Math.max(1, canvas.ownerDocument.defaultView.devicePixelRatio || 1);
	canvas.width = Math.ceil(width * ratio);
	canvas.height = Math.ceil(height * ratio);
	canvas.style.width = width + 'px';
	canvas.style.height = height + 'px';
	const ctx = canvas.getContext('2d');
	ctx.setTransform(ratio, 0, 0, ratio, 0, 0);
	ctx.clearRect(0, 0, width, height);
	draw(ctx);
}

export function createEditor(element) {
	const document = element.ownerDocument;
	const view = document.defaultView;
	if (view.getComputedStyle(element).position === 'static') {
		element.style.position = 'relative';
	}
	element.innerHTML = '';
	const canvas = document.createElement('canvas');
	canvas.className = 'murokEditorCanvas';
	canvas.width = 0;
	canvas.height = 0;
	canvas.setAttribute('style', 'position: absolute; width: 0px; height: 0px; pointer-events: none;');
	const { wrapper, textarea } = createTextArea(document);
	element.appendChild(canvas);
	element.appendChild(wrapper);
	element.style.cursor = 'text';

	const doc = new RichText();
	const input = new TextInput(textarea);
	let externalPaint = false;
	let paintPending = false;

	const paint = () => {
		paintPending = false;
		if (externalPaint) {
			return;
		}
		if (!doc.widthValue && element.clientWidth) {
			doc.setWidth(element.clientWidth);
		}
		const layout = doc.layout();
		paintInto(canvas, Math.max(layout.width, element.clientWidth, 1),
			Math.max(layout.height, 1), (ctx) => doc.draw(ctx));
	};
	const schedulePaint = () => {
		if (!externalPaint && !paintPending) {
			paintPending = true;
			view.requestAnimationFrame(paint);
		}
	};

	doc.hooks = {
		isActive: () => textarea.isConnected,
		hasFocus: () => input.isFocused(),
		focus: () => input.focus(),
		changed: () => {
			input.sync();
			schedulePaint();
		}
	};
	input.attach(doc);
	textarea.addEventListener('focus', schedulePaint);
	textarea.addEventListener('blur', schedulePaint);

	Object.defineProperty(doc, 'externalScale', {
		get: () => doc.scale,
		set: (value) => {
			doc.scale = Number(value) > 0 ? Number(value) : 1;
		}
	});
	Object.defineProperty(doc, 'externalPaint', {
		get: () => externalPaint,
		set: (value) => {
			externalPaint = !!value;
			if (externalPaint) {
				canvas.width = 0;
				canvas.height = 0;
				canvas.style.width = '0px';
				canvas.style.height = '0px';
			} else {
				schedulePaint();
			}
		}
	});

	// pointer input
	let dragging = false;
	element.addEventListener('pointerdown', (e) => {
		if (e.button !== 0) {
			return;
		}
		e.preventDefault();
		const point = localPoint(element, e);
		const ordinal = doc.byCoordinate(point.x, point.y).ordinal;
		if (e.shiftKey) {
			doc.extendTo(ordinal);
		} else {
			doc.select(ordinal, ordinal, true);
		}
		dragging = true;
		if (element.setPointerCapture) {
			element.setPointerCapture(e.pointerId);
		}
	});
	element.addEventListener('pointermove', (e) => {
		if (dragging) {
			const point = localPoint(element, e);
			doc.extendTo(doc.byCoordinate(point.x, point.y).ordinal);
		}
	});
	const endDrag = () => {
		if (dragging) {
			dragging = false;
			input.focus();
		}
	};
	element.addEventListener('pointerup', endDrag);
	element.addEventListener('pointercancel', endDrag);
	element.addEventListener('dblclick', (e) => {
		const point = localPoint(element, e);
		const range = wordRange(doc, doc.byCoordinate(point.x, point.y).ordinal);
		doc.select(range.start, range.end, true);
	});

	doc.sendKey = (key, shift, ctrl) => input.onKeyDown({ key, shiftKey: !!shift, ctrlKey: !!ctrl,
		metaKey: false, altKey: false, preventDefault() {}, stopPropagation() {} });
	schedulePaint();
	return doc;
}
