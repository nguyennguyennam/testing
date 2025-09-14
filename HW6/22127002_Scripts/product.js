// tests/load_1min.js
// Scenario: cache JWT per VU -> search by Name -> product detail
// Data-driven:
//   - data/login.csv    (header: email,password)
//   - data/products.csv (header: Name)

import http from 'k6/http';
import { check, sleep, group } from 'k6';
import { SharedArray } from 'k6/data';
import { htmlReport } from 'https://raw.githubusercontent.com/benc-uk/k6-reporter/2.4.0/dist/bundle.js';

// ---- Config ----
const BASE_URL = __ENV.BASE_URL || 'http://localhost:8091';
const DEBUG = (__ENV.DEBUG || '0') === '1';

// ---- Utils ----
function clean(s = '') { return s.replace(/^"+|"+$/g, '').trim(); }
function jsonHeaders() { return { 'Content-Type': 'application/json', Accept: 'application/json' }; }
function bearerHeaders(token) { return { Authorization: `Bearer ${token}`, Accept: 'application/json' }; }

// ---- Data: login.csv ----
const users = new SharedArray('users', () => {
  const raw = open('../data/login.csv');
  const lines = raw.split(/\r?\n/).filter(l => l.trim() !== '');
  if (lines.length < 2) throw new Error('login.csv is empty.');
  const header = lines[0].trim();
  const delim = header.includes(';') ? ';' : ',';
  const out = lines.slice(1).map((line) => {
    const [email, password] = line.split(delim).map(clean);
    if (DEBUG) console.log(`Email: ${email} Password: ${password}`);
    return (email && password) ? { email, password } : null;
  }).filter(Boolean);
  if (DEBUG) console.log(`[INIT] Loaded ${out.length} users`);
  return out;
});

// ---- Data: products.csv ----
const productNames = new SharedArray('productNames', () => {
  try {
    const raw = open('../data/products.csv').trim();
    const lines = raw.split(/\r?\n/);
    const header = lines[0].trim();
    const delim = header.includes(';') ? ';' : ',';
    const out = lines.slice(1)
      .map(l => (l.split(delim)[0] || '').replace(/^"+|"+$/g, '').trim())
      .filter(Boolean);
    if (DEBUG) console.log(`[INIT] Loaded ${out.length} product names`);
    return out.length ? out : ['Hammer'];
  } catch {
    return ['Hammer'];
  }
});

// ---- Token cache per VU ----
let tokenCache = null;
function getToken() {
  if (tokenCache) return tokenCache;
  const idx = (Math.max(1, __VU) - 1) % users.length;
  const creds = users[idx];

  const res = http.post(`${BASE_URL}/users/login`, JSON.stringify(creds), { headers: jsonHeaders() });
  check(res, { 'login 200': r => r.status === 200 });

  const token = res.json('access_token') || res.json('token') || res.json('data.token');
  check(token, { 'have token': t => !!t });

  tokenCache = token;
  return tokenCache;
}

// ---- Helpers ----
function getProductIdByName(name, hdrs) {
  const res = http.get(`${BASE_URL}/products/search?q=${encodeURIComponent(name)}`, { headers: hdrs });
  check(res, { 'search 200': r => r.status === 200 });

  try {
    const list = res.json('data') || res.json();
    if (Array.isArray(list) && list.length > 0) {
      const exact = list.find(p => (p.name || '').toLowerCase().trim() === name.toLowerCase().trim());
      return (exact?.id) ?? list[0].id;
    }
  } catch (_) { /* ignore */ }
  return null;
}

//SET MODE for different scenario testing
const MODE = (__ENV.MODE || 'load'); //stress; spike and volume

