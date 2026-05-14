#!/usr/bin/env node
/**
 * validate-slide.mjs — 16:9 web-slide HTML 정적 검증
 *
 * 사용: node validate-slide.mjs <file.html>
 *
 * 검사 항목:
 *   1. viewBox = "0 0 1320 742" (16:9 strict)
 *   2. 5-way diff: data-view / view-X / switchView 분기 / applyTheme 분기 / renderX 함수
 *   3. SVG <text x="..."> 마진 (30 ≤ x ≤ 1290)
 *   4. SVG body 안 raw hex 색 카운트 (informational)
 *
 * Exit codes:
 *   0 = OK (warnings only)
 *   1 = ERROR (5-way diff mismatch 또는 viewBox 불일치)
 */

import { readFileSync } from 'node:fs';

const RED = '\x1b[31m', YELLOW = '\x1b[33m', GREEN = '\x1b[32m',
      CYAN = '\x1b[36m', RESET = '\x1b[0m', BOLD = '\x1b[1m';

const file = process.argv[2];
if (!file) {
  console.error('Usage: node validate-slide.mjs <file.html>');
  process.exit(2);
}

let html;
try {
  html = readFileSync(file, 'utf8');
} catch (e) {
  console.error(`${RED}Cannot read file:${RESET} ${file}`);
  process.exit(2);
}

let errors = 0, warnings = 0;
console.log(`${BOLD}${CYAN}== validate-slide ==${RESET} ${file}`);

