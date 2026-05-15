# live-preview-mcp.md — MCP-driven live verification

`validate-slide.mjs` 가 정적 HTML 분석을 담당하지만, **실제 브라우저에서 어떻게 보이는지 / JS 가 어떻게 동작하는지** 는 정적 분석으로 못 잡는다. 이 reference 는 `chrome-devtools` MCP 와 `playwright` MCP 를 활용해 슬라이드 생성 후 즉시 라이브 검증하는 패턴을 정리한다.

## Contents
1. 두 MCP 비교 — 언제 어느 쪽
2. 기본 워크플로 — generate → preview → verify → iterate
3. 다중 탭 자동 캡처
4. dark/light 양쪽 검증
5. Console 에러로 잡히는 함정들
6. 성능 측정 (LCP / 첫 페인트)
7. 접근성 (대비, 폰트 크기) 검증
8. playwright 다중 브라우저 회귀
9. 흔히 발견되는 실제 이슈 카탈로그

---

## 1. 두 MCP 비교

| 도구 | 강점 | 약점 | 슬라이드 작업엔? |
|---|---|---|---|
| **`chrome-devtools` MCP** | 단일 Chrome 인스턴스, JS evaluate, console/network, 성능 trace, 자연스러운 인터랙티브 디버그 | 단일 브라우저 (Chrome 만), 동시 multi-page 약함 | ⭐ **기본 선택** — 슬라이드 1개 만들고 확인하는 일반 케이스 |
| **`playwright` MCP** | 다중 브라우저 (Chrome/FF/WebKit), 병렬, 시각 회귀, 자동화 | 셋업 무거움, 단순 캡처엔 과다 | 시각 회귀나 cross-browser 검증 필요 시 |

**Rule of thumb**: 일반 슬라이드 검증은 chrome-devtools. 발표자가 다른 브라우저 쓸 가능성 / 이전 버전과 diff 필요 시 playwright.

---

## 2. 기본 워크플로

슬라이드 HTML 을 `~/slides/my-deck.html` 로 생성했다고 가정.

```
[1] HTML 생성 완료 (Write tool)
       ↓
[2] mcp__chrome-devtools__new_page("file:///home/rokey/slides/my-deck.html")
       ↓
[3] mcp__chrome-devtools__take_screenshot()
       → 첫 탭 PNG 받음. 사용자에게 즉시 보일 수 있음
       ↓
[4] mcp__chrome-devtools__list_console_messages()
       → JS 에러 / 경고 즉시 확인
       ↓
[5] (탭이 여러 개라면 §3 의 multi-tab 루프)
       ↓
[6] 발견된 이슈를 사용자에게 보고 + 수정 → [1] 로 복귀
```

**핵심**: 슬라이드를 "넘기는" 데에 사용자 개입 X. JS 로 `switchView()` 호출해서 자동으로 다음 탭 캡처.

---

## 3. 다중 탭 자동 캡처

웹 슬라이드는 `data-view` 분기 + `switchView('view-X')` 함수로 탭 전환. JS 한 줄로 강제 전환 가능.

```javascript
// chrome-devtools__evaluate_script 로 실행할 코드
switchView('view-2');   // tab id 가 view-2 인 슬라이드로 이동
```

7 탭 자동 캡처 패턴:

```
for view in ['view-0', 'view-1', ..., 'view-6']:
    mcp__chrome-devtools__evaluate_script(f"switchView('{view}')")
    # 짧은 wait 권장 (transition CSS 가 있을 수 있음)
    mcp__chrome-devtools__evaluate_script("new Promise(r => setTimeout(r, 200))")
    mcp__chrome-devtools__take_screenshot(filename=f"slide_{view}.png")
```

각 PNG 를 사용자에게 출력 → 한눈에 7 탭 시각 검증.

**자주 잡히는 이슈**:
- view-3 에서 SVG `<text>` 가 화면 밖으로 나감 (svg-text-wrap 누락)
- view-5 의 metric card 가 grid 밖으로 튀어나옴
- view-6 의 다크/라이트 토글이 그 탭에선 동작 안 함

