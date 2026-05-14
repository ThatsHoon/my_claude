# Metric Cards — N 개 KPI pills + bar chart

> 성능 지표를 한눈에. cobot2 의 Training Result 탭 (8 pills + per-class bar) 이 이 형태.

## 좌표

```
y=0
├─ y=0~80      Title
├─ y=90~200    Hero pills row (N pills, 균등 분할)
├─ y=210~720   상세 (bar chart / table / 카드)
y=742
```

## 데이터 스키마

```js
const TAB_METRICS = {
  subtitle: 'TRAINING RESULT · BEST CHECKPOINT',
  title: 'YOLO11s · 7-CLASS DETECTION',
  metaStrip: '9.4M params · 21.5 GFLOPs · 1355 imgs',

  // Hero pills (N=4~10 권장)
  pills: [
    { label: 'mAP@50',     value: '99.0%',  sub: '0.9901',  color: '#2dd4bf', big: true },
    { label: 'mAP@50-95',  value: '92.7%',  sub: '0.9272',  color: '#2dd4bf' },
    { label: 'F1',         value: '96.8%',  sub: '0.9682',  color: '#22d3ee' },
    { label: 'Precision',  value: '96.9%',  sub: '0.9689',  color: '#22d3ee' },
    { label: 'Recall',     value: '96.7%',  sub: '0.9674',  color: '#22d3ee' },
    { label: 'Center err', value: '4.3px',  sub: 'GT↔pred', color: '#fbbf24', highlight: true },
    { label: 'FPS',        value: '181.6',  sub: 'V100',    color: '#a78bfa' },
    { label: 'Fitness',    value: '0.9335', sub: 'best',    color: '#fb923c' },
  ],

  // Per-class / 상세 bars
  perClass: [
    { name: 'shaker',    value: 0.9950 },
    { name: 'toy_block', value: 0.9947 },
    // ...
  ],
};
```

## 렌더 코드

```js
function renderMetrics() {
  clear($content);
  const M = TAB_METRICS;

  // Title
  $content.appendChild(svg('text', {
    class: 'flow-title-sub', x: 30, y: 24, text: M.subtitle,
  }));
  $content.appendChild(svg('text', {
    class: 'flow-title-text', x: 30, y: 54, text: M.title,
  }));
  $content.appendChild(svg('text', {
    class: 'flow-section-desc', x: 30, y: 72, text: M.metaStrip,
  }));

  // Hero pills (균등 분할)
  const heroY = 90, pillH = 96, pillGap = 8;
  const N = M.pills.length;
  const pillW = (1260 - pillGap * (N - 1)) / N;
  M.pills.forEach((p, i) => {
    const x = 30 + i * (pillW + pillGap);
    // bg
    $content.appendChild(svg('rect', {
      x, y: heroY, width: pillW, height: pillH, rx: 10,
      fill: p.highlight ? 'rgba(251, 191, 36, 0.08)' : 'var(--bg-3)',
      stroke: p.color, 'stroke-width': p.big || p.highlight ? 2.2 : 1.4,
      filter: 'drop-shadow(0 2px 6px rgba(0,0,0,0.35))',
    }));
    // label
    $content.appendChild(svg('text', {
      x: x + pillW / 2, y: heroY + 20,
      fill: p.color, 'font-size': 10, 'font-weight': 800,
      'text-anchor': 'middle',
      'letter-spacing': '1.5px', 'text-transform': 'uppercase',
      text: p.label,
    }));
    // value (큰)
    $content.appendChild(svg('text', {
      x: x + pillW / 2, y: heroY + 56,
      fill: 'var(--text)', 'font-size': p.big ? 28 : 24, 'font-weight': 800,
      'text-anchor': 'middle',
      text: p.value,
    }));
    // sub
    $content.appendChild(svg('text', {
      x: x + pillW / 2, y: heroY + 80,
      fill: 'var(--text-3)', 'font-size': 10,
      'text-anchor': 'middle',
      'font-family': "'JetBrains Mono', ui-monospace, monospace",
      text: p.sub,
    }));
  });

  // Bar chart (per-class)
  const chartX = 30, chartY = 230, chartW = 1260, chartH = 480;
  $content.appendChild(svg('rect', {
    x: chartX, y: chartY, width: chartW, height: chartH, rx: 12,
    fill: 'var(--bg-3)', stroke: 'var(--line-2)', 'stroke-width': 1.2,
    filter: 'drop-shadow(0 2px 8px rgba(0,0,0,0.4))',
  }));
  $content.appendChild(svg('text', {
    class: 'flow-section-label', x: chartX + 22, y: chartY + 32,
    fill: 'var(--accent)', text: 'PER-CLASS PERFORMANCE',
  }));

  // bars
  const barAreaX = chartX + 140, barAreaW = chartW - 160;
  const barH = 38, barGap = 8;
  const barStartY = chartY + 70;
  M.perClass.forEach((c, i) => {
    const by = barStartY + i * (barH + barGap);
    // class name
    $content.appendChild(svg('text', {
      x: chartX + 132, y: by + barH / 2 + 5,
      'text-anchor': 'end',
      fill: 'var(--text)', 'font-size': 13, 'font-weight': 700,
      'font-family': "'JetBrains Mono', ui-monospace, monospace",
      text: c.name,
    }));
    // track
    $content.appendChild(svg('rect', {
      x: barAreaX, y: by, width: barAreaW, height: barH, rx: 4,
      fill: 'var(--bg-2)', stroke: 'var(--line)',
    }));
    // fill
    const fillW = Math.max(0.005, Math.min(1.0, c.value)) * barAreaW;
    $content.appendChild(svg('rect', {
      x: barAreaX, y: by, width: fillW, height: barH, rx: 4,
      fill: 'var(--accent)', opacity: 0.85,
    }));
    // value text
    $content.appendChild(svg('text', {
      x: barAreaX + fillW - 8, y: by + barH / 2 + 5,
      'text-anchor': 'end',
      fill: '#0b0f1a', 'font-size': 14, 'font-weight': 800,
      'font-family': "'JetBrains Mono', ui-monospace, monospace",
      text: (c.value * 100).toFixed(2) + '%',
    }));
  });
}
```

## 변형

- **Pills row + 2-column** (chart + dataset) — cobot2 Training Result 가 이 형태
- **Pills row + 3-column** — chart 더 작게 + 양옆에 sub 정보
- **Pills 만** (큰 슬라이드) — pills 가 메인, 차트 없음
- **Pills 없이 chart 만** — full-bleed bar chart 또는 line chart
- **N pills**: 4 / 6 / 8 / 10 가능. 8 권장 (가독성)

## Pill 강조 4 종류

| 옵션 | 시각 | 용도 |
|---|---|---|
| 기본 | stroke 1.4 px | 일반 metric |
| `big: true` | stroke 2.2 px + value font 28 | 핵심 metric (mAP@50 등) |
| `highlight: true` | bg amber tint + stroke 2.2 | 매우 중요 (center_err 등) |
| `color`별로 다름 | 색으로 grouping | accuracy / speed / 종합 |

## 언제 쓰나

- 머신러닝 / AI 모델 결과
- 시스템 성능 KPI 대시보드
- A/B 테스트 결과 비교
- 비즈니스 metric 요약
