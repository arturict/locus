/*
 * Locus rich text: run formatting.
 * Copyright (c) 2026 Locus contributors, EUPL 1.2.
 * The run model follows Carota by Daniel Earwicker (MIT, https://github.com/danielearwicker/carota).
 */

/** Formatting keys in the order in which saved runs list them. */
export const FORMAT_KEYS = ['size', 'font', 'color', 'bgcolor', 'bold', 'italic', 'underline',
	'strikeout', 'align', 'script', 'url'];

/**
 * Values that a run has when it does not name a key. The Java side changes `size`
 * before creating any editor (CarotaUtil.setDefaultFontSize).
 */
export const defaultFormatting = {
	size: 16,
	font: 'Arial, sans-serif',
	color: '#1C2024',
	bgcolor: 'transparent',
	bold: false,
	italic: false,
	underline: false,
	strikeout: false,
	align: 'left',
	script: 'normal',
	url: ''
};

/** Marker for a key that has different values within a range. */
export const multipleValues = Object.freeze({});

export function isMultipleValues(value) {
	return value === multipleValues;
}

const interned = new Map();

function canonicalKeys(format) {
	const extra = Object.keys(format).filter((key) => !FORMAT_KEYS.includes(key)).sort();
	return FORMAT_KEYS.filter((key) => key in format).concat(extra);
}

/**
 * Returns a shared, frozen formatting object with keys in canonical order, so that
 * equal formatting is always the same object.
 */
export function intern(format) {
	const keys = canonicalKeys(format);
	const id = JSON.stringify(keys.map((key) => [key, format[key]]));
	let shared = interned.get(id);
	if (!shared) {
		shared = {};
		for (const key of keys) {
			shared[key] = format[key];
		}
		Object.freeze(shared);
		interned.set(id, shared);
	}
	return shared;
}

function keeps(key, value) {
	if (value === undefined || value === null || value === false || value === '') {
		return false;
	}
	return !(key in defaultFormatting) || value !== defaultFormatting[key];
}

/**
 * Formatting of a run without its text and without values that equal the defaults
 * (Carota's clone semantics). Keys unknown to Locus are kept so that they survive a
 * load/save round trip.
 */
export function cleanFormat(run) {
	const result = {};
	if (!run || typeof run !== 'object') {
		return intern(result);
	}
	for (const key of Object.keys(run)) {
		if (key !== 'text' && keeps(key, run[key])) {
			result[key] = run[key];
		}
	}
	return intern(result);
}

export const EMPTY_FORMAT = intern({});

/** Returns formatting `format` with `key` set to `value` (or removed if it is a default). */
export function withFormat(format, key, value) {
	const copy = Object.assign({}, format);
	if (keeps(key, value)) {
		copy[key] = value;
	} else {
		delete copy[key];
	}
	return intern(copy);
}

/** The value of `key` in `format`, falling back to the default. */
export function resolve(format, key) {
	const value = format[key];
	return value === undefined ? defaultFormatting[key] : value;
}

/** Complete formatting (every key resolved) of a single run. */
export function resolveAll(format) {
	const result = {};
	for (const key of FORMAT_KEYS) {
		result[key] = resolve(format, key);
	}
	return result;
}

/** Merges resolved formatting objects: keys that differ become `multipleValues`. */
export function merge(formats) {
	if (!formats.length) {
		return resolveAll(EMPTY_FORMAT);
	}
	const result = resolveAll(formats[0]);
	for (let i = 1; i < formats.length; i++) {
		for (const key of FORMAT_KEYS) {
			if (result[key] !== multipleValues && result[key] !== resolve(formats[i], key)) {
				result[key] = multipleValues;
			}
		}
	}
	return result;
}
