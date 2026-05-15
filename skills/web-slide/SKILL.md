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

6. **검증** — 2 단계:
   - **정적**: `node ~/.claude/skills/web-slide/scripts/validate-slide.mjs <file.html>` → exit 0
   - **라이브 (MCP)**: `references/live-preview-mcp.md` 의 표준 시퀀스 따름 — `chrome-devtools` MCP 로 모든 탭 자동 캡처 + console 에러 확인 + 다크/라이트 양쪽 검증. 발표용이면 LCP + 접근성까지. **정적 통과해도 라이브 검증으로만 잡히는 이슈가 9 종 이상** — 절대 생략 X.
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

### 5.1 슬라이드 컨테이너 디자인 규칙 (필수)

모든 슬라이드 컨테이너는 다음 규칙을 따른다:

| 규칙 | 값 | 이유 |
|---|---|---|
| **직각 사각형** | `border-radius: 0` (CSS) + `rx: 0` (SVG rect/chip 모두) | 발표/문서 톤을 또렷하게. 둥근 카드는 캐주얼한 인상을 줘 채용 데크/엔지니어링 자료에 부적합 |
| **다크 배경** | `background: #131826` (또는 dark theme `--bg-2`) | 컨테이너 안 강조 색이 또렷하게 보이고, 페이지(다크) 와 일관 |
| **컨테이너 내부 텍스트** | `--text: #e6ecf5` (light glyph on dark) | dark 배경에서 가독성 확보 |
| **light hex 사용 금지** | `'#F4F2EC' / '#ECEAE0' / '#1a1a1a'` 등 light 친화 hex 직접 사용 X | CSS 변수만 사용 — 컨테이너 토큰 override 시 자동 호환 |
| **내부 카드 rx** | `.slide-card`, `.slide-card-strong`, `.slide-chip` 모두 `rx: 0` | 컨테이너 통일 |

기본 `.slide-frame` CSS 템플릿 (이 그대로 복사해서 사용):

```css
.slide-frame {
  --bg:     #131826;
  --bg-2:   #1c2335;
  --bg-3:   #2a3550;
  --text:   #e6ecf5;
  --text-2: #b6c1d6;
  --text-3: #8a96ad;
  --accent: #2dd4bf;
  --line:   #2a3550;
  --line-2: #3a4665;

  background: #131826;
  color: #e6ecf5;
  aspect-ratio: 16 / 9;
  border-radius: 0;                                    /* 필수 — 직각 */
  box-shadow: 0 0 0 1px #2a3550, 0 12px 32px rgba(0,0,0,0.45);
  padding: 24px 28px;
  overflow: hidden;
  width: 100%; max-width: 1320px; margin: 0 auto;
}
.slide-frame svg.diagram { width: 100%; height: 100%; aspect-ratio: 16 / 9 !important; }
.slide-card        { fill: var(--bg-2); stroke: var(--line-2); rx: 0; }
.slide-card-strong { fill: var(--bg-2); stroke: var(--accent);  rx: 0; stroke-width: 1.4; }
.slide-chip        { fill: var(--bg-3); stroke: var(--line-2); rx: 0; }
```

JS 안 rect 생성 시에도 `rx: 0` 명시 — 디폴트 0 이지만 명시해서 가독성/일관성 확보.

**예외**: 사이드바 탭 버튼 (`.tab`) 의 둥근 모서리는 슬라이드 외부 UI 이므로 유지 가능. 이 규칙은 슬라이드(.slide-frame) 안 요소에만 적용.

### 5.2 viewBox 는 반드시 16:9 strict — modifier 로 비율 깨면 안 됨

모든 슬라이드 SVG 는 `viewBox="0 0 1320 742"` 고정. 콘텐츠가 안 들어간다고 viewBox 를 1320×820 / 1320×920 으로 확장하거나 CSS modifier 로 `aspect-ratio: 1320/820` 같은 비-16:9 비율을 부여하면 안 됨.

**실수 사례** (cobot2 프로젝트, 2025-05): flow / system / stack / training 슬라이드의 SVG viewBox 가 1320×820~920 으로 설계되어 있었고, 흰 카드 컨테이너를 적용할 때 콘텐츠 보존을 위해 `.slide-frame.tall` / `.slide-frame.taller` modifier 로 컨테이너 비율 자체를 깨뜨렸다. 결과 — 사용자가 요청한 "모든 슬라이드 16:9" 가 4개 슬라이드에서 위반.

**올바른 해결**:
- viewBox 가 1320×742 보다 세로로 길면 → 콘텐츠 좌표 재배치 (폰트/카드 크기 줄여서 742 안에 fit). 이게 정답.
- 즉시 fix 가 필요하면 → `preserveAspectRatio="xMidYMid meet"` 으로 letterbox 처리. 컨테이너는 16:9 유지, SVG 콘텐츠는 비례 유지하며 약간 작아짐.
- modifier 클래스로 컨테이너 비율 깨는 건 **금지**.

validator (`scripts/validate-slide.mjs`) 가 이 규칙을 강제:
- `aspect-ratio:` CSS 값이 `16/9` 가 아니면 ERROR
- SVG viewBox 가 `0 0 1320 742` 이외이면 ERROR

### 5.3 글씨 크기 — 여백을 보면 크게 만들 것

