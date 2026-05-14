#!/usr/bin/env node
/**
 * scaffold.mjs — 새 web-slide deck 자동 생성
 *
 * 사용:
 *   node scaffold.mjs <output.html> <deck-title> <tab1>[:layout1] <tab2>[:layout2] ...
 *
 * 예시:
 *   node scaffold.mjs ~/decks/cobot.html "cobot2 — 협동 로봇 시스템" \
 *        overview:title-hero system:architecture-diagram metrics:metric-cards
 *
 * 출력:
 *   - multi-tab-shell.html 을 복사하여 사용자 지정 탭 N 개로 자동 확장
 *   - 각 탭의 data 객체 + render 함수 + view div + 양분기를 자동 패치
 *   - validator 통과 보장 (5-way diff 자동 일치)
 */

import { readFileSync, writeFileSync } from 'node:fs';
import { dirname, resolve, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const TEMPLATES_DIR = join(__dirname, '..', 'templates');
const SHELL_PATH = join(TEMPLATES_DIR, 'multi-tab-shell.html');

const RED = '\x1b[31m', YELLOW = '\x1b[33m', GREEN = '\x1b[32m',
      CYAN = '\x1b[36m', RESET = '\x1b[0m', BOLD = '\x1b[1m';

// ─── Args ──────────────────────────────────────────────────────
const args = process.argv.slice(2);
if (args.length < 3) {
  console.error(`${RED}Usage:${RESET} node scaffold.mjs <output.html> <title> <tab1[:layout]> <tab2[:layout]> ...`);
  console.error('');
  console.error(`${BOLD}Layouts:${RESET} title-hero, 3-column, architecture-diagram, timeline-history, metric-cards, sequence-diagram`);
  console.error('');
  console.error(`${BOLD}Example:${RESET}`);
  console.error('  node scaffold.mjs ~/decks/myproject.html "My Project" \\');
  console.error('       overview:title-hero arch:architecture-diagram metrics:metric-cards');
  process.exit(2);
}

const [outPath, title, ...tabSpecs] = args;
const outputPath = resolve(outPath);

if (tabSpecs.length === 0) {
  console.error(`${RED}Need at least 1 tab.${RESET}`);
  process.exit(2);
}
if (tabSpecs.length > 7) {
  console.error(`${RED}Max 7 tabs (got ${tabSpecs.length}).${RESET} Split into multiple decks.`);
  process.exit(2);
}

// Parse tab specs (name:layout or just name)
const tabs = tabSpecs.map(spec => {
  const [name, layout = 'title-hero'] = spec.split(':');
  if (!/^[a-z][a-z0-9-]*$/.test(name)) {
    console.error(`${RED}Invalid tab name '${name}'${RESET} — must be lowercase, kebab-case, start with letter`);
    process.exit(2);
  }
  return { name, layout, label: capitalize(name) };
});

function capitalize(s) {
  return s.split('-').map(w => w[0].toUpperCase() + w.slice(1)).join(' ');
}

function viewToCamel(v) {
  return v.replace(/-([a-z])/g, (_, c) => c.toUpperCase())
          .replace(/^([a-z])/, (_, c) => c.toUpperCase());
}

// ─── Shell template 로드 ──────────────────────────────────────
let html;
try {
  html = readFileSync(SHELL_PATH, 'utf8');
} catch (e) {
  console.error(`${RED}Cannot read template:${RESET} ${SHELL_PATH}`);
  process.exit(2);
}

console.log(`${BOLD}${CYAN}== scaffold ==${RESET}`);
console.log(`  output: ${outputPath}`);
console.log(`  title:  ${title}`);
console.log(`  tabs:   ${tabs.length}`);
tabs.forEach(t => console.log(`    · ${t.name.padEnd(20)} → ${t.layout}`));

// ─── Title 치환 ───────────────────────────────────────────────
html = html.replace(/\{\{TITLE\}\}/g, title);

// ─── 탭 버튼 row 교체 ─────────────────────────────────────────
const newTabsBlock = tabs.map((t, i) =>
  `  <button class="tab${i === 0 ? ' active' : ''}" data-view="${t.name}">${t.label}</button>`
).join('\n');

html = html.replace(
  /<div class="tabs">[\s\S]*?<\/div>/,
  `<div class="tabs">\n${newTabsBlock}\n</div>`
);

// ─── view 컨테이너 교체 ──────────────────────────────────────
const newViews = tabs.map((t, i) => `  <!-- view-${t.name} (${t.layout}) -->
  <div class="view view-${t.name}${i === 0 ? ' active' : ''}">
    <svg class="slide" viewBox="0 0 1320 742"
         preserveAspectRatio="xMidYMin meet"
         xmlns="http://www.w3.org/2000/svg">
      <defs>
        <pattern id="grid-${t.name}" x="0" y="0" width="32" height="32"
                 patternUnits="userSpaceOnUse">
          <path d="M 32 0 L 0 0 0 32" fill="none"
                stroke="var(--line)" stroke-width="0.5" opacity="0.2"/>
        </pattern>
      </defs>
      <rect width="100%" height="100%" fill="url(#grid-${t.name})"
            pointer-events="none"/>
      <g id="${t.name}-content"></g>
    </svg>
  </div>`).join('\n\n');

html = html.replace(
  /<main>[\s\S]*?<\/main>/,
  `<main>\n${newViews}\n</main>`
);

// ─── 데이터 객체 + render 함수 교체 ──────────────────────────
const dataObjects = tabs.map(t => {
  const c = viewToCamel(t.name);
  return `const TAB_${c.toUpperCase()} = {
  title: '${t.label}',
  subtitle: '${t.name.toUpperCase()} · ${t.layout}',
  // TODO: ${t.layout} 레이아웃의 데이터 추가
  // 참고: ~/.claude/skills/web-slide/templates/slide-layouts/${t.layout}.md
};`;
}).join('\n\n');

const contentRefs = tabs.map(t =>
  `const $${viewToCamel(t.name).toLowerCase()}Content = document.getElementById('${t.name}-content');`
).join('\n');

const renderFns = tabs.map(t => {
  const c = viewToCamel(t.name);
  const varName = c.toLowerCase() + 'Content';
  return `function render${c}() {
  clear($${varName});
  const T = TAB_${c.toUpperCase()};
  $${varName}.appendChild(svg('text', {
    class: 'flow-title-sub', x: 30, y: 32, text: T.subtitle,
  }));
  $${varName}.appendChild(svg('text', {
    class: 'flow-title-text', x: 30, y: 70, text: T.title,
  }));
  $${varName}.appendChild(svg('text', {
    x: 660, y: 380, 'text-anchor': 'middle',
    fill: 'var(--text-3)', 'font-size': 18,
    text: '${t.layout} — 콘텐츠 추가',
  }));
  // TODO: ${t.layout} 패턴 따라 채우기
  // ~/.claude/skills/web-slide/templates/slide-layouts/${t.layout}.md
}`;
}).join('\n\n');

// switchView 분기
const switchBranches = tabs.map((t, i) => {
  const c = viewToCamel(t.name);
  const op = i === 0 ? 'if' : 'else if';
  return `  ${op} (view === '${t.name}') render${c}();`;
}).join('\n');

// applyTheme 분기
const applyBranches = tabs.map((t, i) => {
  const c = viewToCamel(t.name);
  const op = i === 0 ? 'if' : 'else if';
  return `  ${op} (state.view === '${t.name}') render${c}();`;
}).join('\n');

// 초기 view
const initialView = tabs[0].name;

// 데이터 + render 블록 교체
const oldDataBlock = /\/\/ ─── Data 객체 \(탭별\)[\s\S]*?\/\/ ─── View 전환/;
const newDataBlock = `// ─── Data 객체 (탭별) ─────────────────────────────────
${dataObjects}

// ─── Render 함수 (탭별) ───────────────────────────────
${contentRefs}

${renderFns}

// ─── View 전환`;

html = html.replace(oldDataBlock, newDataBlock);

// switchView body 교체
html = html.replace(
  /(\/\/ ★ 새 탭 추가 시 여기에 분기 추가\n)([\s\S]*?)(\n\}\n\n\/\/ ─── 테마 토글)/,
  `$1${switchBranches}$3`
);

// applyTheme body 교체
html = html.replace(
  /(\/\/ ★ 새 탭 추가 시 여기에도 분기 추가[^\n]*\n)([\s\S]*?)(\n\}\n\nfunction toggleTheme)/,
  `$1${applyBranches}$3`
);

// 초기 state.view
html = html.replace(/view:\s*'overview'/, `view: '${initialView}'`);

// ─── 출력 ─────────────────────────────────────────────────────
try {
  writeFileSync(outputPath, html, 'utf8');
} catch (e) {
  console.error(`${RED}Cannot write:${RESET} ${outputPath}`);
  console.error(e.message);
  process.exit(2);
}

console.log('');
console.log(`${GREEN}✓ scaffolded${RESET} → ${outputPath}`);
console.log('');
console.log(`${BOLD}Next steps:${RESET}`);
console.log(`  1. open ${outputPath}   # 브라우저로 열어 동작 확인`);
console.log(`  2. 각 탭의 TAB_XXX 데이터 객체 채우기`);
console.log(`  3. render 함수에 콘텐츠 그리기 (layout md 참조)`);
console.log(`  4. node ${join(__dirname, 'validate-slide.mjs')} ${outputPath}`);
