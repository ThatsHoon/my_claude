# Architecture Diagram — 노드 + 엣지 시스템 구조도

> 시스템 구성 요소들의 관계 시각화. cobot2 의 "시스템 노드 구조" 탭이 이 형태.

## 좌표 / 레이아웃 패턴

```
y=0
├─ y=0~80      Title
├─ y=90~720    Diagram canvas (1260 × 630)
│  └─ Lanes (수평 그룹) 또는 layers (수직 그룹)
│  └─ Nodes (사각 카드)
│  └─ Edges (직선 / Manhattan)
│  └─ Labels (엣지 위 라벨)
└─ y=720~742   Legend (선택)
y=742
```

## 데이터 스키마

```js
const TAB_SYSTEM = {
  subtitle: 'SYSTEM ARCHITECTURE',
  title: '실시간 객체 인식 + 협동 로봇 시스템',

  // Lanes (수평 그룹) — 선택
  lanes: [
    { x: 30, y: 100, w: 600, h: 280, title: '서브 PC', layer: 1 },
    { x: 660, y: 100, w: 600, h: 280, title: '메인 PC', layer: 2 },
  ],

  // Nodes
  nodes: [
    { id: 'mic',     x: 60,  y: 140, w: 140, h: 60, label: 'microphone',  layer: 1 },
    { id: 'stt',     x: 240, y: 140, w: 160, h: 60, label: 'STT (Whisper)', layer: 1 },
    { id: 'gpt',     x: 440, y: 140, w: 160, h: 60, label: 'GPT-4o',     layer: 1 },
    { id: 'bt',      x: 690, y: 140, w: 160, h: 60, label: 'bt_manager', layer: 2 },
    { id: 'robot',   x: 880, y: 140, w: 160, h: 60, label: 'doosan m0609', layer: 2 },
  ],

  // Edges
  edges: [
    { from: 'mic',  to: 'stt',   topic: '/audio_raw' },
    { from: 'stt',  to: 'gpt',   topic: '/stt_result' },
    { from: 'gpt',  to: 'bt',    topic: '/voice_command' },
    { from: 'bt',   to: 'robot', topic: '/execute_command' },
  ],
};
```

## 렌더 코드

```js
function renderSystem() {
  clear($content);
  const T = TAB_SYSTEM;

  // Title
  $content.appendChild(svg('text', {
    class: 'flow-title-sub', x: 30, y: 24, text: T.subtitle,
  }));
  $content.appendChild(svg('text', {
    class: 'flow-title-text', x: 30, y: 56, text: T.title,
  }));

  // Lanes (group bg)
  const layerColors = ['', 'var(--layer-1)', 'var(--layer-2)',
                       'var(--layer-3)', 'var(--layer-4)'];
  T.lanes.forEach(lane => {
    const c = layerColors[lane.layer];
    $content.appendChild(svg('rect', {
      x: lane.x, y: lane.y, width: lane.w, height: lane.h, rx: 8,
      fill: 'transparent', stroke: c, 'stroke-opacity': 0.4,
      'stroke-width': 1, 'stroke-dasharray': '4 4',
    }));
    $content.appendChild(svg('text', {
      x: lane.x + 12, y: lane.y - 6,
      fill: c, 'font-size': 11, 'font-weight': 700,
      'letter-spacing': '1.3px', 'text-transform': 'uppercase',
      text: lane.title,
    }));
  });

  // Edges (먼저 그려서 노드가 위에 오게)
  const nodeById = Object.fromEntries(T.nodes.map(n => [n.id, n]));
  T.edges.forEach(e => {
    const from = nodeById[e.from], to = nodeById[e.to];
    const x1 = from.x + from.w, y1 = from.y + from.h / 2;
    const x2 = to.x,            y2 = to.y + to.h / 2;
    $content.appendChild(svg('line', {
      x1, y1, x2, y2,
      stroke: 'var(--text-3)', 'stroke-width': 1.5,
      'marker-end': 'url(#ah-system)',
    }));
    // 라벨 (중간)
    $content.appendChild(svg('text', {
      x: (x1 + x2) / 2, y: (y1 + y2) / 2 - 6,
      fill: 'var(--text-3)', 'font-size': 9,
      'text-anchor': 'middle',
      'font-family': "'JetBrains Mono', ui-monospace, monospace",
      text: e.topic,
    }));
  });

  // Nodes
  T.nodes.forEach(n => {
    const c = layerColors[n.layer];
    // bg
    $content.appendChild(svg('rect', {
      x: n.x, y: n.y, width: n.w, height: n.h, rx: 8,
      fill: 'var(--bg-3)', stroke: c, 'stroke-width': 1.4,
      filter: 'drop-shadow(0 2px 6px rgba(0,0,0,0.35))',
    }));
    // top strip
    $content.appendChild(svg('rect', {
      x: n.x + 1.5, y: n.y + 1.5, width: n.w - 3, height: 4, rx: 2,
      fill: c,
    }));
    // label
    $content.appendChild(svg('text', {
      x: n.x + n.w / 2, y: n.y + n.h / 2 + 5,
      'text-anchor': 'middle',
      fill: 'var(--text)', 'font-size': 13, 'font-weight': 700,
      text: n.label,
    }));
  });
}
```

## 변형

- **Manhattan / L-shape edges** — `<path d="M x1 y1 L x1 yMid L x2 yMid L x2 y2"/>` 로 직각 꺽임
- **Edge bundling** — 같은 from→to 의 여러 토픽을 1 line + stacked label 로
- **Sub-graphs** — 색별 그룹 (서브 PC = purple, 메인 PC = teal, Docker = orange)
- **Hover/click 하이라이트** — JavaScript event 로 관련 엣지 강조
- **Legend** — 우하단에 색 → 의미 매핑

## 언제 쓰나

- "이 시스템은 어떻게 연결되는가?"
- ROS 노드 그래프, 마이크로서비스 다이어그램, 데이터 흐름
- multi-PC / multi-container 분산 시스템

## 흡수 출처

- **playground/templates/code-map.md** — 노드/엣지 mapping 패턴
- **cobot2 architecture-playground.html** L596~879 — 7 SVG view 중 system 탭의 노드/엣지/lanes 패턴
