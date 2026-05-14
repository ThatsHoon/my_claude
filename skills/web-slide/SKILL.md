---
name: web-slide
description: Use when creating PPT-style 16:9 web slides as a single static self-contained HTML file — typically to explain a project architecture, system, workflow, training pipeline, or result deck across 1–7 tabs. Triggers on web slide, web slides, HTML slide deck, single-file presentation, 16:9 웹 슬라이드, architecture slide, project deck, training result deck, switchView/applyTheme 패턴, viewBox 1320 742, PPT-style HTML, 프로젝트 슬라이드, architecture 한 장. Also trigger on "한 장 슬라이드", "explainer HTML", "tab-based architecture explainer" when HTML output is implied. Do NOT use for .pptx files (route to pptx skill), reveal.js/marp/impress.js decks, or interactive playgrounds with live controls (route to playground skill).
---

# web-slide — PPT 스타일 16:9 웹 슬라이드 작성 스킬

> 단일 HTML 파일 안에 N 개 탭의 16:9 슬라이드를 작성. 각 탭은 PPT 한 장. 시각/타이포/컬러가 모든 탭에 통일됨.

기준 reference: `/home/hoon/cobot_ws/docs/cobot2/architecture-playground.html` (cobot2 로봇 음성 제어 시스템의 7-탭 PPT 슬라이드). 줄번호 색인은 `references/reference-example.md`.

---

## 1. When to use / not to use

**Use** (이 skill 트리거):
- 프로젝트/시스템/워크플로우 설명용 1~7 탭 단일 HTML
- 16:9 비율 슬라이드 (1320×742 픽셀 viewBox)
- 다크/라이트 테마 토글 필요
- 정적 HTML — 한 파일로 어디서나 열림

**Don't use** (다른 skill 으로 라우팅):
- `.pptx` 산출물 → **document-skills:pptx** (PptxGenJS / html2pptx)
- reveal.js / marp / impress.js 류 발표 도구
- 풀스크린 페이지가 아닌 일반 웹 컴포넌트 → **frontend-design**
- 정지 이미지(PNG/PDF) → **canvas-design**
- 인터랙티브 control + live preview tool → **playground**

---

## 2. Quick start (decision tree)

```
사용자 요청
  │
  ├─ 1 탭만? ───────────────→ templates/blank-slide.html 복사
  │
  ├─ 2~7 탭? ───────────────→ templates/multi-tab-shell.html 복사
  │
  └─ 레이아웃 이름 매칭? ───→ templates/slide-layouts/<X>.md 패턴 참조
                            (title-hero / 3-column / architecture-diagram /
                             timeline-history / metric-cards)
```

탭 8개 이상은 **거부** — `.tabs` 가로 공간이 부족함. 8 개 이상은 sub-section 으로 묶거나 2 deck 으로 분리 권장.

---

## 3. Workflow (6 단계)

1. **Scope 파악** — 사용자에게 (a) 탭 이름들 (b) 각 탭 한 줄 설명 (c) 메인 데이터/포커스 확인. 7 개 초과 시 분리 제안.

2. **Layout 매칭** — 각 탭마다 `templates/slide-layouts/*.md` 5종 중 1-2 개 선택. 결과는 표:
   | 탭 | 레이아웃 | 핵심 데이터 |
   |---|---|---|
   | overview | title-hero | tagline, key bullet |
   | system | architecture-diagram | nodes[], edges[] |
   | metrics | metric-cards | metrics[] (label/value/sub) |
   | history | timeline-history | versions[] (change, delta, lesson) |
   | result | 3-column | dataset / techniques / per-class |

3. **Theme 선택** — `references/themes.md` 의 10+1 옵션 중 선택. 사용자 선호 없으면 기본 **Modern Minimalist** (general) 또는 **Tech Innovation** (코드/엔지니어링). 모든 테마는 dark/light 양쪽 정의됨.

4. **Scaffold** — boilerplate 복사 → 토큰 치환:
   - `<title>` 변경
   - 탭 버튼 + view div + render 함수 stubs 추가
   - 토큰 CSS variables 교체 (선택된 theme 기준)
   - **검증**: 브라우저로 열어 모든 탭이 placeholder 라도 렌더되고 dark/light 토글이 동작하는지 확인. 이 단계 종료 시 함정 #1 (switchView/applyTheme 양분기) 이 잡혀 있어야 함.

5. **콘텐츠 채우기** — 탭별:
   - 데이터 객체 (`const TAB_X = {...}`) 정의
   - `renderTabX()` 함수 작성 — `svg('text', {x, y, text, ...})` helper 호출
   - SVG `<text>` 는 자동 wrap 없음 — `snippets/svg-text-wrap.js` 헬퍼 사용
   - 좌표는 `references/16-9-layout.md` 의 grid 가이드 따름 (1320 폭, 30 px 마진)

6. **검증**:
   - `node ~/.claude/skills/web-slide/scripts/validate-slide.mjs <file.html>` → exit 0
   - chrome-devtools-mcp 또는 브라우저로 모든 탭 클릭 + dark/light 토글 + 시각 오버플로우 확인
   - `references/pitfalls.md` 의 5개 함정 체크리스트

---

## 4. Layout grid (16:9 strict)