카드 안 여백이 많은데 글씨를 작게 두는 건 흔한 실수. 카드 콘텐츠 폰트의 **하한**:

| 용도 | 최소 px | 권장 |
|---|---|---|
| 카드 본문 | **12** | 13-14 |
| 카드 제목 | **14** | 16 |
| metric 큰 숫자 | **24** | 32-38 |
| label (UPPERCASE 메타) | **10** | 11 |
| footer strip 값 | **12** | 12-13 |
| 코드/JSON 스니펫 | **11** | 11.5 (mono) |

**11px 이하**는 footnote / 메타 / 작은 라벨에만 허용. 카드 본문에 11px 이하 사용 금지.

**작성 워크플로**:
1. 콘텐츠를 권장 폰트(13-14px)로 먼저 배치
2. 카드 크기가 넘치면 → 문장 줄이기 / 항목 수 줄이기 (폰트 줄이지 말 것)
3. 카드 크기 줄여도 안 들어가면 → 카드 폭 키우거나 column 수 줄이기
4. 그래도 안 되면 → 콘텐츠를 다른 슬라이드로 분리

**실수 사례** (cobot2 exception-handling, 2025-05): 2×2 quadrant 안 본문 12.5px / 카드 높이 250px 인데 항목 3-4개로 카드 안 여백 100px+ 낭비. 13.5-14px 로 키우는 게 정답.

### 5.4 기술 스택 / 브랜드 아이콘 — emoji 금지

기술 스택 / 서비스 / 브랜드를 표시할 때 **emoji 절대 금지**. 이모지는 정식 브랜드 표현이 아니고 OS 별 렌더링이 달라 신뢰성 없음.

| 잘못된 예 | 올바른 대안 |
|---|---|
| 🐬 (MySQL) | simple-icons MySQL SVG path 또는 lucide `database` 아이콘 |
| 🍃 (MongoDB) | simple-icons MongoDB SVG path 또는 lucide `database` |
| 🐍 (Python/FastAPI) | simple-icons Python/FastAPI SVG path 또는 lucide `code` |
| 🤖 (robot) | 사진 placeholder rect 또는 simple-icons / lucide `bot` |
| 📋 (clipboard) | lucide `clipboard` 또는 `list` |