// ─── 1. viewBox check ──────────────────────────────────────────
// 슬라이드 svg 만 검사 — viewBox 가 "0 0 1320 ..." 으로 시작하는 것.
// icon / marker / theme-toggle 등 작은 viewBox 는 제외.
const slideViewBoxes = [...html.matchAll(/<svg\b[^>]*\sviewBox\s*=\s*["'](0\s+0\s+1320\s+[\d.]+)["']/g)];
if (slideViewBoxes.length === 0) {
  console.log(`${RED}✗ ERROR:${RESET} no slide-sized viewBox found (expected at least one viewBox="0 0 1320 742")`);
  errors++;
} else {
  const allCorrect = slideViewBoxes.every(m =>
    m[1].trim().replace(/\s+/g, ' ') === '0 0 1320 742');
  if (allCorrect) {
    console.log(`${GREEN}✓${RESET} viewBox = "0 0 1320 742" (${slideViewBoxes.length} slide${slideViewBoxes.length > 1 ? 's' : ''})`);
  } else {
    console.log(`${RED}✗ ERROR:${RESET} slide viewBox mismatch (expected "0 0 1320 742" strict 16:9):`);
    slideViewBoxes.forEach(m => {
      const v = m[1].trim().replace(/\s+/g, ' ');
      if (v !== '0 0 1320 742') {
        console.log(`    found: "${v}"`);
      }
    });
    errors++;
  }
}

// ─── 1.5 aspect-ratio CSS 검사 (16:9 strict, SKILL.md §5.2) ────
// .slide / .slide-frame 의 aspect-ratio 가 16/9 또는 1320/742 만 허용.
// 1320/820, 1320/920 같이 비-16:9 비율 modifier 발견 시 ERROR.
const aspectMatches = [...html.matchAll(/aspect-ratio\s*:\s*([0-9./\s]+)\s*[;}]/g)];
const badRatios = [];
for (const m of aspectMatches) {
  const v = m[1].trim().replace(/\s+/g, ' ');
  const ok = (v === '16 / 9' || v === '16/9' || v === '1320 / 742' || v === '1320/742');
  if (!ok) badRatios.push(v);
}
if (badRatios.length > 0) {
  console.log(`${RED}✗ ERROR:${RESET} non-16:9 aspect-ratio CSS found (${badRatios.length}). SKILL.md §5.2 — slide 컨테이너는 16:9 strict.`);
  badRatios.slice(0, 5).forEach(v => console.log(`    found: aspect-ratio: ${v}`));
  errors++;
} else if (aspectMatches.length > 0) {
  console.log(`${GREEN}✓${RESET} all aspect-ratio CSS are 16/9 (${aspectMatches.length} rule${aspectMatches.length > 1 ? 's' : ''})`);
}

// ─── 1.6 emoji 검사 (SKILL.md §5.4) ─────────────────────────────
// SVG <text> element 안에 emoji (pictograph) 가 있으면 ERROR.
// Brand 표현 시 simple-icons SVG / lucide 사용해야 함.
const emojiRe = /[\u{1F300}-\u{1FAFF}\u{2600}-\u{27BF}\u{1F000}-\u{1F2FF}]/u;
let bodyForEmoji = html.replace(/<style[\s\S]*?<\/style>/g, '');
const emojiFound = [];
// SVG text content
for (const m of bodyForEmoji.matchAll(/<text\b[^>]*>([\s\S]*?)<\/text>/g)) {
  if (emojiRe.test(m[1])) emojiFound.push(m[1].slice(0, 40));
}
// JS svg('text', { text: '...' }) — heuristic
for (const m of bodyForEmoji.matchAll(/text\s*:\s*['"]([^'"]+)['"]/g)) {
  if (emojiRe.test(m[1])) emojiFound.push(m[1].slice(0, 40));
}
if (emojiFound.length > 0) {
  console.log(`${RED}✗ ERROR:${RESET} emoji in SVG content (${emojiFound.length}). SKILL.md §5.4 — 브랜드/아이콘은 simple-icons SVG path 또는 lucide 사용.`);
  [...new Set(emojiFound)].slice(0, 5).forEach(s => console.log(`    found: "${s}"`));
  errors++;
}

// ─── 1.7 inline hex 검사 (SKILL.md §5.9, §5.17) ────────────────
// HTML style="...#XXXXXX" 발견 시 ERROR (gradient/border-radius 예외).
// SVG render 와 HTML static 혼합 금지 — CSS 변수만 사용.
const bodyForInlineHex = html.replace(/<style[\s\S]*?<\/style>/g, '');
const inlineHexFound = [];
for (const m of bodyForInlineHex.matchAll(/style\s*=\s*["']([^"']*)["']/g)) {
  const style = m[1];
  if (/gradient|border-radius/.test(style)) continue;
  const hexMatch = style.match(/#[0-9A-Fa-f]{3,6}\b/);
  if (hexMatch) inlineHexFound.push(`${hexMatch[0]} in style="${style.slice(0, 50)}..."`);
}
if (inlineHexFound.length > 0) {
  console.log(`${RED}✗ ERROR:${RESET} inline hex color (${inlineHexFound.length}). SKILL.md §5.9 — CSS 변수만 사용.`);
  inlineHexFound.slice(0, 5).forEach(s => console.log(`    found: ${s}`));
  errors++;
}

// ─── 1.8 .tall/.taller modifier 검사 (SKILL.md §5.2, §5.17) ────
// slide-frame.tall / slide-frame.taller 사용 시 ERROR — viewBox 비-16:9 우회 시도.
const modifierMatches = [...html.matchAll(/slide-frame\s+(tall|taller)\b/g)];
if (modifierMatches.length > 0) {
  console.log(`${RED}✗ ERROR:${RESET} .slide-frame.${modifierMatches[0][1]} modifier (${modifierMatches.length}). SKILL.md §5.2 — 16:9 strict.`);
  errors++;
}

// ─── 2. 5-way diff ─────────────────────────────────────────────
// data-view="X" 추출
const dataViewSet = new Set();
for (const m of html.matchAll(/data-view\s*=\s*["']([^"']+)["']/g)) {
  dataViewSet.add(m[1]);
}

// class="view view-X" 추출 (view-X 만 매치, class 순서 무관)
const viewClassSet = new Set();
for (const m of html.matchAll(/class\s*=\s*["'][^"']*\bview-([\w-]+)/g)) {
  viewClassSet.add(m[1]);
}

// switchView 함수 안의 `view === 'X'` 또는 `view === "X"`
const switchViewSet = new Set();
const switchFnMatch = html.match(/function\s+switchView\s*\([^)]*\)\s*\{([\s\S]*?)\n\}/);
if (switchFnMatch) {
  for (const m of switchFnMatch[1].matchAll(/view\s*===?\s*['"]([\w-]+)['"]/g)) {
    switchViewSet.add(m[1]);
  }
}

// applyTheme 함수 안의 `state.view === 'X'`
const applyThemeSet = new Set();
const applyFnMatch = html.match(/function\s+applyTheme\s*\([^)]*\)\s*\{([\s\S]*?)\n\}/);
if (applyFnMatch) {
  for (const m of applyFnMatch[1].matchAll(/state\.view\s*===?\s*['"]([\w-]+)['"]/g)) {
    applyThemeSet.add(m[1]);
  }
}

// render 함수 — `function renderX()` or `function render_X()` 또는 camelCase 매칭
// data-view 가 'training-result' 이면 renderTrainingResult 또는 renderTrainingresult 매칭
function viewToCamel(v) {
  return v.replace(/-([a-z])/g, (_, c) => c.toUpperCase())
          .replace(/^([a-z])/, (_, c) => c.toUpperCase());
}
const renderFnSet = new Set();
for (const m of html.matchAll(/function\s+render([A-Z]\w*)\s*\(/g)) {
  renderFnSet.add(m[1]);
}

// 5-way 합집합 + 누락 검사
const allViews = new Set([
  ...dataViewSet, ...viewClassSet,
  ...switchViewSet, ...applyThemeSet,
]);

console.log(`\n${BOLD}5-way diff:${RESET}`);
console.log(`  data-view:     {${[...dataViewSet].sort().join(', ')}}`);
console.log(`  view-class:    {${[...viewClassSet].sort().join(', ')}}`);
console.log(`  switchView:    {${[...switchViewSet].sort().join(', ')}}`);
console.log(`  applyTheme:    {${[...applyThemeSet].sort().join(', ')}}`);
console.log(`  render fns:    {${[...renderFnSet].sort().join(', ')}}`);

let diffErr = false;
for (const v of allViews) {
  const camel = viewToCamel(v);
  const missing = [];
  if (!dataViewSet.has(v))   missing.push('data-view');
  if (!viewClassSet.has(v))  missing.push('view-class');
  if (!switchViewSet.has(v)) missing.push('switchView branch');
  if (!applyThemeSet.has(v)) missing.push('applyTheme branch');
  if (!renderFnSet.has(camel)) missing.push(`render${camel}() fn`);

  if (missing.length > 0) {
    console.log(`${RED}✗ ERROR:${RESET} tab '${v}' missing in: ${missing.join(', ')}`);
    diffErr = true;
  }
}
if (!diffErr && allViews.size > 0) {
  console.log(`${GREEN}✓${RESET} all ${allViews.size} tab(s) consistent across 5 locations`);
}
if (diffErr) errors++;

// ─── 2.5 duplicate data-view 검사 ──────────────────────────────
const dataViewList = [...html.matchAll(/data-view\s*=\s*["']([^"']+)["']/g)].map(m => m[1]);
const dupSet = new Set();
const dupes = dataViewList.filter(v => {
  if (dupSet.has(v)) return true;
  dupSet.add(v);
  return false;
});
if (dupes.length > 0) {
  console.log(`${RED}✗ ERROR:${RESET} duplicate data-view: ${[...new Set(dupes)].join(', ')}`);
  errors++;
}

// ─── 3. 마진 검출 ──────────────────────────────────────────────
// SVG <text x="..."> 30..1290 검사
const textXs = [];
for (const m of html.matchAll(/<text[^>]*\sx\s*=\s*["']([\d.-]+)["']/g)) {
  const x = parseFloat(m[1]);
  if (!Number.isFinite(x)) continue;
  if (x < 30 || x > 1290) textXs.push(x);
}

// <rect x="" width=""> 마진 검사 — x + width > 1290 또는 x < 30
const rectViolations = [];
for (const m of html.matchAll(/<rect[^>]*\sx\s*=\s*["']([\d.-]+)["'][^>]*\swidth\s*=\s*["']([\d.-]+)["']/g)) {
  const x = parseFloat(m[1]), w = parseFloat(m[2]);
  if (!Number.isFinite(x) || !Number.isFinite(w)) continue;
  // x=0 width=100% 같이 grid pattern 은 제외 (width 가 정수가 아니거나 100% 형태)
  if (m[2].includes('%')) continue;
  if (x < 30 || x + w > 1290) {
    rectViolations.push(`x=${x} w=${w} (extends to ${x + w})`);
  }
}

const totalMarginViolations = textXs.length + rectViolations.length;
if (totalMarginViolations > 0) {
  console.log(`\n${YELLOW}⚠ WARNING:${RESET} ${totalMarginViolations} element(s) outside slide margin [30, 1290]:`);
  if (textXs.length > 0) {
    console.log(`    <text> x: ${textXs.slice(0, 5).join(', ')}${textXs.length > 5 ? ', ...' : ''}`);
  }
  if (rectViolations.length > 0) {
    console.log(`    <rect>: ${rectViolations.slice(0, 3).join(' / ')}${rectViolations.length > 3 ? ' / ...' : ''}`);
  }
  warnings++;
} else {
  console.log(`\n${GREEN}✓${RESET} all elements within margin [30, 1290]`);
}

// ─── 3.5 heuristic: 데이터 객체 필드 vs render 함수 참조 ───────
// 각 const TAB_X = {...} 또는 const X_DATA = {...} 의 키 → renderX 함수 안 v.key / T.key 참조
const dataObjMatches = [...html.matchAll(/const\s+([A-Z_]+)\s*=\s*\{([\s\S]*?)\n\s*\}\s*;/g)];
const renderFnContents = new Map(); // X → fn body
for (const m of html.matchAll(/function\s+render([A-Z]\w*)\s*\([^)]*\)\s*\{([\s\S]*?)\n\}/g)) {
  renderFnContents.set(m[1], m[2]);
}
const unusedFields = [];
for (const [, name, body] of dataObjMatches) {
  // skill data 객체만 — TAB_XXX 또는 *_DATA 또는 SLIDE 같은
  if (!/^(TAB_|SLIDE|.*_DATA$|.*_HISTORY$|.*_RESULT$)/.test(name)) continue;
  // 상단 레벨 key 만 추출 (간단한 휴리스틱)
  const keys = [...body.matchAll(/\n\s{2,4}(\w+)\s*:/g)].map(m => m[1]);
  // 해당 데이터를 쓰는 render 함수 추정 (이름이 비슷한 것)
  const camelName = name.replace(/^TAB_/, '').toLowerCase()
    .replace(/^([a-z])/, c => c.toUpperCase())
    .replace(/_([a-z])/g, (_, c) => c.toUpperCase());
  // render 함수 안에서 키 참조 검사
  for (const [fn, fnBody] of renderFnContents) {
    if (!fn.toLowerCase().includes(camelName.toLowerCase()) &&
        !camelName.toLowerCase().includes(fn.toLowerCase())) continue;
    for (const key of keys) {
      // T.key 또는 v.key 또는 data.key 패턴 검사
      if (!new RegExp(`\\.${key}\\b`).test(fnBody)) {
        unusedFields.push(`${name}.${key} (not used in render${fn})`);
      }
    }
  }
}
if (unusedFields.length > 0) {
  console.log(`\n${YELLOW}⚠ WARNING:${RESET} ${unusedFields.length} data field(s) defined but not rendered (heuristic):`);
  unusedFields.slice(0, 5).forEach(u => console.log(`    ${u}`));
  if (unusedFields.length > 5) console.log(`    ... and ${unusedFields.length - 5} more`);
  warnings++;
}

// ─── 4. raw hex 카운트 (informational) ──────────────────────────
// <defs>...</defs> 제외
let bodyForHex = html;
bodyForHex = bodyForHex.replace(/<defs[\s\S]*?<\/defs>/g, '');
// CSS 블록도 제외 (raw hex 는 CSS variables 안에서는 OK)
bodyForHex = bodyForHex.replace(/<style[\s\S]*?<\/style>/g, '');
// <script>는 데이터 객체 안에 색 정의가 있을 수 있어 살림 (counting 만 함)

const hexMatches = bodyForHex.match(/#[0-9a-fA-F]{3,8}\b/g) || [];
if (hexMatches.length > 0) {
  console.log(`\n${CYAN}ℹ INFO:${RESET} ${hexMatches.length} raw hex color(s) outside <defs>/<style>`);
  console.log(`    consider using var(--accent), var(--text), etc.`);
  console.log(`    samples: ${[...new Set(hexMatches)].slice(0, 5).join(', ')}`);
}

// ─── Summary ───────────────────────────────────────────────────
console.log('');
if (errors === 0 && warnings === 0) {
  console.log(`${GREEN}${BOLD}✓ OK${RESET} — no errors, no warnings`);
  process.exit(0);
} else if (errors === 0) {
  console.log(`${YELLOW}${BOLD}✓ PASS${RESET} — ${warnings} warning(s), 0 errors`);
  process.exit(0);
} else {
  console.log(`${RED}${BOLD}✗ FAIL${RESET} — ${errors} error(s), ${warnings} warning(s)`);
  process.exit(1);
}