---

## 4. dark/light 양쪽 검증

테마 토글이 작동하는지 + 두 테마 모두 깨지지 않는지 확인.

```javascript
// 다크 모드 강제
applyTheme('dark');
```

캡처 패턴:
```
for theme in ['light', 'dark']:
    mcp__chrome-devtools__evaluate_script(f"applyTheme('{theme}')")
    for view in tab_list:
        mcp__chrome-devtools__evaluate_script(f"switchView('{view}')")
        mcp__chrome-devtools__take_screenshot(filename=f"{theme}_{view}.png")
```

→ 14 장 이미지 (7 탭 × 2 테마). 다크/라이트 색 대비 양쪽 모두 시각 확인.

**자주 잡히는 이슈**:
- 다크 모드에서 SVG `<text fill="#000">` 하드코드 — 보이지 않음. theme 변수로 바꿔야 함
- 라이트 모드에서 텍스트 그림자 (filter: drop-shadow) 너무 진해서 글자 안 보임

---

## 5. Console 에러 — 정적 분석이 못 잡는 함정

`validate-slide.mjs` 는 코드 패턴은 잡지만 **런타임 실패**는 못 잡음. Console 로 잡히는 흔한 케이스:

| Console 메시지 | 원인 | 수정 |
|---|---|---|
| `lucide is not defined` | Lucide 라이브러리 import 누락 | `templates/snippets/lucide-icons.js` 의 CDN 라인 추가 |
| `Cannot read property 'forEach' of undefined` | 데이터 객체 (예: `TAB_3.metrics`) 누락 또는 잘못된 키 | render 함수 실행 전 데이터 정의 확인 |
| `applyTheme is not defined` | switchView 만 정의되고 applyTheme 누락 (5-way diff 한쪽 실종) | applyTheme 함수 작성 |
| `SyntaxError: Unexpected token` | HTML 안 JS 따옴표 충돌 | `'` 와 `"` 일관성 |
| 404 (CDN 자산) | Lucide / simple-icons 의 잘못된 버전 URL | 최신 안정 버전으로 |

검증 한 줄:
```
mcp__chrome-devtools__list_console_messages()
```
→ 빨간 라인 = 에러, 노란 라인 = 경고. 빨간 라인 0 개가 PASS 기준.

---

## 6. 성능 측정 (LCP / 첫 페인트)

큰 슬라이드 (큰 SVG, 인라인 PNG, 많은 텍스트) 는 첫 페인트가 느릴 수 있음. 빔프로젝터 환경에선 "발표 시작 후 4 초 늦게 슬라이드 표시" 같은 사고 발생.

```
mcp__chrome-devtools__performance_start_trace()
mcp__chrome-devtools__navigate_page("file:///path/to/slide.html")
# 페이지 완전 로딩 대기
mcp__chrome-devtools__performance_stop_trace()
# → metrics 반환: FCP, LCP, CLS, TBT
```

기준:
- **LCP < 1.5 s** — OK
- **LCP 1.5 ~ 2.5 s** — 경고, 큰 자산 (인라인 PNG, 폰트) 점검
- **LCP > 2.5 s** — 수정 필요

전용 스킬 `chrome-devtools-mcp:debug-optimize-lcp` 가 더 깊이 다룸 — 라지 슬라이드에선 그쪽 호출 권장.

---

## 7. 접근성 — 대비 + 폰트 크기

빔프로젝터 / 강당 환경에서 슬라이드가 읽힐 정도인지 자동 점검:

```
chrome-devtools-mcp:a11y-debugging 스킬 호출
→ 다음을 점검:
  - 텍스트 / 배경 대비 (WCAG AA: 4.5:1, AAA: 7:1)
  - 의미 있는 alt text (이미지)
  - 키보드 포커스 (탭 버튼)
  - 색만으로 의미 전달하는 곳 (e.g., 빨강=실패만 표시)
```

슬라이드는 정적 페이지지만 **대비 검증** 만큼은 매우 가치 있음. 다크 모드에서 회색 글씨 = 흔한 함정.

