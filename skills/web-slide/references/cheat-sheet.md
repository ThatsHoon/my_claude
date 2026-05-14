# Cheat Sheet — 한 페이지 빠른 참조

## viewBox + 마진

```
viewBox="0 0 1320 742"     preserveAspectRatio="xMidYMin meet"
유효 영역: x 30~1290 (w 1260), y 30~712 (h 682)
```

## N-column 분할 (gap 14, 유효폭 1260)

| N | colW | 용도 |
|---|---|---|
| 2 | 623 | 좌/우 |
| 3 | 410 | feature |
| 4 | 301 | grid |
| 5 | 244 | timeline 5단 |
| 8 | 142 | KPI pills |

## 토큰

`var(--bg)` `var(--bg-2)` `var(--bg-3)` `var(--text)` `var(--text-2)` `var(--text-3)` `var(--line)` `var(--line-2)` `var(--accent)` `var(--layer-1..4)`

## 폰트 크기

| 용도 | px |
|---|---|
| 슬라이드 제목 | 22, weight 800 |
| Sub-title (UPPERCASE) | 10.5, JetBrains Mono |
| 섹션 번호 (01, 02) | 56 Georgia italic, opacity 0.18 |
| 섹션 라벨 (UPPERCASE) | 12, weight 700, letter-spacing 1.3 |
| 본문 | 12~14 |
| 큰 KPI 값 | 24~32, weight 800 |
| 작은 메타 | 9~10 |

한글 라벨은 +1~2 px 보정.

## 카드 4요소 (드롭섀도우 카드)

```js
svg('rect', { x, y, width, height, rx: 12,
  fill: 'var(--bg-3)', stroke: 'var(--line-2)',
  'stroke-width': 1.4,
  filter: 'drop-shadow(0 2px 8px rgba(0,0,0,0.4))' });
svg('rect', { x: x+1.5, y: y+1.5, width: w-3, height: 5, rx: 2, fill: color });  // top strip
svg('line', { x1: x+16, y1: dividerY, x2: x+w-16, y2: dividerY,
  stroke: 'var(--line)', 'stroke-dasharray': '2 3' });  // dashed divider
```

## 새 탭 6 위치 (`scripts/new-slide-tab.sh` 자동, 또는 수동)

1. `<button class="tab" data-view="X">`
2. `<div class="view view-X"><svg><g id="X-content">`
3. `switchView` if-chain → `else if (view === 'X') renderX();`
4. `applyTheme` if-chain → `else if (state.view === 'X') renderX();`
5. `const TAB_X = {...}` 데이터 객체
6. `function renderX() { clear($Xc); ... }`

## scaffold (한 줄 자동 생성)

```bash
node ~/.claude/skills/web-slide/scripts/scaffold.mjs \
  /tmp/myproject.html "My Project" \
  overview:title-hero arch:architecture-diagram metrics:metric-cards
```

## validate (한 줄 검증)

```bash
node ~/.claude/skills/web-slide/scripts/validate-slide.mjs <file.html>
```

검사: viewBox 1320×742 / 5-way diff / rect+text 마진 / 데이터-render 동기 (heuristic).

## 자주 쓰는 패턴

| 패턴 | layout md |
|---|---|
| 인트로 / 단일 제목 | title-hero |
| 3 카테고리 | 3-column |
| 노드 그래프 | architecture-diagram |
| 버전 진화 5단 | timeline-history |
| KPI + bar chart | metric-cards |
| 시간순 단계 흐름 | sequence-diagram |

## 키보드 단축키 (multi-tab-shell)

- `←` `→` : 탭 이동
- `T` : 테마 토글

## 인쇄 / PDF export

브라우저 → `Cmd+P` → "Save as PDF". `@media print` 가 헤더/탭 숨김, 모든 슬라이드를 page-break 으로 분리.

## 함정 5개 (자세히는 `references/pitfalls.md`)

1. switchView / applyTheme 양분기 누락 → validator 검출
2. SVG text 자동 wrap 없음 → `wrapSvgText()` 사용
3. 마진 30~1290 침범 → validator 검출
4. 한영 폰트 사이즈 불균형 → 한글 +1~2 px
5. 데이터-render 동기 누락 → validator heuristic 경고
