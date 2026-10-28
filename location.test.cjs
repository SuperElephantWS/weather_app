const { test } = require('node:test');
const assert = require('node:assert/strict');
const { readFileSync } = require('node:fs');
const { runInNewContext } = require('node:vm');
const script = readFileSync(`${__dirname}/static/location.js`, 'utf8');

function setup(geolocation, href = 'https://weather.example/') {
  const status = { textContent: '' };
  const listeners = {};
  const redirects = [];
  runInNewContext(script, {
    document: {
      getElementById: () => status,
      querySelector: () => ({ addEventListener: (event, fn) => { listeners[event] = fn; } }),
    },
    navigator: { geolocation },
    window: { location: {
      href,
      replace: (url) => redirects.push(url),
    } },
    URL, URLSearchParams,
  });
  return { status, listeners, redirects };
}

test('visitor coordinates replace the frame URL', () => {
  const result = setup({ getCurrentPosition(success, error, options) {
    assert.equal(options.timeout, 10000);
    success({ coords: { latitude: 42.36, longitude: -71.06 } });
  } });
  assert.deepEqual(result.redirects, ['https://weather.example/?lat=42.36&lon=-71.06']);
});

test('location detection preserves the embedded strip layout', () => {
  const result = setup({ getCurrentPosition(success) {
    success({ coords: { latitude: 42.36, longitude: -71.06 } });
  } }, 'https://weather.example/?layout=strip');
  const url = new URL(result.redirects[0]);
  assert.equal(url.searchParams.get('layout'), 'strip');
  assert.equal(url.searchParams.get('lat'), '42.36');
  assert.equal(url.searchParams.get('lon'), '-71.06');
});

test('denial, timeout, unsupported browser and thrown errors keep city search', () => {
  for (const geolocation of [undefined,
    { getCurrentPosition: (success, error) => error({ code: 1 }) },
    { getCurrentPosition: (success, error) => error({ code: 3 }) },
    { getCurrentPosition: () => { throw new Error('blocked'); } },
  ]) {
    const result = setup(geolocation);
    assert.match(result.status.textContent, /Search by city/);
    assert.deepEqual(result.redirects, []);
  }
});

test('late detection cannot overwrite a manual city search', () => {
  for (const event of ['input', 'submit']) {
    let success;
    const result = setup({ getCurrentPosition: (callback) => { success = callback; } });
    result.listeners[event]();
    success({ coords: { latitude: 42, longitude: -71 } });
    assert.deepEqual(result.redirects, []);
  }
});

test('invalid coordinates fall back without navigating', () => {
  const result = setup({ getCurrentPosition(success) {
    success({ coords: { latitude: NaN, longitude: 0 } });
  } });
  assert.match(result.status.textContent, /Search by city/);
  assert.deepEqual(result.redirects, []);
});
