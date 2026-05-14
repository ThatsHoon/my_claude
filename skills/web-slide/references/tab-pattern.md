# 탭 패턴 — switchView + applyTheme + state 객체

> 단일 HTML 안에서 N 개 탭을 라우팅하는 표준 패턴. 함정 #1 (양분기 동기 누락) 의 해결책.

## 1. State 객체 (단일 출처)

```js
const state = {
  view: 'overview',  // 현재 활성 탭 id (data-view 값과 일치)
  theme: 'dark',     // 'dark' | 'light'
};
```

모든 컨트롤 변경은 `state` 를 업데이트한 후 적절한 render 호출.

## 2. HTML 구조

```html
<div class="tabs">
  <button class="tab active" data-view="overview">Overview</button>
  <button class="tab"        data-view="system">System</button>
  <button class="tab"        data-view="metrics">Metrics</button>
</div>

<div class="view view-overview active">
  <svg viewBox="0 0 1320 742" ...><g id="overview-content"></g></svg>
</div>
<div class="view view-system">
  <svg viewBox="0 0 1320 742" ...><g id="system-content"></g></svg>
</div>
<div class="view view-metrics">
  <svg viewBox="0 0 1320 742" ...><g id="metrics-content"></g></svg>
</div>
```

규칙:
- `data-view="X"` ↔ `class="view view-X"` 정확한 1:1 매칭
- `.active` 클래스로 표시/숨김 (CSS `.view { display: none; } .view.active { display: block; }`)
- 첫 번째 탭에 초기 `.active` 적용

## 3. switchView() 함수

```js
function switchView(view) {
  state.view = view;

  // 탭 버튼 active 토글
  document.querySelectorAll('.tab').forEach(t =>
    t.classList.toggle('active', t.dataset.view === view)
  );
  // view 컨테이너 active 토글
  document.querySelectorAll('.view').forEach(v =>
    v.classList.toggle('active', v.classList.contains(`view-${view}`))
  );

  // 탭별 render 호출 (★ 새 탭 추가 시 분기 추가)
  if (view === 'overview') {
    renderOverview();
  } else if (view === 'system') {
    renderSystem();
  } else if (view === 'metrics') {
    renderMetrics();
  }
}
```

## 4. applyTheme() 함수

```js
function applyTheme(theme) {
  state.theme = theme;
  document.body.setAttribute('data-theme', theme);
  try { localStorage.setItem('myapp-theme', theme); } catch (e) {}

  // CSS variables 는 [data-theme="light"] 가 자동 적용.
  // 하지만 SVG 안 hardcoded color 는 다시 그려야 갱신됨.
  // ★ 새 탭 추가 시 여기에도 분기 추가
  if (state.view === 'overview') renderOverview();
  else if (state.view === 'system') renderSystem();
  else if (state.view === 'metrics') renderMetrics();
}

function toggleTheme() {
  applyTheme(state.theme === 'dark' ? 'light' : 'dark');
}
```

## 5. 부팅

```js
function bootstrap() {
  // 이벤트 바인딩
  document.querySelectorAll('.tab').forEach(t => {
    t.addEventListener('click', () => switchView(t.dataset.view));
  });
  document.getElementById('theme-toggle')
    ?.addEventListener('click', toggleTheme);

  // 저장된 테마 복원
  let savedTheme = 'dark';
  try { savedTheme = localStorage.getItem('myapp-theme') || 'dark'; }
  catch (e) {}
  applyTheme(savedTheme);

  // 초기 뷰 렌더
  switchView(state.view);
}
document.addEventListener('DOMContentLoaded', bootstrap);
```

## 6. 데이터 객체 + render 분리

```js
const OVERVIEW = {
  title: '프로젝트 X',
  bullets: ['포인트 A', '포인트 B', '포인트 C'],
};

const $overviewContent = document.getElementById('overview-content');

function renderOverview() {
  clear($overviewContent);
  $overviewContent.appendChild(svg('text', {
    class: 'flow-title-text', x: 30, y: 60, text: OVERVIEW.title,
  }));
  OVERVIEW.bullets.forEach((b, i) => {
    $overviewContent.appendChild(svg('text', {
      x: 30, y: 110 + i * 24,
      fill: 'var(--text)', 'font-size': 14,
      text: '· ' + b,
    }));
  });
}
```

## 7. 새 탭 추가 — 6 위치 체크리스트

| # | 위치 | 코드 |
|---|---|---|
| 1 | `<div class="tabs">` | `<button class="tab" data-view="X">X 이름</button>` |
| 2 | `<main>` 안 | `<div class="view view-X"><svg ...><g id="X-content"></g></svg></div>` |
| 3 | `switchView()` if-chain | `else if (view === 'X') { renderX(); }` |
| 4 | `applyTheme()` if-chain | `else if (state.view === 'X') renderX();` |
| 5 | 데이터 객체 | `const X_DATA = {...};` |
| 6 | render 함수 | `function renderX() { clear(...); ... }` |

**1 위치라도 빠지면** `scripts/validate-slide.mjs` 가 ERROR. 6 위치를 동시에 수정하기 위해서 새 탭은 항상 multi-edit 으로 한 번에 처리.

## 8. 흡수 출처

이 패턴은 다음을 통합/단순화한 것:
- **playground skill** (`~/.claude/plugins/cache/claude-plugins-official/playground/.../SKILL.md`): state + updateAll() 패턴 (인터랙티브 controls 용도. 슬라이드에서는 tab 클릭과 theme 토글만 사용)
- **cobot2 architecture-playground.html**: `switchView` (L4720~4812) + `applyTheme` (L4830~4850) — 7 탭으로 검증된 양분기 패턴