| 속성 | 값 |
|---|---|
| viewBox | `0 0 1320 742` (1320/742 = 1.779 ≈ 16/9) |
| preserveAspectRatio | `xMidYMin meet` |
| CSS aspect-ratio | `16 / 9` |
| CSS min-height | `742px` |
| 안쪽 마진 | 좌우/상하 30 px (= 유효폭 1260, 유효높이 682) |

자세한 픽셀 좌표 수학은 `references/16-9-layout.md`.

---

## 5. Color & typography (theme 시스템)

- 모든 색은 CSS variables 로 단일 출처 (`:root` + `[data-theme="light"]` 두 블록)
- 필수 토큰 세트: `--bg`, `--bg-2`, `--bg-3`, `--text`, `--text-2`, `--text-3`, `--accent`, `--line`
- SVG 내부에서 `fill="var(--accent)"` 사용. raw hex (`fill="#2dd4bf"`) **금지** (예외: `<defs>` 안 marker/gradient)
- 한영 혼용 시 한글이 영문 폰트보다 시각적으로 1-2 px 작게 보임 — 한글 라벨은 +1~2 px 보정
- 10+1 팔레트 카탈로그: `references/themes.md`

---

## 6. Adding a tab — 6 위치 동시 패치 (체크리스트)

새 탭 `X` 추가 시 반드시 6 위치 모두 편집:

| # | 위치 | 패치 |
|---|---|---|
| 1 | `<div class="tabs">` | `<button class="tab" data-view="X">탭 이름</button>` |
| 2 | `<main>` 안 | `<div class="view view-X"><svg viewBox="0 0 1320 742" ...><g id="X-content"></g></svg></div>` |
| 3 | `switchView()` | `else if (view === 'X') { renderX(); }` |
| 4 | `applyTheme()` | `else if (state.view === 'X') renderX();` |
| 5 | data 객체 | `const TAB_X = {...};` |
| 6 | render 함수 | `function renderX() { clear($Xcontent); ... }` |

**1 위치라도 빠지면** validator 가 ERROR. 자세히는 `references/tab-pattern.md`.

---

## 7. Common pitfalls

1. **switchView/applyTheme 양분기 동기 누락** — 한쪽만 추가하면 테마 토글 시 빈 화면. validator 가 잡음.
2. **SVG text 자동 wrap 없음** — `snippets/svg-text-wrap.js` 의 `wrapSvgText(text, maxChars)` 사용. 또는 `<tspan>` 수동 줄단위 배치.
3. **viewBox 좌표 = 픽셀** — `x: 30` 좌측 30 px 마진 / `x: 1290` 우측 30 px 마진. 1320 폭 안에서 계산.
4. **한영 폰트 사이즈 불균형** — 한글 시각적으로 작게 보임. font-size 한글 +1~2 px 권장.
5. **데이터 객체 ↔ render 함수 동기** — 데이터에 새 필드 추가했는데 render 안 그리면 침묵 누락. validator 에 직접 검사 항목은 없으므로 PR 리뷰 시 주의.

자세히: `references/pitfalls.md`.

---

## 8. Verification

1. **정적 검증**: `node ~/.claude/skills/web-slide/scripts/validate-slide.mjs <slide.html>` → exit code 0
2. **시각 검증**:
   - 브라우저 또는 chrome-devtools-mcp 로 파일 열기
   - 모든 탭 차례로 클릭 → 정상 렌더 확인
   - dark/light 토글 → 양쪽 모두 텍스트 가독성 유지
   - 윈도우 크기 변경 → 16:9 비율 유지, 텍스트 오버플로우 없음
3. **회귀 검증**: 새 탭 추가 후 기존 탭이 깨지지 않았는지 모두 다시 클릭

---

## 9. References (이 디렉토리 안)

- **빠른 참조**: `references/cheat-sheet.md` (한 페이지 요약 — 처음 시작할 때)
- `references/16-9-layout.md` — 픽셀 좌표 수학, 그리드 가이드라인
- `references/tab-pattern.md` — switchView/applyTheme/state 객체 패턴
- `references/svg-primitives.md` — svg() helper / wrap / marker / 카드 카탈로그
- `references/themes.md` — 10+1 컬러 팔레트 + 한영 폰트 페어
- `references/pitfalls.md` — 5개 함정 + 재현/탐지법
- `references/reference-example.md` — cobot2 architecture-playground 줄번호 색인
- `references/export.md` — PNG / PDF / PPTX 변환 방법
- `templates/blank-slide.html` — 1 탭 starter (Pretendard + JetBrains Mono CDN 포함)
- `templates/multi-tab-shell.html` — 3 탭 starter (양분기 완비, 키보드 ←→T 단축키, 인쇄 호환, web font CDN)
- `templates/slide-layouts/*.md` — 6 레이아웃 (title-hero / 3-column / architecture-diagram / timeline-history / metric-cards / sequence-diagram)
- `templates/snippets/` — svg-text-wrap.js / theme-tokens.css / lucide-icons.js (30 icon)
- `scripts/scaffold.mjs` — 새 deck 자동 생성 (탭/render/양분기 1회 패치)
- `scripts/validate-slide.mjs` — 정적 검증 (5-way diff + 마진 + 데이터-render heuristic)
- `evals/evals.json` — 트리거 정확도 측정용 (10 trigger + 8 non-trigger)

**빠른 생성**:
```bash
node ~/.claude/skills/web-slide/scripts/scaffold.mjs \
  /tmp/myproject.html "My Project" \
  overview:title-hero arch:architecture-diagram metrics:metric-cards
```
