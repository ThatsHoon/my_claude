# Common Pitfalls — 5 함정 + 탐지법

> 새 슬라이드 만들거나 탭 추가할 때 가장 자주 일어나는 5 함정. 각 항목 — 재현 조건 / 증상 / 탐지법 / 해결.

---

## 함정 #1 — switchView / applyTheme 양분기 동기 누락

**재현**: 새 탭 `X` 추가했는데 `switchView()` 에만 분기 넣고 `applyTheme()` 에는 안 넣음. 또는 그 반대.

**증상**:
- 탭을 클릭하면 정상 렌더 ✓
- 하지만 dark/light 토글 후 `X` 탭 진입 → **빈 화면**
- 또는 페이지 로드 직후 첫 진입 → 빈 화면

**탐지법**:
```bash
node ~/.claude/skills/web-slide/scripts/validate-slide.mjs <slide.html>
# → ERROR: tab 'X' in switchView but missing in applyTheme
```

**해결**: 5-way diff 가 정확히 일치하도록 6 위치 모두 패치. `references/tab-pattern.md` §7 체크리스트.

---

## 함정 #2 — SVG `<text>` 자동 wrap 없음

**재현**: 긴 한국어/영문 문장을 한 `<text>` 안에 넣음.

**증상**: 텍스트가 카드/슬라이드 우측 경계를 넘어 잘림. responsive 안 됨.

**탐지법**:
- validate-slide.mjs 의 WARNING: `<text x="..."> with x > 1290`
- 시각: chrome-devtools-mcp `take_screenshot` 후 슬라이드 우측 경계 확인

**해결**:
```js
// snippets/svg-text-wrap.js 의 헬퍼 사용
import { wrapSvgText } from './snippets/svg-text-wrap.js';
wrapSvgText(longText, maxChars).forEach((ln, i) => {
  $content.appendChild(svg('text', { x, y: y + i * lineHeight, text: ln }));
});
```

또는 `<text><tspan>line1</tspan><tspan x="0" dy="1.2em">line2</tspan></text>` 수동 분할.

---

## 함정 #3 — viewBox 좌표 = 픽셀 (그러나 슬라이드 폭 = 1320 고정 아님)

**재현**: 사용자가 슬라이드를 풀스크린 (예: 2560 px) 으로 봄. `x: 1290` 으로 우측 끝에 둔 텍스트가 잘 보임. 작은 창에서도 viewBox 가 스케일되어 비율 유지됨.

**증상**: 슬라이드 보기 자체는 정상 — 그러나 코딩 시 1320 폭이라는 사실을 잊고 `x: 1500` 같이 viewBox 밖에 좌표 둠 → SVG 안 보임.

**탐지법**:
- validate-slide.mjs 의 WARNING: `<text x="1500">` 또는 `<rect x="0" width="1400">`
- 시각: 콘텐츠 일부가 안 보임 + viewBox 외각이 잘림

**해결**: 항상 `30 ≤ x ≤ 1290`, `30 ≤ y ≤ 712` 안에서 작성. `references/16-9-layout.md` 의 grid 가이드.

---

## 함정 #4 — 한영 폰트 사이즈 시각 불균형

**재현**: `font-size: 14` 로 영문 라벨과 한글 라벨을 같은 카드에 배치.

**증상**: 한글이 영문 대비 시각적으로 1~2 px 작아 보임. 가독성 떨어짐.

**탐지법**:
- 시각: 카드 안 영/한 혼용 라벨을 같이 본 후 크기 비교
- 한글 라인이 영문 라인보다 "가벼워" 보이면 함정 발생

**해결**:
- 한글 라벨 font-size 를 + 1~2 px (영문 14 → 한글 15~16)
- 또는 한글-only / 영문-only 카드로 분리
- 또는 영문 폰트의 `font-feature-settings: "kern"` 조정

---

## 함정 #5 — 데이터 객체 ↔ render 함수 동기 누락

**재현**: 데이터 객체에 새 필드 `lesson` 추가했는데 `renderX()` 함수가 그걸 안 그림.

**증상**: 침묵 누락 — 에러 없음, 단지 새 필드가 화면에 없음.

**탐지법**:
- validate-slide.mjs 에 자동 검사 항목 **없음** (동적 분석 필요)
- PR/diff 리뷰 시 데이터 변경 1줄 → render 함수 수정 N줄 페어가 보이는지 확인
- 시각: chrome-devtools-mcp 스크린샷 후 누락된 필드 확인

**해결**: 데이터 객체와 render 함수는 항상 같은 commit 에서 함께 수정. 작업 시 "데이터 추가 → render 코드 → 시각 확인" 3단 흐름 권장.

---

## 보조 함정 — raw hex 색 사용

**재현**: SVG 안에 `fill="#2dd4bf"` 같이 hex 직접 사용.

**증상**: 테마 토글 시 색이 변경되지 않음. dark 색이 light 모드에서도 그대로 → 시각적 충돌.

**탐지법**:
- validate-slide.mjs 의 INFO: SVG body 의 hex 개수 (defs 외)
- 시각: light 모드에서 어두운 색이 그대로 보이거나, dark 에서 너무 밝음

**해결**: `fill="var(--accent)"` 등 토큰 사용. `<defs>` 안 marker / gradient 는 raw hex OK (테마별로 따로 정의하거나 단일).

---

## 빠른 체크리스트

새 탭 추가 시 다음 5개를 모두 ✓:

- [ ] `data-view="X"` ↔ `view view-X` 매칭
- [ ] `switchView` if-chain 에 `view === 'X'` 분기
- [ ] `applyTheme` if-chain 에 `state.view === 'X'` 분기
- [ ] 데이터 객체 + render 함수 페어 추가
- [ ] 모든 좌표 `30 ≤ x ≤ 1290`, `30 ≤ y ≤ 712`

콘텐츠 작성 시:

- [ ] 긴 텍스트는 `wrapSvgText()` 또는 `<tspan>` 분할
- [ ] 색은 `var(--...)` 토큰 사용 (defs 외에서 raw hex 금지)
- [ ] 한글 라벨은 영문보다 +1~2 px

마지막 검증:

- [ ] `node scripts/validate-slide.mjs <file>` exit 0
- [ ] 모든 탭 클릭 + 정상 렌더
- [ ] dark/light 토글 후 모든 탭 재진입 + 정상 렌더