const scenariosByMode = {
  stress: {
    executor: 'ramping-vus',
    startVUs: 0,
    stages: [
      {duration: '20s', target:10}, //Ramp up to 10 VUs Slightly
      {duration: '10s', target:25}, // Keep  Ramp upper average
      {duration: '10s', target:35}, //Ramp to reach the peek
      {duration: '30s', target: 35}, // Maintain peak
      { duration: '20s', target: 20 }, //Recover
      {duration: '20s', target:0 },
      ],
      gracefulRampDown: '30s',
      gracefulStop: '30s', 
  },
spike: {
  executor: 'ramping-vus',
    startVUs: 0,
      stages: [
        { duration: '30s', target: 100 }, // spike high
        { duration: '30s', target: 0 }, // Spike drop
      ],
        gracefulRampDown: '10s',
        gracefulStop: '10s',
  },
  volume: {
    executor: 'shared-iterations',
    vus: 30,                //VU parallel
    iterations:3000,     //total iterations
    maxDuration: '5m',     //time limit
    gracefulStop: '30s',
  },
  load: {
     executor: 'ramping-vus',
      startVUs: 0,
      stages: [
        { duration: '15s', target: 15 }, // ramp up
        { duration: '30s', target: 30 }, // steady
        { duration: '15s', target: 0  }, // ramp down
      ],
      gracefulRampDown: '15s',
      gracefulStop: '15s',
  }
};

//Setup threshold by mode
const thresholdsByMode = {
  stress: {
    http_req_failed: ['rate<0.05'],
    http_req_duration: ['p(95)<1300'],
    'http_req_duration{group:::login}':  ['p(95)<1200'],
    'http_req_duration{group:::search}': ['p(95)<1500'],
    'http_req_duration{group:::detail}': ['p(95)<1200'],
    checks: ['rate>0.95'],
  },
  spike: {
    http_req_failed: ['rate<0.10'],
    http_req_duration: ['p(95)<1800'],
    'http_req_duration{group:::login}':  ['p(95)<1500'],
    'http_req_duration{group:::search}': ['p(95)<2000'],
    'http_req_duration{group:::detail}': ['p(95)<1500'],
    checks: ['rate>0.90'],
  },
  volume: {
    http_req_failed: ['rate<0.05'],
    http_req_duration: ['p(95)<1600'],
    'http_req_duration{group:::login}':  ['p(95)<1500'],
    'http_req_duration{group:::search}': ['p(95)<1800'],
    'http_req_duration{group:::detail}': ['p(95)<1500'],
    checks: ['rate>0.95'],
    iteration_duration: ['p(95)<3500'],
  },
  load: {
    http_req_failed: ['rate<0.03'],
    http_req_duration: ['p(95)<1000'],
    'http_req_duration{group:::login}':  ['p(95)<900'],
    'http_req_duration{group:::search}': ['p(95)<1200'],
    'http_req_duration{group:::detail}': ['p(95)<900'],
    checks: ['rate>0.97'],
  },
};


// ---- Load profile (~1 minute) & SLAs ----
export const options = {
  summaryTrendStats :['avg', 'min', 'med', 'max', 'p(90)', 'p(95)', 'p(99)'],
  scenarios: {
    [MODE]: scenariosByMode[MODE],
  },
  thresholds: thresholdsByMode[MODE] || thresholdsByMode.load,
};

// ---- Test flow ----
export default function () {
  let token;
  group('login', () => {
    token = getToken(); // cached per VU
    check(token, { 'token cached': t => !!t });
  });
  const hdrs = bearerHeaders(token);

  const idx = (__VU + __ITER) % productNames.length;
  const name = productNames[idx];

  let productId = null;
  group('search', () => {
    productId = getProductIdByName(name, hdrs);
    check(productId, { 'have product id': id => !!id });
  });

  if (!productId) { sleep(1); return; }

  group('detail', () => {
    const res = http.get(`${BASE_URL}/products/${productId}`, { headers: hdrs });
    check(res, { 'detail 200': r => r.status === 200 });
  });

  sleep(1); // pacing
}


//REPORTING:HTML with Charts
export function handleSummary(data) {  
  return {
    'summary.html': htmlReport(data),
  };
}
