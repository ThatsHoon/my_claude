# Timeline History — 가로 5단 진화 타임라인

> 시간/버전별 변화를 가로로 나열. cobot2 의 Training History 탭 (v6→v10) 이 이 형태.

## 좌표

```
y=0
├─ y=0~70       Title
├─ y=80~190     Timeline cards row (5 카드, 각 244 px, gap 10)
├─ y=190~210    점선 연결 + dot
├─ y=210~720    상세 컨테이너 row (5 카드, 동일 width)
y=742
```

## 데이터 스키마

```js
const TAB_HISTORY = {
  subtitle: 'TRAINING HISTORY · v6 → v10',
  title: 'fitness 0.6496 → 0.9335 · 시행착오 3건',

  versions: [
    {
      v: 'v6', date: '0507', model: 'yolov8s', fitness: 0.6496, status: 'first',
      change: '최초 정착',
      details: ['yolov8s.pt baseline', '8-class', 'default hyper'],
      delta: ['fitness 0.6496', 'baseline 설정'],
      lesson: 'baseline 확립',
    },
    // ... v7 ~ v10
  ],
};
```

## 색 매핑 (그라데이션)

```js
const statusColor = {
  first:    '#dc2626',  // deep red
  baseline: '#ea580c',  // red-orange
  fail:     '#f97316',  // orange
  success:  '#fb923c',  // light orange
  best:     '#22c55e',  // green (특별)
};
```

## 렌더 코드

```js
function renderHistory() {
  clear($content);
  const H = TAB_HISTORY;

  // Title
  $content.appendChild(svg('text', {
    class: 'flow-title-sub', x: 30, y: 24, text: H.subtitle,
  }));
  $content.appendChild(svg('text', {
    class: 'flow-title-text', x: 30, y: 56, text: H.title,
  }));

  // Timeline row (5 cards, y=80~190)
  const tlY = 80, tlH = 110, tlGap = 10;
  const N = H.versions.length;
  const tlCardW = (1260 - tlGap * (N - 1)) / N;

  // 연결선 (점선)
  $content.appendChild(svg('line', {
    x1: 30 + tlCardW / 2, y1: tlY + tlH + 12,
    x2: 30 + (N - 1) * (tlCardW + tlGap) + tlCardW / 2, y2: tlY + tlH + 12,
    stroke: 'var(--line-2)', 'stroke-width': 1.4, 'stroke-dasharray': '4 4',
  }));

  H.versions.forEach((v, i) => {
    const x = 30 + i * (tlCardW + tlGap);
    const c = statusColor[v.status];
    const isBest = v.status === 'best';

    // timeline 카드
    $content.appendChild(svg('rect', {
      x, y: tlY, width: tlCardW, height: tlH, rx: 10,
      fill: isBest ? 'rgba(34, 197, 94, 0.10)' : 'var(--bg-3)',
      stroke: c, 'stroke-width': isBest ? 2.2 : 1.4,
      filter: 'drop-shadow(0 2px 6px rgba(0,0,0,0.35))',
    }));
    // dot on connector
    $content.appendChild(svg('circle', {
      cx: x + tlCardW / 2, cy: tlY + tlH + 12, r: 5,
      fill: c, stroke: 'var(--bg)', 'stroke-width': 2,
    }));
    // version label
    $content.appendChild(svg('text', {
      x: x + 14, y: tlY + 22,
      fill: c, 'font-size': 16, 'font-weight': 800,
      'font-family': "'JetBrains Mono', ui-monospace, monospace",
      text: v.v,
    }));
    // fitness (큰)
    $content.appendChild(svg('text', {
      x: x + 14, y: tlY + 78,
      fill: 'var(--text)', 'font-size': 24, 'font-weight': 800,
      text: v.fitness.toFixed(4),
    }));
  });

  // 상세 컨테이너 row (y=210~720)
  const vcY = 210, vcH = 510, vcCardW = tlCardW, vcGap = tlGap;
  H.versions.forEach((v, i) => {
    const x = 30 + i * (vcCardW + vcGap);
    const c = statusColor[v.status];

    // 연결 점선 (timeline dot → 상세 카드)
    $content.appendChild(svg('line', {
      x1: x + vcCardW / 2, y1: tlY + tlH + 18,
      x2: x + vcCardW / 2, y2: vcY,
      stroke: c, 'stroke-width': 1, 'stroke-dasharray': '3 3', opacity: 0.45,
    }));

    // 카드
    $content.appendChild(svg('rect', {
      x, y: vcY, width: vcCardW, height: vcH, rx: 12,
      fill: 'var(--bg-3)', stroke: c, 'stroke-opacity': 0.5, 'stroke-width': 1.4,
      filter: 'drop-shadow(0 2px 8px rgba(0,0,0,0.4))',
    }));
    // top strip
    $content.appendChild(svg('rect', {
      x: x + 1.5, y: vcY + 1.5, width: vcCardW - 3, height: 5, rx: 2,
      fill: c,
    }));

    // 변경 타이틀
    $content.appendChild(svg('text', {
      x: x + 16, y: vcY + 58,
      fill: 'var(--text)', 'font-size': 14, 'font-weight': 800,
      text: v.change,
    }));

    // 변경 상세
    $content.appendChild(svg('text', {
      x: x + 16, y: vcY + 100,
      fill: c, 'font-size': 10, 'font-weight': 800,
      'letter-spacing': '1.3px', 'text-transform': 'uppercase',
      text: '변경 상세',
    }));
    let dy = vcY + 122;
    v.details.forEach(d => {
      $content.appendChild(svg('text', {
        x: x + 16, y: dy,
        fill: 'var(--text)', 'font-size': 12,
        text: '· ' + d,
      }));
      dy += 22;
    });

    // 결과
    $content.appendChild(svg('text', {
      x: x + 16, y: vcY + 292,
      fill: c, 'font-size': 10, 'font-weight': 800,
      'letter-spacing': '1.3px', 'text-transform': 'uppercase',
      text: '결과',
    }));
    let ry = vcY + 316;
    v.delta.forEach(d => {
      $content.appendChild(svg('text', {
        x: x + 16, y: ry,
        fill: 'var(--text)', 'font-size': 13, 'font-weight': 700,
        text: d,
      }));
      ry += 20;
    });

    // 교훈
    $content.appendChild(svg('text', {
      x: x + 16, y: vcY + 442,
      fill: c, 'font-size': 10, 'font-weight': 800,
      'letter-spacing': '1.3px', 'text-transform': 'uppercase',
      text: '교훈',
    }));
    $content.appendChild(svg('text', {
      x: x + 16, y: vcY + 466,
      fill: 'var(--text)', 'font-size': 12, 'font-style': 'italic',
      text: v.lesson,
    }));
  });
}
```

## 변형

- **3 단** (작은 N) — 카드 width 408
- **5 단** (cobot2 기본) — 카드 width 244
- **7 단** (최대) — 카드 width 165, details/lesson 매우 짧게
- **status 색 없이** 모두 동일 액센트 — 단순 시간순 진화

## 언제 쓰나

- 버전 진화 (v1 → vN)
- 실패와 성공의 시행착오 추적
- 프로젝트 마일스톤 타임라인
- before/after 의 N 단 점진 변화
