# my_claude — Claude Code 설정 미러

다른 PC 에서 Claude Code 를 설치할 때, AI 가 이 레포의 내용을 그대로 읽어
**현재 PC 의 Claude Code 설정을 복제**하도록 만든 저장소다.

> 사용 방법: 새 PC 에서 Claude Code 를 띄우고 다음과 같이 지시하면 된다.
>
> > "https://github.com/ThatsHoon/my_claude 의 내용을 그대로 적용해줘."

AI 는 [APPLY.md](APPLY.md) 의 절차를 따라 CLAUDE.md, 플러그인, 사용자 스킬,
그리고 AIRIS MCP Gateway 까지 동일하게 세팅한다.

## 레포 구성

| 경로 | 내용 |
| --- | --- |
| `APPLY.md` | 새 PC 에서 적용할 때 AI 가 따라야 할 절차 |
| `claude_md/global.md` | `~/CLAUDE.md` (사용자 전역 규칙) 의 내용 |
| `claude_md/cobot_ws.md` | `~/cobot_ws/CLAUDE.md` (Doosan m0609 워크스페이스 규칙) 의 내용 |
| `plugins/enabled_plugins.json` | `~/.claude/settings.json` 의 `enabledPlugins` 섹션. `context7`/`serena` 는 AIRIS 와 중복되어 의도적으로 `false` |
| `plugins/installed_plugins.json` | 설치할 마켓플레이스별 플러그인 목록 (26 개) |
| `plugins/known_marketplaces.json` | 등록할 플러그인 마켓 출처 (5 개) |
| `skills/<이름>/` | 필수 사용자 스킬 — `~/.claude/skills/<이름>/` 에 그대로 복사 |
| `skills/optional/<이름>/` | 선택 사용자 스킬 — 설치 전 사용자 확인 필요 |

## 포함된 사용자 스킬

### 필수 스킬 (항상 설치)

마켓플레이스 플러그인에 없는, 로컬에서 직접 만들었거나 외부 레포에서 가져온
스킬을 같이 미러링한다. 새 PC 에서는 `skills/<이름>/` 폴더를
`~/.claude/skills/<이름>/` 로 복사하면 된다.

- `html-ppt` — 36 테마 / 31 레이아웃 / 27 CSS + 20 canvas FX / presenter mode (S 키). 단일 HTML PPT 데크 (ThatsHoon/html-ppt-skill 미러)
- `architecture-diagram` — 다크 테마 HTML+SVG 인프라/네트워크 토폴로지 다이어그램. Copy/PNG/PDF 내장 (ThatsHoon/architecture-diagram-generator 미러)
- `ros2-architect` — ROS 2 아키텍처/엔지니어링 전반
- `doosan-robotics` — Doosan m0609 (DRL/DRFL/doosan-robot2) 작업용
- `mcp-builder` — MCP 서버 작성 가이드 (FastMCP / MCP TypeScript SDK)
- `build-mcpb` — `.mcpb` 패키징 (Node/Python 런타임 번들링)
- `rive-web` — Rive 인터랙티브 애니메이션 웹 통합 (`@rive-app/*` 런타임)

### 선택 스킬 (특정 환경 전용 — 설치 전 사용자 확인 필요)

`skills/optional/` 아래에 위치. APPLY.md §5-2 에서 AI 가 사용자에게
각 스킬을 설치할지 개별적으로 묻는다.

- `isaac-sim-bridge` — NVIDIA Isaac Sim / Isaac Lab / Isaac ROS 도메인 지식 (USD/PhysX/OG). Isaac Sim 작업 PC 에서만 필요
- `isaac-sim-mcp` — `isaac-sim-mcp` 서버를 통한 라이브 Isaac Sim 제어 playbook. `isaac-sim-bridge` 와 보완관계. Isaac Sim MCP 서버 사용 PC 에서만 필요
- `gp-quadruped` — Boston Dynamics Spot 4족 경계초소 로봇 (cobot3 GP) 컨텍스트. Spot 로봇 작업 PC 에서만 필요

## MCP Gateway (AIRIS)

이 PC 는 [AIRIS MCP Gateway](https://github.com/agiletec-inc/airis-mcp-gateway)
를 단일 허브로 사용한다. context7 / serena / chrome-devtools / supabase /
github 등 20+ MCP 서버를 게이트웨이 한 개 뒤에 집약. Claude Code 에
`airis-mcp-gateway` 한 줄만 등록하면 모든 backend 접근 가능. observability,
on-demand lifecycle, intelligent noise reduction 제공.

설치 절차는 [APPLY.md](APPLY.md) §6 참조.
