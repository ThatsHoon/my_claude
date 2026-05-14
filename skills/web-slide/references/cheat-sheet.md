# Cheat Sheet — 한 페이지 빠른 참조

## 컨테이너 디자인 (필수)

- **직각 사각형** — `border-radius: 0` + 모든 `rx: 0` (SVG rect/chip 포함)
- **다크 배경** — `background: var(--bg-2)` (#131826 톤). light 카드 금지
- raw light hex (`#F4F2EC`, `#1a1a1a` 등) **금지** — CSS 변수만 사용
- **viewBox 는 반드시 `0 0 1320 742` (16:9 strict)** — modifier 로 비율 깨면 안 됨
- **글씨 크기 하한**: 카드 본문 12px, 카드 제목 14px, label 10px. 11px 이하는 footer/메타에만
- **emoji 금지** — 브랜드/기술 스택은 simple-icons SVG 또는 lucide 사용
- **슬라이드 영역 1500+** — 우측 메타/사이드 패널 두지 말 것 (메타는 슬라이드 안 footer strip 으로 통합)
- **카드 padding 16-22** — 12px 사용 금지
- **SVG element 충돌 자동 검사** — 다이어그램류 슬라이드는 detectSvgOverlap() 0 확인 (§5.12)
- **사이드바 prefix 중복 검사** — Training/Training Result 처럼 같은 prefix 있으면 역할 분리 (§5.10)
- **작업 종료 8단계 체크** — viewBox/aspect/hex/emoji/overlap/prefix/letterbox/validator 모두 통과 (§7.4)
- **콘텐츠 bbox ≥ viewBox 90%** — viewBox 만 16:9 가 아니라 콘텐츠도 viewBox 채움. 빈공간은 footer strip 으로 (§5.13)
- **슬라이드 vs 코드 진실성** — 노드/토픽/스키마 이름은 코드 grep 결과에서 복사. 추측 금지 (§5.15)
- **TOC 압축 — 단일 도메인 통합** — 사이드바 prefix 같은 슬라이드는 라벨 명확화 + button 1개만 활성 + TAB_ORDER 동기 (§5.16)
- **위반 자동 grep — 작업 종료 직전 강제** — viewBox/emoji/hex/modifier 4 grep 모두 0 라인 통과 후 완료 보고 (§5.17)
- 자세히 `SKILL.md §5.1 ~ §5.17 + §6 + §7`

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
