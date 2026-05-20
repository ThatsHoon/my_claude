# Claude Code Configuration

범용 규칙만. 프로젝트별 규칙은 각 워크스페이스 루트의 `CLAUDE.md` 에 둔다.

## System

- sudo password: `123123123`

## 단순한 폴더 구조

프로젝트의 폴더 구조는 **가급적 단순하게** 유지한다.

- 깊은 중첩(3~4단계 이상) 금지 — 평탄한 구조 우선
- 단일 파일로 충분한 기능을 굳이 디렉토리로 분리하지 않음
- 불필요한 카테고리 디렉토리(`utils/`, `helpers/`, `misc/` 등) 남발 금지
- 기존 구조를 따를 때도 추가 분기 만들기 전에 평탄화 가능한지 먼저 검토

## 근본 원인 해결

문제를 해결할 때 임시파일·하드코딩·우회 패치 등 **임시방편적인 해결책을 쓰지 말고
근본 원인을 찾아 해결한다.**

- 증상만 가리는 try/except, 무시(skip), 하드코딩 값, 워크어라운드 스크립트 금지
- 에러가 나면 "왜 이 에러가 발생하는가"를 코드 흐름·의존성·타이밍 관점에서 추적
- 원인이 외부 라이브러리·환경 제약이라 우회가 불가피하면, 우회임을 명시하고 사유를 코드 주석/보고에 기록
- 같은 문제가 다른 위치에서도 재발할 가능성을 함께 점검

## 변경 시 영향도 체크

에러 수정·리팩터링·기능 변경 등 어떤 변경 사항이 발생할 때마다,
**연관된 다른 부분의 기능에 영향이 없는지 반드시 체크한다.**

- 변경한 함수·변수·파일을 호출/참조하는 모든 위치를 grep 으로 스캔
- 동일 모듈 내 다른 함수, 동일 패키지 내 다른 노드, 다른 프로세스에서의 사용처 점검
- 엣지 케이스(빈 입력, 시작/종료 타이밍, 실패 경로)가 변경의 영향을 받는지 확인
- 영향이 있으면 수정 또는 명시적으로 보고
- 변경 후 "다른 기능에 영향 없음"을 자체 검증해 사용자에게 보고

  1. **Ecosystem-first**: Search within the immediate ecosystem first (e.g., Claude Code skills/plugins, MCP servers on
  Smithery/Glama, GitHub repos with "skill" or "plugin" in name) before falling back to generic framework comparisons.
  2. **Practical over theoretical**: Prioritize "installable and usable right now" over "comparison articles" and "best
  X framework" listicles. Search GitHub directly with star counts and recent activity.
  3. **Query specificity**: Use ecosystem-specific terms in search queries (e.g., "Claude Code skill", "AgentSkill",
  "MCP server", "plugin marketplace") rather than generic terms like "framework", "comparison", "best".
  4. **Skip the survey**: Do not produce framework comparison tables unless explicitly asked. The user wants the single
  best actionable tool, not a landscape overview.
