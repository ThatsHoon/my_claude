# Reference example — cobot2 architecture-playground.html 줄번호 색인

> 기준 예시: `/home/hoon/cobot_ws/docs/cobot2/architecture-playground.html` (4906 라인). 새 슬라이드 만들 때 라인 번호로 참조.
> **이 파일은 READ-ONLY**. 절대 수정하지 말 것. 패턴 추출용으로만 사용.

## 라인 색인

| 범위 | 내용 |
|---|---|
| L1~7 | `<!DOCTYPE html>` + `<head>` 메타 |
| L8~69 | **CSS variables** — `:root` (dark) + `[data-theme="light"]` (HOMIE light) |
| L72~115 | Body 구조 + 탭 컨테이너 |
| L120~198 | **공통 유틸 CSS 클래스** — `.flow-title-text`, `.flow-section-num`, `.flow-section-label`, `.flow-section-desc`, `.flow-group-divider` |
| L200~280 | 노드 카드 / 엣지 라벨 / 마커 CSS |
| L281~285 | **aspect-ratio + min-height** 적용 — `#training-result-diagram` |
| L580~590 | **탭 버튼 9 개** — `<button class="tab" data-view="...">` |
| L591~610 | 첫 view 컨테이너 (`.view.view-system.active`) |
| L817~828 | **training 탭 view + SVG viewBox** |
| L829~870 | **training-result + training-history view + SVG viewBox** (16:9 1320×742) |
| L964~968 | **svg() helper 함수** (6 줄) |
| L1283~1300 | precomputeBundling — 엣지 묶기 |
| L4123~4165 | **TRAINING_RESULT 데이터 객체** (meta / metrics / perClass / dataset / techniques) |
| L4169~4185 | `renderTrainingResult()` 시작 — clear + title block |
| L4189~4220 | metric pills hero row (8 pills, 균등 분할) |
| L4220~4470 | 3-column layout — Dataset / Techniques / Per-class AP@50 |
| L4500~4540 | `TRAINING_HISTORY` 데이터 객체 (5 versions + lesson 필드) |
| L4550~4720 | `renderTrainingHistory()` — timeline 5 cards + 변경 컨테이너 5 cards |
| L4720~4812 | **`switchView()` 함수** — 7 탭 분기 (system / stack / workflow / flow / db / gripper / training / training-result / training-history) |
| L4830~4850 | **`applyTheme()` 함수** — 모든 view 재렌더 분기 |
| L4857~4861 | `bootstrap()` — localStorage 테마 복원 |

## 7 탭 (정확한 data-view 값)

| 탭 이름 | data-view | 레이아웃 매칭 |
|---|---|---|
| 시스템 노드 구조 | `system` | architecture-diagram |
| 기술 스택 | `stack` | 3-column |
| 전체 워크플로우 | `workflow` | timeline + parallel flows |
| 명령 시퀀스 흐름 | `flow` | sequence diagram |
| DB 구조 | `db` | HTML (2 슬라이드) |
| Challenge: 동적 그리퍼 진입 | `gripper` | HTML article + diagram |
| Model Training | `training` | metric-cards + 3-column + bar chart |
| Training Result | `training-result` | **3-column** (dataset / techniques / per-class) |
| Training History | `training-history` | **timeline-history** (5 versions + lesson) |

## 활용 방법

새 슬라이드 만들 때:

1. **viewBox 골격** 복사: L817~870 (단일 svg + grid pattern + content `<g>`)
2. **CSS variables**: L8~69 → 새 테마로 token override
3. **공통 유틸 클래스**: L120~198 → 그대로 복사 (모든 슬라이드 공통)
4. **svg() helper**: L964~968 → 그대로
5. **switchView / applyTheme**: L4720~4850 의 패턴 그대로 새 탭에 맞게 분기 추가
6. **데이터 객체**: L4123~4165 (TRAINING_RESULT) 형태로 새 객체 정의
7. **render 함수**: L4169~4470 (renderTrainingResult) 형태로 새 함수 작성

## 자주 인용되는 코드 (10 줄 미만)

### svg() helper (L964~968)
```js
const SVG_NS = 'http://www.w3.org/2000/svg';
function svg(tag, attrs = {}, ...children) {
  const e = document.createElementNS(SVG_NS, tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (k === 'text') e.textContent = v;
    else if (v != null) e.setAttribute(k, v);
  }
  return e;
}
```

### switchView 패턴 (L4720~4730)
```js
function switchView(view) {
  state.view = view;
  document.querySelectorAll('.tab').forEach(t =>
    t.classList.toggle('active', t.dataset.view === view));
  document.querySelectorAll('.view').forEach(v =>
    v.classList.toggle('active', v.classList.contains(`view-${view}`)));
  if (view === 'system') { render(); renderMeta(); }
  else if (view === 'training-result') renderTrainingResult();
  // ... 다른 분기
}
```

### applyTheme 패턴 (L4830~4850)
```js
function applyTheme(theme) {
  document.body.setAttribute('data-theme', theme);
  localStorage.setItem('cobot2-theme', theme);
  if (state.view === 'system') render();
  else if (state.view === 'training-result') renderTrainingResult();
  else if (state.view === 'training-history') renderTrainingHistory();
  // ★ 새 탭 추가 시 반드시 여기에도 분기!
}
```
