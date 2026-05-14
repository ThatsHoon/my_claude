# SVG primitives — helper / 카드 / wrap 카탈로그

## 1. svg() helper

가장 핵심. 6 줄. 모든 render 함수가 이걸 호출.

```js
const SVG_NS = 'http://www.w3.org/2000/svg';

function svg(tag, attrs = {}, ...children) {
  const e = document.createElementNS(SVG_NS, tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (k === 'text') e.textContent = v;
    else if (k === 'class') e.setAttribute('class', v);
    else if (v != null) e.setAttribute(k, v);
  }
  for (const c of children) {
    if (typeof c === 'string') e.appendChild(document.createTextNode(c));
    else if (c) e.appendChild(c);
  }
  return e;
}

function clear(node) {
  while (node.firstChild) node.removeChild(node.firstChild);
}
```

사용:
```js
$content.appendChild(svg('text', {
  x: 30, y: 60,
  fill: 'var(--text)', 'font-size': 22, 'font-weight': 800,
  text: '슬라이드 제목',
}));
```

## 2. 텍스트 줄바꿈 — wrapSvgText

SVG `<text>` 는 자동 wrap 안 됨. 헬퍼:

```js
function wrapSvgText(text, maxChars = 36) {
  if (text.length <= maxChars) return [text];
  const lines = [];
  let remaining = text;
  while (remaining.length > maxChars) {
    let cut = remaining.lastIndexOf(' ', maxChars);
    if (cut < maxChars * 0.5) cut = maxChars;
    lines.push(remaining.slice(0, cut));
    remaining = remaining.slice(cut).trim();
  }
  if (remaining) lines.push(remaining);
  return lines;
}
```

사용:
```js
wrapSvgText('긴 텍스트...', 30).forEach((ln, i) => {
  $content.appendChild(svg('text', {
    x: 30, y: 100 + i * 18,
    fill: 'var(--text)', 'font-size': 12,
    text: ln,
  }));
});
```

한글의 경우: 공백이 적어 `lastIndexOf(' ')` 가 안 잡힘 → 강제 cut 으로 폴백. 한글 문장은 maxChars 더 작게 (예: 18~22).

## 3. 카드 (rect + top strip + drop-shadow)

cobot2 와 동일한 시각 언어. 모든 카드는 이 4 요소 조합:

```js
function drawCard({x, y, w, h, color}) {
  // bg
  $content.appendChild(svg('rect', {
    x, y, width: w, height: h, rx: 12,
    fill: 'var(--bg-3)',
    stroke: color || 'var(--line-2)',
    'stroke-opacity': color ? 0.5 : 1,
    'stroke-width': 1.4,
    filter: 'drop-shadow(0 2px 8px rgba(0,0,0,0.4))',
  }));
  // top strip (5 px 컬러 띠) — color 가 있을 때만
  if (color) {
    $content.appendChild(svg('rect', {
      x: x + 1.5, y: y + 1.5, width: w - 3, height: 5, rx: 2,
      fill: color,
    }));
  }
}
```

## 4. 섹션 헤더 (번호 + 라벨 + 액센트 라인)

```js
function drawSectionHeader({x, y, num, label, color}) {
  // 큰 번호 (Georgia italic)
  $content.appendChild(svg('text', {
    x: x + 18, y: y + 48,
    class: 'flow-section-num',
    text: num,  // '01', '02', ...
  }));
  // 라벨 (UPPERCASE)
  $content.appendChild(svg('text', {
    x: x + 82, y: y + 30,
    class: 'flow-section-label',
    fill: color,
    text: label,
  }));
  // 액센트 라인 (40 px)
  $content.appendChild(svg('line', {
    x1: x + 82, y1: y + 38, x2: x + 122, y2: y + 38,
    stroke: color, 'stroke-width': 2, 'stroke-linecap': 'round',
  }));
}
```

CSS:
```css
.flow-section-num {
  font: italic 800 56px Georgia, serif;
  fill: var(--text); opacity: 0.18;
}
.flow-section-label {
  font: 700 12px ui-monospace, monospace;
  letter-spacing: 1.3px; text-transform: uppercase;
}
```

## 5. 대시 분할선

```js
$content.appendChild(svg('line', {
  x1: x + 16, y1: dividerY, x2: x + cardW - 16, y2: dividerY,
  stroke: 'var(--line)', 'stroke-dasharray': '2 3',
}));
```

`stroke-dasharray` 변형: `'2 3'` (촘촘), `'4 4'` (균등), `'6 4'` (긴 점선).

## 6. 마커 (화살표 / 닫힌 화살촉)

```html
<defs>
  <marker id="ah-default" viewBox="0 0 10 10"
          refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto">
    <polygon points="0 0, 10 5, 0 10" fill="#64748b"/>
  </marker>
</defs>
```

사용:
```js
svg('line', {
  x1, y1, x2, y2,
  stroke: 'var(--text-3)', 'stroke-width': 1.5,
  'marker-end': 'url(#ah-default)',
});
```

`<defs>` 안의 marker 는 raw hex 사용 가능 (테마 토큰 미지원). 테마별로 다른 마커가 필요하면 dark/light 둘 다 정의해 두고 JS 로 switch.

## 7. 카드 안 chip / pill

```js
function drawChip({x, y, w, h, text, color}) {
  $content.appendChild(svg('rect', {
    x, y, width: w, height: h, rx: 6,
    fill: color, 'fill-opacity': 0.10,
    stroke: color, 'stroke-width': 1,
  }));
  $content.appendChild(svg('text', {
    x: x + w / 2, y: y + h / 2 + 4,
    fill: color,
    'font-size': 11, 'font-weight': 800,
    'text-anchor': 'middle',
    'letter-spacing': '1.3px', 'text-transform': 'uppercase',
    text: text,
  }));
}
```

## 8. 가로 bar (per-class AP@50 류)

```js
function drawHBar({x, y, w, h, fillRatio, color, label, value}) {
  // bg (track)
  $content.appendChild(svg('rect', {
    x, y, width: w, height: h, rx: 4,
    fill: 'var(--bg-2)', stroke: 'var(--line)',
  }));
  // fill
  const fillW = Math.max(0.005, Math.min(1.0, fillRatio)) * w;
  $content.appendChild(svg('rect', {
    x, y, width: fillW, height: h, rx: 4,
    fill: color, opacity: 0.85,
  }));
  // value text (bar 안 우측 끝)
  $content.appendChild(svg('text', {
    x: x + fillW - 8, y: y + h / 2 + 5,
    'text-anchor': 'end',
    fill: '#0b0f1a', 'font-size': 14, 'font-weight': 800,
    'font-family': "'JetBrains Mono', ui-monospace, monospace",
    text: value,
  }));
}
```

## 9. 흡수 출처

- **playground/templates/code-map.md** — 노드/엣지/connection marker 패턴
- **cobot2 architecture-playground.html** — svg() helper (L964~968), drawCard (L2651~2654), drawSectionHeader 패턴 (L120~198 CSS + 4023~4032 사용)
