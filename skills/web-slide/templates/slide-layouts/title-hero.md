# Title Hero — 풀-블리드 타이틀 슬라이드

> 첫 슬라이드용. 큰 제목 + 짧은 tagline + 3~5 bullet. 가장 단순.

## 좌표

```
y=0
├─ y=0~80      Sub-title (UPPERCASE 라벨)
├─ y=90~180    Main title (큰 글씨)
├─ y=200~280   Tagline (한 줄 강조)
├─ y=320~580   Bullets / accent box
└─ y=620~720   Footer / meta info
y=742
```

## 데이터 스키마

```js
const TAB_OVERVIEW = {
  subtitle: 'PROJECT ALPHA',
  title: '실시간 객체 인식 + 협동 로봇 시스템',
  tagline: '음성 명령으로 7-class 객체를 잡고 옮긴다',
  bullets: [
    'YOLO11s · 7-class detection · 99% mAP@50',
    'Doosan m0609 협동 로봇 · ROS 2 Humble',
    '3 PC 분산 (메인/서브/Docker) · WebSocket UI',
    'BehaviorTree.CPP 명령 오케스트레이션',
  ],
  meta: '2026.05 · cobot2 project',
};
```

## 렌더 코드

```js
function renderOverview() {
  clear($content);
  const T = TAB_OVERVIEW;

  // Sub-title
  $content.appendChild(svg('text', {
    class: 'flow-title-sub', x: 30, y: 50,
    fill: 'var(--accent)', text: T.subtitle,
  }));

  // Main title (큰)
  $content.appendChild(svg('text', {
    x: 30, y: 140,
    fill: 'var(--text)', 'font-size': 56, 'font-weight': 800,
    'letter-spacing': '-1px',
    text: T.title,
  }));

  // Tagline
  $content.appendChild(svg('text', {
    x: 30, y: 240,
    fill: 'var(--text-2)', 'font-size': 20, 'font-weight': 500,
    text: T.tagline,
  }));

  // Bullets — 큰 카드 안
  $content.appendChild(svg('rect', {
    x: 30, y: 320, width: 1260, height: 280, rx: 12,
    fill: 'var(--bg-3)', stroke: 'var(--line-2)', 'stroke-width': 1.2,
    filter: 'drop-shadow(0 2px 8px rgba(0,0,0,0.4))',
  }));
  $content.appendChild(svg('rect', {
    x: 31.5, y: 321.5, width: 1257, height: 5, rx: 2,
    fill: 'var(--accent)',
  }));

  T.bullets.forEach((b, i) => {
    // 점
    $content.appendChild(svg('circle', {
      cx: 60, cy: 380 + i * 50, r: 4,
      fill: 'var(--accent)',
    }));
    // 텍스트
    $content.appendChild(svg('text', {
      x: 80, y: 386 + i * 50,
      fill: 'var(--text)', 'font-size': 18, 'font-weight': 500,
      text: b,
    }));
  });

  // Meta footer
  $content.appendChild(svg('text', {
    x: 30, y: 700,
    fill: 'var(--text-3)', 'font-size': 11,
    'font-family': "'JetBrains Mono', ui-monospace, monospace",
    text: T.meta,
  }));
}
```

## 변형

- **Bullets 대신 large image** — `<image>` 또는 hero illustration (300×300) 우측에 배치
- **Tagline 없이** title 만 더 크게 (font-size: 72)
- **gradient 배경** — `<defs>` 안에 linearGradient 정의 후 `fill="url(#gradient)"`

## 언제 쓰나

- Deck 의 첫 슬라이드 (intro)
- "What is X?" 형 단순 정의 슬라이드
- 카테고리 구분용 transition 슬라이드
