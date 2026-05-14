# Sequence Diagram — 시간순 N 단계 흐름

> 음성 명령 → 로봇 동작 같은 step-by-step 시퀀스. cobot2 의 "명령 시퀀스 흐름" 탭이 이 형태.

## 좌표

```
y=0
├─ y=0~80      Title
├─ y=90~200    Actors / Lanes (가로 N 개 actor)
├─ y=210~660   Steps (수직 시간순 흐름, actor 간 화살표)
└─ y=680~720   Timeline ticks (선택)
y=742
```

또는 가로 N 단계:
```
y=0
├─ y=0~80      Title
├─ y=100~300   Step cards (가로 N 개, 가운데 화살표)
├─ y=320~700   각 step 상세 (cards 또는 timeline)
y=742
```

## 데이터 스키마

```js
const TAB_FLOW = {
  subtitle: 'COMMAND SEQUENCE',
  title: '음성 발화 → 로봇 동작 (~6초)',

  // 가로 단계 카드
  steps: [
    { id: 1, label: 'CAPTURE',  actor: 'mic',          duration: '0.1s', color: '#a78bfa' },
    { id: 2, label: 'UNDERSTAND', actor: 'voice_to_cmd', duration: '1.2s', color: '#a78bfa' },
    { id: 3, label: 'DISPATCH', actor: 'bt_manager',   duration: '0.2s', color: '#2dd4bf' },
    { id: 4, label: 'PERCEIVE', actor: 'object_det',   duration: '0.3s', color: '#2dd4bf' },
    { id: 5, label: 'ACT',      actor: 'doosan',       duration: '4.2s', color: '#fb923c' },
  ],

  // 단계별 상세
  details: [
    { step: 1, text: '사용자 발화 → 마이크 → openwakeword' },
    { step: 2, text: 'Whisper STT → GPT-4o → JSON 시퀀스' },
    { step: 3, text: 'BehaviorTree.CPP 가 액션 분기' },
    { step: 4, text: 'YOLO11s + RealSense → 3D 위치' },
    { step: 5, text: 'movej / movel / gripper 제어' },
  ],
};
```

## 렌더 코드 (가로 단계 + 화살표)

```js
function renderFlow() {
  clear($content);
  const F = TAB_FLOW;

  // Title
  $content.appendChild(svg('text', {
    class: 'flow-title-sub', x: 30, y: 24, text: F.subtitle,
  }));
  $content.appendChild(svg('text', {
    class: 'flow-title-text', x: 30, y: 56, text: F.title,
  }));

  // Step cards (가로) — y=100~280
  const stY = 100, stH = 180;
  const N = F.steps.length;
  const stGap = 12;
  const arrowW = 30;
  const totalArrowW = (N - 1) * arrowW;
  const stCardW = (1260 - totalArrowW - stGap * (N - 1)) / N;
  let curX = 30;

  F.steps.forEach((s, i) => {
    // card
    $content.appendChild(svg('rect', {
      x: curX, y: stY, width: stCardW, height: stH, rx: 12,
      fill: 'var(--bg-3)', stroke: s.color, 'stroke-width': 1.4,
      filter: 'drop-shadow(0 2px 8px rgba(0,0,0,0.4))',
    }));
    // top strip
    $content.appendChild(svg('rect', {
      x: curX + 1.5, y: stY + 1.5, width: stCardW - 3, height: 5, rx: 2,
      fill: s.color,
    }));
    // step number (큰)
    $content.appendChild(svg('text', {
      x: curX + 18, y: stY + 50,
      fill: s.color, 'font-size': 36, 'font-weight': 800,
      'font-family': 'Georgia, serif', 'font-style': 'italic',
      text: String(s.id).padStart(2, '0'),
    }));
    // label
    $content.appendChild(svg('text', {
      x: curX + 18, y: stY + 84,
      fill: 'var(--text)', 'font-size': 14, 'font-weight': 800,
      'letter-spacing': '1.4px', 'text-transform': 'uppercase',
      text: s.label,
    }));
    // actor
    $content.appendChild(svg('text', {
      x: curX + 18, y: stY + 110,
      fill: 'var(--text-2)', 'font-size': 12,
      'font-family': "'JetBrains Mono', ui-monospace, monospace",
      text: s.actor,
    }));
    // duration
    $content.appendChild(svg('text', {
      x: curX + stCardW - 18, y: stY + stH - 16,
      'text-anchor': 'end',
      fill: 'var(--text-3)', 'font-size': 11, 'font-weight': 700,
      'font-family': "'JetBrains Mono', ui-monospace, monospace",
      text: s.duration,
    }));

    // 다음 단계로의 화살표 (마지막 제외)
    if (i < N - 1) {
      const ax = curX + stCardW + stGap;
      const ay = stY + stH / 2;
      $content.appendChild(svg('line', {
        x1: ax, y1: ay, x2: ax + arrowW - 4, y2: ay,
        stroke: 'var(--text-3)', 'stroke-width': 2,
        'marker-end': 'url(#ah-flow)',
      }));
    }

    curX += stCardW + (i < N - 1 ? stGap + arrowW : 0);
  });

  // 상세 (수직 list, y=320~700)
  F.details.forEach((d, i) => {
    const dy = 320 + i * 70;
    const step = F.steps[d.step - 1];
    // 좌측 번호 chip
    $content.appendChild(svg('circle', {
      cx: 60, cy: dy + 24, r: 16,
      fill: step.color, 'fill-opacity': 0.15,
      stroke: step.color, 'stroke-width': 1.5,
    }));
    $content.appendChild(svg('text', {
      x: 60, y: dy + 30, 'text-anchor': 'middle',
      fill: step.color, 'font-size': 14, 'font-weight': 800,
      text: String(d.step).padStart(2, '0'),
    }));
    // text
    $content.appendChild(svg('text', {
      x: 90, y: dy + 30,
      fill: 'var(--text)', 'font-size': 16, 'font-weight': 600,
      text: d.text,
    }));
  });
}
```

**필수**: `<defs>` 에 `<marker id="ah-flow" ...>` 화살촉 정의.

## 변형

- **N=3** : 시작/중간/끝
- **N=5** : capture/understand/dispatch/perceive/act (cobot2)
- **N=7** : 더 미세한 단계 (각 카드 작음)
- **수직 sequence** : actor 가 가로, time 이 세로 (UML sequence diagram 형태)
- **parallel flow** : 메인 흐름 + 병렬 flow (TTS, DB 로깅 등)
- **timeline tick** : 하단에 시간축 0s / 1s / 2s / ...

## 언제 쓰나

- "X 가 어떻게 동작하는가" 의 step-by-step
- 음성 → 모델 → 로봇 같은 cross-system 흐름
- HTTP 요청 lifecycle, OAuth flow
- ML pipeline (data → train → eval → deploy)
- CI/CD 단계
