# my_claude — Claude Code 설정 미러

다른 PC 에서 Claude Code 를 설치할 때, AI 가 이 레포의 내용을 그대로 읽어
**현재 PC 의 Claude Code 설정을 복제**하도록 만든 저장소다.

> 사용 방법: 새 PC 에서 Claude Code 를 띄우고 다음과 같이 지시하면 된다.
>
> > "https://github.com/ThatsHoon/my_claude 의 내용을 그대로 적용해줘."

AI 는 [APPLY.md](APPLY.md) 의 절차를 따라 CLAUDE.md, 플러그인, 사용자 스킬을
동일하게 세팅한다.

## 레포 구성

| 경로 | 내용 |
| --- | --- |
| `APPLY.md` | 새 PC 에서 적용할 때 AI 가 따라야 할 절차 |
| `settings.json` | `~/.claude/settings.json` 전체 (플러그인 + 권한 + 모델 설정) |
| `claude_md/global.md` | `~/CLAUDE.md` (사용자 전역 규칙) |
| `claude_md/home.md` | `~/.claude/CLAUDE.md` (홈 디렉토리 규칙) |
| `claude_md/cobot_ws.md` | `~/cobot_ws/CLAUDE.md` (Doosan m0609 워크스페이스 규칙) |
| `plugins/enabled_plugins.json` | `settings.json` 의 `enabledPlugins` 섹션 |
| `plugins/installed_plugins.json` | 설치할 마켓플레이스별 플러그인 목록 |
| `plugins/known_marketplaces.json` | 등록할 플러그인 마켓 출처 |
| `skills/<이름>/` | 활성 사용자 스킬 — `~/.claude/skills/<이름>/` 에 복사 |
| `skills/legacy/<이름>/` | 비활성 스킬 — 특정 환경에서만 필요하거나 deprecated |

## 포함된 사용자 스킬

### 활성 스킬 (`skills/`)

| 스킬 | 설명 |
| --- | --- |
| `html-ppt` | 36 테마 / 31 레이아웃 / 27 CSS + 20 canvas FX / presenter mode. 단일 HTML PPT 데크 |
| `ros2-architect` | ROS 2 아키텍처/엔지니어링 전반 |
| `mcp-builder` | MCP 서버 작성 가이드 (FastMCP / MCP TypeScript SDK) |
| `build-mcpb` | `.mcpb` 패키징 (Node/Python 런타임 번들링) |

### Legacy 스킬 (`skills/legacy/`)

특정 환경 전용이거나 더 이상 활발히 사용하지 않는 스킬.
필요 시 `~/.claude/skills/` 로 복사하여 활성화.

| 스킬 | 설명 |
| --- | --- |
| `architecture-diagram` | 다크 테마 HTML+SVG 인프라/네트워크 토폴로지 다이어그램 |
| `configdb-reverse` | Wuthering Waves ConfigDB FlatBuffer 역설계 |
| `doosan-robotics` | Doosan m0609 (DRL/DRFL/doosan-robot2) 작업용 |
| `rive-web` | Rive 인터랙티브 애니메이션 웹 통합 |
| `isaac-sim-bridge` | NVIDIA Isaac Sim / Isaac Lab / Isaac ROS 도메인 지식 |
| `isaac-sim-mcp` | `isaac-sim-mcp` 서버를 통한 라이브 Isaac Sim 제어 |
| `gp-quadruped` | Boston Dynamics Spot 4족 경계초소 로봇 (cobot3 GP) |
