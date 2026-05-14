# 3-Column — 3 개 카테고리 / feature / metric 가로 분할

> 가장 자주 쓰는 레이아웃. cobot2 의 Training Result, 기술 스택 탭이 이 형태.

## 좌표

```
y=0
├─ y=0~80         Title block
├─ y=90~200       Hero / summary row (선택)
├─ y=210~720      3 columns (gap 14)
│  └─ col 1: x=30~440 (w=410)
│  └─ col 2: x=454~864 (w=410)
│  └─ col 3: x=878~1290 (w=410+12)
y=742
```

또는 비균등:
- col 1: w=380 (Dataset)
- col 2: w=280 (Techniques)
- col 3: w=608 (Per-class chart)

## 데이터 스키마

```js
const TAB_RESULT = {
  subtitle: 'TRAINING RESULT',
  title: 'YOLO11s · 7-class · mAP@50 99%',
  metaStrip: '9.4M params · 21.5 GFLOPs · 1355 imgs',

  // Hero pills (선택, y=90~200)
  pills: [
    { label: 'mAP@50',     value: '99.0%',  sub: '0.9901',  color: '#2dd4bf', big: true },
    { label: 'F1',         value: '96.8%',  sub: '0.9682',  color: '#22d3ee' },
    // ...
  ],

  // Columns (필수, y=210~720)
  columns: [
    { num: '01', label: 'DATASET',             color: 'var(--layer-2)', content: ... },
    { num: '02', label: 'LEARNING TECHNIQUES', color: 'var(--layer-1)', content: ... },
    { num: '03', label: 'PER-CLASS AP@50',     color: 'var(--layer-2)', content: ... },
  ],
};
```

## 렌더 코드 (카드 그리기)

```js
function renderResult() {
  clear($content);
  const T = TAB_RESULT;

  // Title
  $content.appendChild(svg('text', {
    class: 'flow-title-sub', x: 30, y: 24, text: T.subtitle,
  }));
  $content.appendChild(svg('text', {
    class: 'flow-title-text', x: 30, y: 56, text: T.title,
  }));
  $content.appendChild(svg('text', {
    class: 'flow-section-desc', x: 30, y: 76, text: T.metaStrip,
  }));

  // 3-column
  const blockY = 210, blockH = 510, gap = 14;
  const widths = [380, 280, 608];  // 비균등 or [410, 410, 410]
  let x = 30;
  T.columns.forEach((col, i) => {
    drawColumn(x, blockY, widths[i], blockH, col);
    x += widths[i] + gap;
  });
}

function drawColumn(x, y, w, h, col) {
  // bg
  $content.appendChild(svg('rect', {
    x, y, width: w, height: h, rx: 12,
    fill: 'var(--bg-3)', stroke: 'var(--line-2)', 'stroke-width': 1.2,
    filter: 'drop-shadow(0 2px 8px rgba(0,0,0,0.4))',
  }));
  // top strip
  $content.appendChild(svg('rect', {
    x: x + 1.5, y: y + 1.5, width: w - 3, height: 5, rx: 2,
    fill: col.color,
  }));
  // section num (Georgia italic)
  $content.appendChild(svg('text', {
    class: 'flow-section-num', x: x + 18, y: y + 48,
    text: col.num,
  }));
  // label
  $content.appendChild(svg('text', {
    class: 'flow-section-label', x: x + 82, y: y + 30,
    fill: col.color, text: col.label,
  }));
  // accent line
  $content.appendChild(svg('line', {
    x1: x + 82, y1: y + 38, x2: x + 122, y2: y + 38,
    stroke: col.color, 'stroke-width': 2, 'stroke-linecap': 'round',
  }));

  // col.content() 호출하여 본문 그리기
  if (typeof col.content === 'function') col.content(x, y + 80, w, h - 90);
}
```

## 변형

- **3 균등** 컬럼 (각 410 px) — 사용 빈도 가장 높음
- **비균등** (예: 380/280/608) — 컬럼별 콘텐츠 밀도가 다를 때
- **Hero row 없이** 바로 3 column — y=90 부터 컬럼 시작
- **2-column** 변형 — 좌 800 / 우 430 같이 큰/작은 대비
- **4-column** — 각 301 px (gap 14) — KPI 카드 4개

## 언제 쓰나

- "이 시스템의 3가지 핵심 요소"
- 좌(input) / 중(process) / 우(output) 흐름
- 카테고리 비교 (Dataset / Techniques / Result)
- 기술 스택 (frontend / backend / infra)