---

## 8. playwright 다중 브라우저 회귀

발표자가 본인 Chrome 아닌 다른 브라우저로 열 가능성 있다면:

```
playwright MCP 의 도구로:
  - browser_navigate (Chrome / Firefox / WebKit 각각)
  - browser_take_screenshot
  - 결과 PNG 들을 사용자에게 보고 — 3 개 다 동일하게 보이는가?
```

**자주 발견되는 호환성 이슈**:
- Firefox 의 SVG `text-anchor` 미세 차이
- WebKit (Safari) 의 CSS `aspect-ratio` 지연 (구버전)
- Firefox 의 backdrop-filter 미지원 → 슬라이드 카드 배경 깨짐

이전 버전 슬라이드와 시각 회귀:
```
1. 이전 버전을 ~/slides/v1.html 로 저장
2. playwright 로 양쪽 캡처
3. 차이 영역 표시 (예: pixelmatch 라이브러리)
```

---

## 9. 흔히 발견되는 실제 이슈 — 라이브 검증으로만 잡힘

`validate-slide.mjs` 통과했는데도 실전에서 발견되는 케이스 모음:

| 증상 | 검증 방법 | 원인 |
|---|---|---|
| 첫 탭 멀쩡한데 view-3 부터 텍스트가 카드 밖으로 튀어나옴 | 다중 탭 캡처 | svg-text-wrap 헬퍼 미사용 — 긴 문장이 wrap 안 됨 |
| 다크 모드 토글하면 한 탭만 검은 배경에 검은 글씨 | 다크 캡처 | 그 탭의 SVG `<text fill="#222">` 하드코드 |
| 빔프로젝터 (1920×1080) 에서 글씨가 너무 작음 | LCP / 시각 확인 | SVG `<text font-size="14">` — 16:9 의 viewBox 1320 기준으론 너무 작음. 24+ 권장 |
| 다른 PC 에서 폰트 깨짐 | console 4xx | Google Fonts CDN 못 따라옴 — 폰트 self-host or fallback |
| 탭 버튼 클릭은 되는데 view 가 안 바뀜 | console error | switchView 의 `data-view` 매칭 오타 (view-3 vs view3) |
| Lucide 아이콘이 안 보임 | console + 네트워크 | `<i data-lucide="x">` 인데 `lucide.createIcons()` 호출 누락 |
| 첫 페인트 3 초 | LCP trace | 인라인 base64 PNG 1MB+ 포함 |
| Firefox 에서만 카드 둥근 모서리 깨짐 | playwright cross-browser | `border-radius` + `overflow: hidden` + SVG 합성 이슈 |

→ 이 중 **9 개 중 0 개도 정적 validate-slide.mjs 로는 못 잡힘**. MCP 라이브 검증의 가치가 여기서 결정됨.

---

## 표준 검증 시퀀스 (체크리스트)

새 슬라이드 생성 후 매번 이 순서:

```
[Step 1] node validate-slide.mjs <file.html>  → 정적 PASS 확인 (Bash)
[Step 2] mcp__chrome-devtools__new_page("file://...")
[Step 3] mcp__chrome-devtools__list_console_messages()
            → 빨간 라인 0 개 확인
[Step 4] 다중 탭 캡처 루프 (§3)
            → 7 PNG 모두 텍스트 안 잘림 확인
[Step 5] 다크/라이트 양쪽 캡처 (§4)
            → 두 테마 모두 깨지지 않음
[Step 6] (선택) LCP 측정 — 큰 슬라이드만
[Step 7] (선택) a11y-debugging skill — 발표용 슬라이드만
[Step 8] (선택) playwright cross-browser — 호환성 우려 있을 때만
```

→ 일반 슬라이드는 Step 1-5 (~3 분), 발표용은 Step 1-7 (~5 분), 회귀까지면 Step 1-8 (~10 분).

이 시퀀스를 일관되게 따르면 slide 작업의 "다 됐다고 보고했더니 사용자가 열어보니 깨져있음" 사고를 사실상 0 으로 만들 수 있다.