**선택 우선순위**:
1. **simple-icons** (https://simpleicons.org/) — 공식 브랜드 SVG path. inline 으로 path d 데이터 복사. 라이선스 CC0.
2. **lucide** — generic 아이콘. 이 skill 의 `templates/snippets/lucide-icons.js` 에 30개 path 카탈로그.
3. (필요 시) 텍스트 라벨 + 색 레일 — "MySQL" 텍스트 + 좌측 색 5px

**실수 사례** (cobot2 docker-deploy, 2025-05): mysql 🐬, mongodb 🍃, robot-stack 🐍 emoji 사용. 3개 모두 정식 브랜드 아이콘 아님. simple-icons brand SVG 로 교체.

코드 작성 시 자가 점검: SVG 안 `text` element 의 `text` 값에 emoji(non-ASCII pictograph) 포함됐는지 grep. 발견 시 무조건 SVG path 로 교체.

### 5.5 슬라이드 영역 단독 폭 1500+ 보장 — 사이드 패널은 슬라이드 안으로

좌측 사이드바 (탭 네비게이션) 외에 **우측에 메타/요약/사이드 패널을 두지 말 것**. 슬라이드 자체가 PPT 의 본질이므로 메타 정보는 슬라이드 안 footer strip 으로 통합. 슬라이드 카드 단독 폭을 **1500px 이상** 확보.

```css
.canvas-wrap {
  display: grid;
  grid-template-columns: 230px 1fr;  /* 사이드바 + 슬라이드. 우측 패널 없음 */
}
.view, .view-area { max-width: 1600px; }
.slide-frame { max-width: 1600px; }
```

**왜 중요**: 슬라이드 영역이 1380px 이하로 압축되면 SVG viewBox 1320×742 가 화면 1380px 로 렌더되면서 콘텐츠 폰트가 시각적으로 작아짐 (12px → 11px). 5-6장 슬라이드에서 글씨 8-10px 로 짜기 시작. 패널 1개 제거하면 +300px → 즉시 해결.

**실수 사례** (cobot2, 2025-05): 우측 310px 메타 패널("현재 뷰 요약" + 복사 버튼) 이 슬라이드 영역을 1380px 로 압축 → gripper/db/node-arch/workflow/training-history 5장이 4-10px 글씨로 짜낌 → PPT 본질 훼손. 메타 패널 제거만으로 5장 모두 14+/20 점 회복.

**원칙**: 슬라이드 외부 UI (메타/요약/사이드 패널/copy 버튼) 는 디버깅용. 발표/공유용 deck 에는 **슬라이드 + 사이드바** 만. 외부 정보는 슬라이드 안에 footer strip 으로 통합 (§5 의 `drawFooterStrip` 헬퍼 참고).

### 5.6 다단 콘텐츠의 글씨 사이즈 최소값

PPT 슬라이드는 발표/공유 시 멀리서 읽을 수 있어야 함. 글씨 크기 **하한**:

| 용도 | 최소 | 권장 |
|---|---|---|
| 카드 본문 | **12** | 13-14 |
| 카드 제목 | **14** | 16-17 |
| 테이블 데이터 (td) | **11** | 12 |
| 코드/JSON 블록 | **11** | 11.5-12 |
| 라벨 (UPPERCASE 메타) | **10** | 11 |
| metric 큰 숫자 | **24** | 32-38 |
| footer strip 값 | **12** | 12-13 |

**11px 이하 본문 사용 금지**. 카드 본문에 10px 또는 9px 발견 시 즉시 다음 순서로 해결:

1. **컨테이너 폭 확보 우선** — 사이드/메타 패널 제거. 단독 슬라이드 폭 ≥ 1500px (§5.5).
2. **카드 폭 확장** — 카드 수 줄이거나 행 분리 (5-row → 3+2 row).
3. **콘텐츠 분할** — 한 슬라이드 → 두 슬라이드. 정보 압축이 아니라 분배.

**금지**: "콘텐츠 다 들어가지 않으니 폰트 줄이기" — 이건 절대 금지. PPT 본질 (멀리서 읽힘) 을 깨뜨림.

### 5.7 카드 padding 16-22 표준 (12 금지)

카드 안 텍스트 좌측 padding 12px 은 폭이 좁아 보임. 표준:
- 카드 내부 padding: **16-22px** (좌우 동일, 일관성)
- 카드끼리 gap: **14-16px**
- 카드 내부 줄간격 (line-height): 1.5em (32-36px @ 14px font)

12px padding 사용 금지. 슬라이드 안 카드끼리 시각적 일관성 깨뜨림.

신규 슬라이드 작성 시 `drawCard(g, x, y, w, h, opts)` 헬퍼 사용 권장 (이 skill 의 templates/ 안 정의된 표준 카드).

### 5.8 SVG viewBox 자체가 16:9 — 컨테이너만 16:9 로 만들지 말 것

§5.2 에서 "viewBox 16:9 strict" 강제했지만, **컨테이너의 aspect-ratio 만 16:9 로 강제하고 SVG viewBox 가 1320×920 처럼 16:9 가 아닌 경우** preserveAspectRatio="xMidYMid meet" 으로 letterbox 자동 처리되면서 컨테이너 안 좌우/상하에 빈 공간이 생긴다.

**예** (cobot2 flow, 2025-05): viewBox 1320×920 (1.435 비율) + 컨테이너 16:9 (1.778) → SVG 가 컨테이너 height (900px) 에 fit 하면서 width 가 1544px 까지만 → 좌우 28px 씩 빈공간.

**근본 원칙**: **컨테이너 비율 ≡ 콘텐츠 비율**. 컨테이너만 16:9 로 만들면 letterbox 만 옮길 뿐 빈공간 자체는 해소 안 됨.

**올바른 처리**:
- SVG viewBox 반드시 `0 0 1320 742`
- 콘텐츠 좌표가 1320×742 안에 안 들어가면 → **콘텐츠 압축/분할** (폰트 줄이지 말고). 슬라이드를 2장으로 나누는 게 정답.
- `.slide-frame.tall` / `.slide-frame.taller` 같은 modifier 클래스로 viewBox 비율을 살리려 하지 말 것.

**자가검증** (모든 슬라이드 작업 직후 실행):
```js
// Playwright/devtools console
document.querySelectorAll('svg.diagram').forEach(svg => {
  const vb = svg.getAttribute('viewBox');
  if (vb !== '0 0 1320 742') console.warn('Bad viewBox', svg.id, vb);
});
```

### 5.9 한 deck = 한 렌더링 패러다임 (SVG-render vs HTML-static 혼합 금지)

같은 deck 안에서 일부 슬라이드는 SVG `<text>` element 로 그려지고 일부는 HTML `<table>`/`<pre>` 로 그려지면 디자인 토큰 (font-size, color, padding) 이 자동 적용 안 된다. SVG 와 HTML 은 CSS class/var 가 다른 방식으로 적용된다.

**예** (cobot2 db, 2025-05): 19 슬라이드는 SVG render (`renderX()` 함수 안 `svg('text', {...})`), DB 구조 슬라이드만 HTML 인라인 style (`<table style="font-size:9px">`). 결과 — DB 슬라이드만 텍스트 8-9px / 색 hardcode (#00758F 등) / padding 다름 → 다른 19 슬라이드와 일관성 파괴.

**올바른 처리** — 둘 중 하나:
1. **단일 패러다임 강제** — 모든 슬라이드를 SVG render 로 통일. 테이블/JSON 도 SVG `<text>` 로 그림 (단조롭지만 일관성 확실).
2. **혼합 허용 + 공통 HTML class** — HTML 슬라이드는 `.slide-table`, `.slide-code`, `.slide-section-title` 같은 공통 class 만 사용. CSS 변수 (`var(--text)`, `var(--accent)`) 만 사용. 인라인 hex 색 금지.

**자가검증**:
```bash
# 인라인 hex 색 발견 시 ERROR
grep -E '<[^>]*style="[^"]*#[0-9A-Fa-f]{3,6}' file.html | grep -v 'border-radius\|gradient'
```

### 5.10 슬라이드 간 콘텐츠 중복 검사 — 사이드바에 비슷한 이름이면 의심

여러 슬라이드가 비슷한 데이터/메트릭을 반복하면 deck 의 정보 밀도가 떨어지고 사용자가 혼란스러워한다.

**예** (cobot2 training + training-result, 2025-05): 두 슬라이드 모두 상단 7-pill metric row 동일 (mAP/F1/Recall/Fitness 등). 본문 70% 겹침. 사용자 인식 — "왜 같은 내용을 두 번?".

**원인**: 슬라이드를 한 장씩 작성하면서 deck 전체 narrative 검증 안 함. 비슷한 카테고리 (Training, Training Result, Training History — 모두 "training" 시작) 의 슬라이드를 따로 작성하면 자연스럽게 중복.

**올바른 처리**:
1. **사이드바 이름 prefix 같으면 의심** — 같은 prefix (Training/Training Result/Training History) 가진 슬라이드들은 명시적 역할 분리 필요.
2. **역할 분리 원칙** — 동일 도메인 슬라이드들 사이에:
   - 첫 번째: "과정" (어떻게)
   - 두 번째: "결과" (얼마나)
   - 세 번째: "히스토리/회고" (왜)
3. **중복 검사** — 슬라이드 작업 후 사이드바 prefix 가 같은 슬라이드들의 메트릭/KPI row 일치 여부 확인. 동일 row 가 있으면 한 슬라이드에서만 표시.

**자가검증**: 각 슬라이드 별 핵심 메시지를 한 문장으로 적어 비교. 중복되면 콘텐츠 재분배.

### 5.11 자가검증 체크리스트 — 슬라이드 작업 후 반드시 실행

새 슬라이드를 추가하거나 deck 을 큰 변경한 직후, 다음 8 항목을 차례로 점검:

```markdown
## web-slide 자가검증 체크리스트

- [ ] **viewBox 16:9 strict** — 모든 SVG viewBox === "0 0 1320 742"? (§5.2, §5.8)
- [ ] **컨테이너 16:9 strict** — aspect-ratio CSS 값이 16/9? (§5.2)
- [ ] **글씨 최소값** — 카드 본문 ≥12px, 카드 제목 ≥14px, 라벨 ≥10px, 코드 ≥11px? (§5.3, §5.6)
- [ ] **emoji 0개** — SVG text content 에 emoji 발견 시 simple-icons/lucide 로 교체? (§5.4)
- [ ] **카드 padding 16-22** — 카드 내부 좌측 padding ≥16px? 12px 없음? (§5.7)
- [ ] **사이드 패널 없음** — 우측 메타/요약/사이드 패널 두지 않음? (§5.5)
- [ ] **렌더 패러다임 통일** — HTML 인라인 style hex 색 0개? (§5.9)
- [ ] **슬라이드 중복 없음** — 사이드바 같은 prefix 슬라이드들 역할 분리 명확? (§5.10)
```

8 항목 중 1개라도 실패 시 → 작업 미완성. 사용자에게 보고 전 모두 통과시킬 것.

validator (`scripts/validate-slide.mjs`) 가 §5.2, §5.4, §5.7 자동 검사. 나머지는 시각 + grep + 사람 판단.

---

## 6. 시행착오 패턴 — 이전 작업에서 학습한 함정

이 skill 의 §5.1~§5.11 규칙들은 모두 cobot2 architecture-playground.html 작업 중 발견된 실제 시행착오로부터 유래. 각 규칙은 한 번 실패한 후에야 시스템화되었다. 새 deck 작업 시 같은 함정에 빠지지 않도록 다음 패턴들을 의식할 것:

### 6.1 viewBox 가 16:9 가 아닌 채로 컨테이너만 강제

**언제 발생**: 콘텐츠 보존을 위해 viewBox 1320×820/920 그대로 두고 컨테이너 aspect-ratio 만 16/9 로 변경.
**결과**: letterbox 좌우/상하 빈공간.
**해법**: viewBox 도 1320×742 로. 콘텐츠 안 들어가면 슬라이드 분할.

### 6.2 SVG render 와 HTML static 혼합

**언제 발생**: 테이블/코드 표현이 어려워 HTML 로 작성한 슬라이드를 deck 에 포함.
**결과**: 디자인 토큰 적용 안 됨. 폰트 8-10px / 색 hardcode.
**해법**: HTML 슬라이드도 CSS 변수만 사용 + 공통 class.

### 6.3 비슷한 이름의 슬라이드 중복 콘텐츠

**언제 발생**: Training/Training Result/Training History 처럼 같은 prefix 의 슬라이드들 따로 작성.
**결과**: metric pill row 100% 동일 / 본문 70% 겹침.
**해법**: 사이드바 prefix 같으면 의심. 명시적 역할 분리 (과정/결과/회고).

### 6.4 이모지를 브랜드 아이콘으로 사용

**언제 발생**: mysql=🐬, mongodb=🍃, fastapi=🐍 같은 이모지를 정식 아이콘으로 착각.
**결과**: OS 별 렌더링 다름 / 정식 brand 아님.
**해법**: simple-icons SVG path inline 또는 lucide generic 아이콘.

### 6.5 우측 메타 패널 / 사이드 영역 추가

**언제 발생**: "현재 뷰 요약" 같은 보조 정보 영역을 슬라이드 우측에 추가.
**결과**: 슬라이드 영역 1380px 로 압축 → 콘텐츠 폰트 4-10px 로 짜냄.
**해법**: 보조 정보는 슬라이드 안 footer strip 으로. 외부 사이드 패널 금지.

### 6.6 BT tree / 다이어그램 sub-tree 노드 충돌

**언제 발생**: 트리/네트워크 다이어그램에서 sub-tree 의 자식 노드들을 부모 좌표 ±gap 으로 단순 분기. 인접 부모의 sub-tree 와 영역 겹침.
**결과**: 카드끼리 시각적으로 붙거나 겹침 (border 가 겹쳐 보임).
**예** (cobot2 behavior-tree, 2025-05): PickObject 자식 (Retry x2, x=xs[1]+90=910, w=150 → 우측 985) 와 ShakeMotion 자식 (PCA Orientation, x=xs[2]=1020, w=160 → 좌측 940) 가 45px 겹침.
**해법**: §5.12 (아래) — SVG 좌표 충돌 자동 검증 + sub-tree 영역 계산 규칙.

---

## 5.12 SVG element 충돌 자동 검증 — 다이어그램류 슬라이드 필수

BT tree / sequence / network 같은 다이어그램류 슬라이드는 SVG rect/text 가 절대 좌표로 배치되므로 **충돌 사전 검증** 없이는 카드끼리 겹친다. 시각 검증 (스크린샷) 으로 작은 겹침을 놓치기 쉬워 자동 검사 필수.

### 5.12.1 사후 검증 (devtools console 또는 Playwright evaluate)

```js
// 모든 작은 rect (= 카드) 의 충돌 검출. 배경/그리드 rect 는 폭 400+ 으로 제외.
function detectSvgOverlap(svgEl) {
  const rects = Array.from(svgEl.querySelectorAll('rect'));
  const boxes = rects
    .filter(r => r.width.baseVal.value > 30 && r.width.baseVal.value < 400)
    .map(r => ({
      el: r,
      x1: r.x.baseVal.value, y1: r.y.baseVal.value,
      x2: r.x.baseVal.value + r.width.baseVal.value,
      y2: r.y.baseVal.value + r.height.baseVal.value,
    }));
  const overlaps = [];
  for (let i = 0; i < boxes.length; i++) {
    for (let j = i+1; j < boxes.length; j++) {
      const a = boxes[i], b = boxes[j];
      const ix = Math.max(0, Math.min(a.x2, b.x2) - Math.max(a.x1, b.x1));
      const iy = Math.max(0, Math.min(a.y2, b.y2) - Math.max(a.y1, b.y1));
      // 카드끼리 1px 이상 겹치면 (border-on-border 도 포함) 보고
      if (ix > 0 && iy > 0) {
        overlaps.push({ i, j, overlapX: ix, overlapY: iy });
      }
    }
  }
  return overlaps;
}
// 모든 슬라이드 검사
document.querySelectorAll('svg.diagram').forEach(svg => {
  const ovs = detectSvgOverlap(svg);
  if (ovs.length) console.warn('OVERLAP', svg.id, ovs);
});
```

다이어그램류 슬라이드 작업 후 반드시 이 스크립트 실행. 출력 0건 = OK.

### 5.12.2 사전 검증 — 좌표 계산 단계에서 충돌 방지 규칙

트리/그래프 노드 좌표 계산 시 다음 규칙:

1. **sibling 노드 폭 합 ≤ 부모 영역 폭** — 부모 노드 자식이 N개 이면 자식 폭 합 + (N-1)*gap ≤ 부모가 차지하는 sub-tree 영역.
2. **sub-tree 영역 분리** — 부모 A 의 sub-tree 영역 우측 ≤ 부모 B 의 sub-tree 영역 좌측 (gap 최소 20px).
3. **sub-tree 깊이가 깊어질수록 영역 좁아짐** — sub-tree 의 가용 폭 = 부모의 가용 폭 / sibling 수. 4-children 부모 안 2-children 손자 영역은 1/8.

**구현 패턴** — sub-tree 영역을 데이터 구조로 추적:

```js
function layoutTree(node, x, y, areaW) {
  node.x = x + areaW / 2;  // 중앙 정렬
  node.y = y;
  if (!node.children?.length) return;
  const childW = areaW / node.children.length;
  node.children.forEach((c, i) => {
    layoutTree(c, x + i*childW, y + LEVEL_GAP, childW);
  });
}
```

`areaW` 가 분기 시 자동 분할되어 자식 영역이 부모 영역 안에 들어가도록 강제. 충돌 0.

### 5.12.3 자가검증 절차

다이어그램류 슬라이드 작업 시 다음 순서:
1. 좌표 계산을 `layoutTree()` 같은 영역-기반 함수로 작성 (절대 좌표 하드코드 금지)
2. 슬라이드 렌더 직후 `detectSvgOverlap()` 실행 → 출력 0건 확인
3. Playwright 스크린샷 + 시각 확인

위 3 단계를 통과해야 다이어그램류 슬라이드 작업 완료.

### 5.13 콘텐츠 bbox 도 viewBox 를 채워야 — 단순히 viewBox 만 16:9 가 아니라

§5.8 에서 "viewBox 자체가 16:9" 강제했지만, 한 단계 더 — **콘텐츠 bbox (실제 element 들이 분포한 영역) 도 viewBox 의 90% 이상 채워야 함**. viewBox 만 16:9 라도 콘텐츠가 viewBox 의 60%만 사용하면 나머지 40% 가 빈공간 그대로 노출.

**예** (cobot2 system, 2025-05): viewBox 1320×742 (16:9 ✓) 적용 후에도 lane 들이 y=50~650 (콘텐츠 bbox 600px) 만 사용 → viewBox 742 중 **142px (19%) 하단 빈공간**. 사용자가 "여백 활용 부족" 지적.

**근본 원인**: 콘텐츠 자체 비율이 viewBox 와 다름. 시스템 노드의 콘텐츠 bbox 1212×600 비율 = 2.02 (와이드) ≠ 16:9 (1.778). preserveAspectRatio meet 으로 fit 시키면 자연스레 letterbox 발생.

**올바른 처리** — 다음 중 하나:
1. **콘텐츠 bbox 비율을 viewBox 와 일치** — lane/노드/카드 좌표를 일괄 재배치해서 콘텐츠가 1320×742 비율을 채움.
2. **footer strip 으로 하단 채움** — viewBox 의 빈 영역에 `drawFooterStrip()` 으로 metric/info row 추가. 적은 작업, 큰 시각 효과.
3. **outer transform** — `<g transform="scale(sx, sy)">` 로 콘텐츠 비례 확대. 비등비 시 폰트 stretch 주의.

**자가검증**:
```js
// 모든 SVG 슬라이드의 콘텐츠 bbox vs viewBox 검사
document.querySelectorAll('svg.diagram').forEach(svg => {
  const vb = svg.viewBox.baseVal;
  const bb = svg.getBBox();
  const wRatio = bb.width / vb.width;
  const hRatio = bb.height / vb.height;
  if (wRatio < 0.9 || hRatio < 0.9) {
    console.warn(`bbox 부족: ${svg.id} — bbox ${Math.round(bb.width)}×${Math.round(bb.height)} / viewBox ${vb.width}×${vb.height} = ${Math.round(wRatio*100)}%×${Math.round(hRatio*100)}%`);
  }
});
```

90% 미만이면 colored warning. 91% 이상이면 OK.

**시스템 노드 fix 사례**: viewBox 1320×742 / 콘텐츠 bbox 1218×600 = 92%×81%. height 미달 19% → footer strip y=690 으로 채움 → 사용자 만족.

### 5.14 §5 규칙 자동 검증 도구 — 작업 후 즉시 실행

§5.1~§5.13 의 규칙들을 사람이 매번 의식적으로 점검하는 건 비현실적. 다음 자동 검증을 작업 종료 직후 실행:

```js
// 단일 함수로 모든 §5 규칙 점검
function auditSlide(svg) {
  const issues = [];
  const vb = svg.viewBox.baseVal;
  // §5.2/§5.8: viewBox 16:9
  if (vb.width !== 1320 || vb.height !== 742) {
    issues.push(`§5.8: viewBox = ${vb.width}×${vb.height}, expected 1320×742`);
  }
  // §5.13: 콘텐츠 bbox ≥ viewBox 90%
  const bb = svg.getBBox();
  const wR = bb.width / vb.width, hR = bb.height / vb.height;
  if (wR < 0.9 || hR < 0.9) {
    issues.push(`§5.13: bbox ratio ${Math.round(wR*100)}%×${Math.round(hR*100)}% (need ≥90%)`);
  }
  // §5.12: rect 겹침
  // (detectSvgOverlap 로직)
  // §5.6: 폰트 12 이하
  svg.querySelectorAll('text').forEach(t => {
    const fs = parseFloat(getComputedStyle(t).fontSize);
    if (fs < 12 && !t.matches('.slide-h-eyebrow,.slide-metric-label,[font-size]')) {
      issues.push(`§5.6: text "${t.textContent.slice(0,20)}" fontSize ${fs}px`);
    }
  });
  return issues;
}
// 모든 슬라이드 검증
document.querySelectorAll('svg.diagram').forEach(svg => {
  const issues = auditSlide(svg);
  if (issues.length) console.warn(`AUDIT ${svg.id}:`, issues);
});
```

이 함수를 `templates/snippets/audit-slide.js` 에 저장. 모든 deck 작업 끝에 console 에 paste 실행.

**모든 슬라이드의 issues 가 0 일 때까지 작업 미종료**. 이게 §7.4 의 핵심 강제 메커니즘.

### 5.15 — 슬라이드 콘텐츠 vs 코드 진실성 검증

deck 의 노드 / topic / DB schema / 메트릭은 **실제 코드와 정합** 해야 함. PPT 슬라이드 작성자가 자주 놓치는 함정 — 코드와 슬라이드가 별도 진실 출처가 되어 어긋남.

**실수 사례** (cobot2, 2025-05): `command_executer` (slide) vs `executer` (setup.py entry_point) 4 곳 불일치. 슬라이드 작성자가 코드 grep 없이 추측해서 적었음.

**규칙**:
1. deck 안 노드/토픽/스키마 이름은 **코드 단일 출처에서 복사** — `grep -nE 'entry_points|create_publisher|create_service' src/`
2. 슬라이드 변경 시 code 변경과 paired (PR 설명에 "deck synced with src/X.py L23" 명시)
3. 검증 — slide HTML 의 노드/토픽 추출 → code grep → 차이 list

**자가검증** (deck 작업 직후):
```bash
# slide 안 node 라벨 추출 (label: 'X' 형식)
grep -oE "label: '[a-z_]+'" file.html | sort -u | sed "s/label: '\\([^']*\\)'/\\1/" > slide-nodes.txt
# code 안 entry_points 추출
grep -oE "'[a-z_]+ *= *[^']+'" src/setup.py \
  | grep -oE "'[a-z_]+ *=" | sed "s/[' =]//g" | sort -u > code-nodes.txt
diff slide-nodes.txt code-nodes.txt
# 차이 발견 시 slide 또는 code 정정. 추상화 명칭 (wakeup_worker 같은 web backend) 은 별개 출처.
```

**예외**: 슬라이드가 의도적 추상화 (예: cobot2 의 `wakeup_worker` = web/cobot2/backend/wakeup_worker.py 파일 — ROS 노드가 아닌 별개 layer) 는 해당 layer 별로 진실 출처 분리. SKILL 안 명시.

### 5.16 — 단일 도메인 슬라이드 통합 (TOC 압축) 절차

같은 도메인 (Training 학습 / Workflow 흐름) 의 슬라이드가 2-3 개로 분리되어 메트릭/콘텐츠 50%+ 겹치면 **사이드바 라벨 명확화 + 통합** 으로 압축.

**실수 사례** (cobot2, 2025-05): Training + Training Result 2탭이 같은 8 KPI pill row 표시 → 사용자 인식 "왜 같은 내용 두 번?". Workflow + Flow 2탭도 같은 흐름 도메인.

**처리 순서**:
1. **라벨 명확화 우선** — 같은 prefix 슬라이드를 명시적 역할 분리 라벨로 (예: "Training" → "Model Training", "Training Result" → "Best Checkpoint", "Training History" → "v6→v10 Evolution")
2. **사이드바 button 1개만 활성** — TOC 가 사용자에게 보이는 entry point. button 제거하면 dead view 처리
3. **TAB_ORDER 갱신** — 키보드 네비게이션 배열 동기. button 제거된 view 는 TAB_ORDER 에서도 제거. 누락 시 ← / → 키가 dead view 로 진입
4. **dead view + render 함수 cleanup** — view div / render 함수 / switchView·applyTheme 분기 정리. **단, hidden 상태로 두는 것도 OK** — JS 가 분기에서 안 호출하면 무해. cleanup 은 후순위.

**원칙**:
- 통합 시 viewBox 1320×742 고정
- 좌/우 2섹션 = 각 660 폭 + gap 30
- 상/하 2섹션 = 각 350 높이 + gap 20
- KPI pill 한 곳에만 표시 (좌 또는 상단). 우/하 영역은 상세/per-class/timeline

### 5.17 — 디자인 위반 자동 grep 검사 — 작업 종료 직전 강제

§7.4 의 8-step 체크 중 grep 가능 항목 모두 단일 명령으로 묶음. validator (`scripts/validate-slide.mjs`) 가 강제:

```bash
# §5.2/§5.8 viewBox 16:9 strict (마커/아이콘 작은 viewBox 제외)
grep 'viewBox=' file.html | grep -v '0 0 1320 742\|0 0 24 24\|0 0 10 10\|0 0 56 22' | head -10
# 결과 0 라인 = OK

# §5.4 emoji (slide 안. UI 외부 텍스트 제외)
grep -nP '[\x{1F300}-\x{1FAFF}]' file.html | grep -v 'btn.textContent\|placeholder='
# 결과 0 라인 = OK

# §5.9 inline hex slide 안 (gradient/border-radius 예외)
grep -E 'style="[^"]*#[0-9A-Fa-f]{3,6}' file.html | grep -v 'gradient\|border-radius'
# 결과 0 라인 = OK

# §5.2 .tall/.taller modifier 사용 (금지)
grep -nE 'slide-frame (tall|taller)' file.html
# 결과 0 라인 = OK
```

validator (`scripts/validate-slide.mjs`) 에 4 검사 추가. 위반 발견 시 ERROR + 위반 위치 (줄번호) 출력. exit 1.

**규칙**: deck 작업 종료 직전 4개 grep 모두 0 라인 통과 후에야 사용자에게 "완료" 보고. 하나라도 위반 시 작업 미종료.

**cobot2 작업 결과** (2025-05): §5.15-§5.17 적용 후 20→18 탭, viewBox 위반 0, emoji 0, hex 0, modifier 0, 노드 라벨 정합 100%. 

---

## 7. 왜 skill 이 실패하는가 — 메타 비판 + 강제 적용 절차

이 skill 의 §5 규칙들은 모두 명문화되어 있지만, **사용 시점에 의식적으로 적용 안 하면 무용**. 이전 cobot2 작업에서 다음 메타 실패 패턴이 반복됐다:

### 7.1 skill 규칙은 신규 작성 가이드일 뿐, 기존 deck 자동 fix 안 함

§5.1~§5.12 는 모두 "이렇게 작성하라" 가이드. **기존 작성된 슬라이드는 명시적으로 audit + retrofit 하지 않으면 규칙 위반 채로 남는다**.

**예** (cobot2 system, 2025-05): 기존 system 슬라이드의 SVG viewBox 가 `1320×820` (§5.2/§5.8 위반). 신규 10장 작업 + 메타 패널 제거 등 변경했지만 system 슬라이드 viewBox 는 그대로 → 16:9 컨테이너 안에서 letterbox → 위/아래 (그리고 lane 폭 활용 부족으로 좌/우) 빈공간.

skill 의 §5 규칙은 신규 슬라이드용. 기존 슬라이드의 viewBox/그리드/콘텐츠는 자동 변경 안 됨.

### 7.2 audit 절차 부재 — 모든 변경 후 §5.11 + §5.12 자가검증 실행 안 함

§5.11 에 자가검증 체크리스트를 정의했지만 **매 작업 후 자동 실행하는 절차 부재**. 사용자가 문제 지적할 때까지 점검 안 함.

**예**: behavior-tree sub-tree 노드 45px 겹침. detectSvgOverlap() 스크립트는 §5.12 에 정의됐지만 **작업 후 즉시 실행 안 함**. 사용자가 스크린샷으로 지적 → 그제서야 발견.

### 7.3 visualtotal 점수 평가가 실제 문제를 가린다

이전 audit (Phase 1 explore agent) 에서 system=15/20, behavior-tree=15/20 으로 "양호" 분류. 실제로는 letterbox 여백 / sub-tree 충돌 모두 있음. 점수 평가가 **카테고리별 평균 4/5** 로 떨어진 항목들을 "양호" 로 분류하면서 실제 문제 가렸음.

### 7.4 강제 적용 절차 — deck 작업 시 다음을 반드시 실행

이 skill 을 사용하는 작업 (deck 작성, 슬라이드 추가, 슬라이드 수정) 의 **모든 단계 종료 시점에**:

```markdown
## web-slide 작업 종료 체크 (모든 변경 직후 실행)

1. **viewBox 검사** — `grep 'viewBox=' file.html | grep -v '0 0 1320 742'` → 0 lines.
2. **aspect-ratio CSS 검사** — `grep 'aspect-ratio:' file.html | grep -v '16 / 9\|16/9'` → 0 lines.
3. **inline hex 검사** — `grep -E 'style="[^"]*#[0-9A-Fa-f]{3,6}' file.html | grep -v 'border-radius\|gradient'` → 0 lines.
4. **emoji 검사** — `grep -nP '[\x{1F300}-\x{1FAFF}]' file.html` → 0 lines.
5. **SVG element 충돌 검사** — 다이어그램 슬라이드 모두 detectSvgOverlap() 실행 → 0 overlap.
6. **사이드바 prefix 중복 검사** — 사이드바 안 같은 prefix 슬라이드 (예: "Training", "Training Result") 의 metric pill row 비교 → 동일 row 0건.
7. **시각 캡쳐 + 좌우/상하 여백 점검** — Playwright 로 모든 슬라이드 캡쳐. 슬라이드 컨테이너 안 letterbox 영역 0px.
8. **validator 실행** — `node ~/.claude/skills/web-slide/scripts/validate-slide.mjs <file>` → exit 0.
```

8 단계 모두 통과 후에야 작업 종료. 사용자에게 "완료" 보고 전 반드시 8/8 확인.

### 7.5 기존 deck audit + retrofit 절차

새 deck 이 아닌 **기존 deck 을 받은 경우**, 다음 절차로 retrofit:

1. **inventory** — 사이드바 모든 슬라이드 list. 각 슬라이드의 viewBox / aspect-ratio / 카드 padding / 폰트 사이즈 / 인라인 hex 색 / emoji / 메타 패널 존재 여부 추출.
2. **분류**:
   - **자동 fix 가능**: hex 색 → CSS 변수, emoji → simple-icons, 메타 패널 제거.
   - **반자동**: viewBox 1320×820/920 → 1320×742 (콘텐츠 좌표 일괄 ×0.806 또는 slide 분할).
   - **수동 재작성**: 다이어그램 sub-tree 충돌, 슬라이드 콘텐츠 중복.
3. **순서**: 자동 → 반자동 → 수동. 각 단계 종료 후 §7.4 체크리스트 실행.
4. **사용자 보고**: 작업 전후 점수 차이 (4축 점수표) + 남은 수동 작업 명시.

이 절차를 따르지 않으면 §5 규칙들이 명시적으로 위반된 채로 deck 이 출시된다.

### 7.6 skill 의 self-test — 새 슬라이드 작성 시 다음을 모방

새 슬라이드 작업 시 다음 시퀀스를 항상 따라야 함:

```
콘텐츠 설계 → viewBox 1320×742 SVG 생성 →
좌표 계산 (영역-기반, 절대 좌표 금지) →
렌더 함수 작성 (drawCard/drawMetricCard/drawFooterStrip 사용) →
detectSvgOverlap() 0 → §5.11 체크리스트 8/8 → validator 0 → 완료
```

**금지**: 위 시퀀스 일부 생략 후 "사용자가 지적하면 그때 fix" — 이게 §7.1~§7.3 모든 실패의 메타 원인.

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
- `references/live-preview-mcp.md` — `chrome-devtools` + `playwright` MCP 로 라이브 렌더링 검증 (다중 탭 캡처, console 에러, dark/light, LCP, 접근성)
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
