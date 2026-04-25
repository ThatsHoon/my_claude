# My Claude Code Configuration

개인 Claude Code 환경 설정 — MCP 서버, Plugins, Skills 목록 정리

- **OS**: Ubuntu 22.04.5 LTS (Linux 6.8.0-110-generic)
- **Model**: claude-opus-4-7 (1M context)
- **Primary projects**: `~/cobot_ws` (ROS2/DSR), `~/Rokey_1` (프론트엔드/키오스크)
- **Last updated**: 2026-04-25

---

## MCP Servers

Claude Code는 **user scope**와 **project scope** 두 계층에서 MCP 서버를 로드한다.
- user scope: `~/.claude.json` 내 `mcpServers` — 모든 프로젝트 공통
- project scope: 각 프로젝트 디렉토리의 `.mcp.json` 또는 `~/.claude.json` `projects.<path>.mcpServers`

### User scope (글로벌)

| 이름 | 타입 | 설명 |
|------|------|------|
| `google-slides` | stdio (local Node) | Google Slides 조작 — `~/google-slides-mcp/build/index.js` 로컬 빌드. OAuth 토큰은 `env`에 주입 (repo 에는 비공개) |

### Project scope — `~/Rokey_1`, `~/cobot_ws`

두 프로젝트 모두 동일한 4개 서버를 stdio 로 기동한다.

| 이름 | 커맨드 | 용도 |
|------|--------|------|
| `context7` | `npx -y @upstash/context7-mcp` | 라이브러리 공식 문서 최신 조회 (React, Next.js, Tailwind, ROS2 등) |
| `sequential-thinking` | `npx -y @modelcontextprotocol/server-sequential-thinking` | 복잡 문제 단계별 추론 |
| `playwright` | `npx -y @playwright/mcp` | 브라우저 자동화 / E2E 테스트 / 스크린샷 |
| `serena` | `uvx --from git+https://github.com/oraios/serena serena start-mcp-server` | 시맨틱 코드 탐색 — 심볼 단위 read/edit |

> `~/cobot_ws` 의 serena 만 절대경로(`/home/hoon/.local/bin/uvx`) 사용. PATH 미설정 세션 대비.

### Project scope — `~` (홈 디렉토리)

홈을 프로젝트로 열 때만 활성화되는 Smithery 호스팅 HTTP MCP 3종:

| 이름 | URL |
|------|-----|
| `context7-mcp` | `https://server.smithery.ai/@upstash/context7-mcp/mcp` |
| `server-sequential-thinking` | `https://server.smithery.ai/@smithery-ai/server-sequential-thinking/mcp` |
| `serena` | `https://server.smithery.ai/chris/serena/mcp` |

### Plugin-provided MCP

설치된 플러그인이 자체 MCP 서버를 가져오는 경우:

| Plugin | MCP | URL |
|--------|-----|-----|
| `eraser` | `eraser` | `https://app.eraser.io/api/mcp` (HTTP) — 아키텍처·플로우차트·BPMN·시퀀스·ERD 다이어그램 생성 |

### 등록 명령어 레퍼런스

```bash
# 프로젝트별 stdio 서버 재등록 (해당 프로젝트 루트에서)
claude mcp add context7            -- npx -y @upstash/context7-mcp
claude mcp add sequential-thinking -- npx -y @modelcontextprotocol/server-sequential-thinking
claude mcp add playwright          -- npx -y @playwright/mcp
claude mcp add serena              -- uvx --from git+https://github.com/oraios/serena serena start-mcp-server

# google-slides (user scope, 로컬 빌드)
claude mcp add --scope user google-slides -- node /home/hoon/google-slides-mcp/build/index.js
# env 로 GOOGLE_CLIENT_ID / GOOGLE_CLIENT_SECRET / GOOGLE_REFRESH_TOKEN 주입 필요
```

---

## Plugins

Claude Code 플러그인은 `~/.claude/plugins/` 아래에 설치되며, 크게 세 경로로 들어온다.

1. **Marketplace 설치** (`/plugin install <name>@<marketplace>`): `~/.claude/plugins/cache/<marketplace>/<plugin>/<version>/`
2. **로컬/커스텀 플러그인**: `~/.claude/plugins/<name>/` 에 직접 배치
3. **Marketplace 등록**: `~/.claude/plugins/known_marketplaces.json`

### Enabled (settings 기준)

`~/.claude/settings.json` 의 `enabledPlugins`:

| Plugin | Marketplace | Version | 설명 |
|--------|-------------|---------|------|
| `frontend-design` | `claude-plugins-official` (anthropics) | unknown | UI/UX 구현 프론트엔드 설계 skill |
| `frontend-slides` | `frontend-slides` (zarazhangrui) | 1.0.0 | Zero-dependency HTML 프레젠테이션 생성기 (12 테마 + PPT 변환) |

### Registered marketplaces

`~/.claude/plugins/known_marketplaces.json`:

| Marketplace | Source |
|-------------|--------|
| `claude-plugins-official` | github:anthropics/claude-plugins-official |
| `frontend-slides` | github:zarazhangrui/frontend-slides |

### Custom / local plugins (marketplace 外)

`~/.claude/plugins/` 직하에 배치된 디렉토리 형태의 플러그인:

| Plugin | 출처 | 역할 |
|--------|------|------|
| `doosan-robotics` | 직접 작성 (ErifKim) | 두산 로보틱스 DRL/DRFL/ROS2/MoveIt2/알고리즘 4종 skill 번들 |
| `awesome-skills` | github:ComposioHQ/awesome-claude-skills | 범용 생산성 skill 모음 7종 |
| `eraser` | github:eraserlabs/eraserio/claude-plugins/eraser | 다이어그램 생성 skill + MCP 서버 |

---

## Skills

Skills 는 `~/.claude/plugins/<plugin>/skills/<skill>/SKILL.md` 에 저장된다. description 키워드 매칭으로 자동 활성화되거나, `/skill-name <args>` 로 명시 호출한다.

### doosan-robotics (custom, 4 skills)

본 repo `skills/` 아래 전체 내용 복사본 보관.

| Skill | 트리거 키워드 | 범위 |
|-------|----------------|------|
| `doosan-robotics` | movej, movel, DRL, DRFL, CDRFLEx, 두산 로봇, DSR_ROBOT2 | **로봇 모델 m0609 고정.** DRL Python v2.12.1 전체 + DRFL C++ API (CDRFLEx, GL013303). 모션/서보/힘/컴플라이언스/I-O/통신/비전/용접/수학/Threading/RT 제어 전 영역 |
| `doosan-robot2-ros2` | doosan-robot2, DSR_ROBOT2, dsr_bringup2, ros2 service/topic, 두산 ROS2 | ROS2 Humble 통합 — launch, 가상/실기 모드, service 호출, 실시간 스트림, MoveIt2 연동, Gazebo |
| `moveit2` | MoveGroupInterface, MoveItPy, PlanningScene, MTC, OMPL/PILZ/CHOMP | MoveIt2 Python/C++ API, 플래너, 충돌·constraint, pick and place |
| `robot-arm-algorithms` | DH, RRT, trajectory, DART, Jacobian IK, 궤적 생성, 상태 머신 | PythonRobotics 기반 알고리즘 레이어. FK/IK, 궤적 생성, 상태 머신, BT, Kalman |

### awesome-skills (ComposioHQ)

출처: [ComposioHQ/awesome-claude-skills](https://github.com/ComposioHQ/awesome-claude-skills)

| Skill | 설명 |
|-------|------|
| `artifacts-builder` | claude.ai 아티팩트용 React+Tailwind+shadcn/ui 멀티 컴포넌트 번들 생성 |
| `changelog-generator` | git 커밋 분석 → 사용자 친화적 changelog 자동 생성 |
| `developer-growth-analysis` | 최근 Claude Code 사용 패턴 분석 → 성장 리포트 Slack DM 발송 |
| `langsmith-fetch` | LangChain/LangGraph 에이전트 실행 트레이스 조회·분석 |
| `mcp-builder` | MCP 서버 설계·구현 가이드 (Python FastMCP / Node MCP SDK) |
| `skill-creator` | 새 Claude Code skill 작성 가이드 |
| `webapp-testing` | Playwright 기반 로컬 웹앱 E2E 테스트 |

### frontend-design (claude-plugins-official)

| Skill | 설명 |
|-------|------|
| `frontend-design` | UI/UX 구현을 위한 프론트엔드 설계 skill |

### frontend-slides (zarazhangrui)

| Skill | 설명 |
|-------|------|
| `frontend-slides` | 단일 HTML 파일 프레젠테이션 생성기 — 12 테마, 뷰포트 100vh 고정, 애니메이션, PPT(.pptx) 변환 지원 |

### eraser (eraserlabs)

| Skill | 설명 |
|-------|------|
| `eraser:diagram` | Eraser.io API 로 아키텍처·플로우차트·BPMN·시퀀스·ERD 다이어그램 생성 (API 토큰 없으면 워터마크) |

---

## 설정 파일 위치

```
~/.claude/
├── settings.json                 # enabledPlugins, extraKnownMarketplaces
├── settings.local.json           # 로컬 권한(allow list)
├── plugins/
│   ├── installed_plugins.json    # marketplace 설치 플러그인 목록
│   ├── known_marketplaces.json   # 등록된 marketplace
│   ├── cache/                    # marketplace 플러그인 실체
│   ├── doosan-robotics/          # 커스텀 플러그인
│   ├── awesome-skills/
│   └── eraser/
└── projects/<path>/memory/       # auto-memory (프로젝트별 영구 메모리)

~/.claude.json                    # user + per-project mcpServers, 세션 상태

# 프로젝트 로컬
<project>/.mcp.json               # 프로젝트 전용 MCP (있는 경우)
<project>/CLAUDE.md               # 프로젝트 규약
```

---

## Skills 호출 방식

```
자동 활성화: SKILL.md frontmatter 의 description 키워드 매칭 시 자동 로드
명시 호출:  /skill-name [arguments]  →  $ARGUMENTS 변수로 전달
플러그인 네임스페이스:  /plugin:skill  (동명 skill 충돌 시)
```

---

## 시스템 / 런타임 버전

서브노드 PC(`~/cobot_ws` 호스트) 기준. ROS2 Humble apt 미러 빌드 타임스탬프는 `20260326` 전후.

### OS / 셸

| 항목 | 버전 |
|------|------|
| OS | Ubuntu 22.04.5 LTS (Jammy) |
| Kernel | 6.8.0-110-generic |
| Shell | bash |

### 언어 런타임

| 도구 | 버전 | 경로/비고 |
|------|------|-----------|
| Python | 3.10.12 | `/usr/bin/python3` (시스템 기본) |
| pip | 22.0.2 | python3.10 dist-packages |
| uv / uvx | 0.11.7 | `~/.local/bin/uvx` (serena MCP 기동에 사용) |
| Node.js | v22.22.2 | `npx` 기반 MCP 서버용 |
| npm | 10.9.7 | |

### ROS2 Humble (apt 패키지)

| 패키지 | 버전 |
|--------|------|
| `ros-humble-desktop` (메타) | 0.10.0 |
| `ros-humble-ros-base` | 0.10.0 |
| `ros-humble-rclpy` | 3.3.21 |
| `ros-humble-rviz2` | 11.2.26 |
| `ros-humble-rqt-common-plugins` | 1.2.0 |
| `ros-humble-tf2` / `tf2-ros` / `tf2-tools` | 0.25.20 |
| `ros-humble-urdf` | 2.6.1 |
| `ros-humble-xacro` | 2.1.1 |
| `ros-humble-robot-state-publisher` | 3.0.3 |
| `ros-humble-joint-state-publisher` | 2.4.0 |
| `ros-humble-controller-manager` / `ros2-control` | 2.53.1 |
| `ros-humble-ros2-controllers` | 2.52.1 |
| `ros-humble-moveit` (메타) | 2.5.9 |
| `ros-humble-gazebo-ros-pkgs` (Classic) | 3.9.0 |
| Gazebo Classic | 11.10.2 |

설치된 rqt 플러그인(전체):
`rqt-action 2.0.1`, `rqt-bag 1.1.6`, `rqt-bag-plugins 1.1.6`, `rqt-console 2.0.3`, `rqt-graph 1.3.2`, `rqt-gui 1.1.9`, `rqt-gui-cpp 1.1.9`, `rqt-gui-py 1.1.9`, `rqt-image-view 1.2.0`, `rqt-msg 1.2.0`, `rqt-plot 1.1.5`, `rqt-publisher 1.5.0`, `rqt-py-common 1.1.9`, `rqt-py-console 1.0.2`, `rqt-reconfigure 1.1.4`, `rqt-service-caller 1.0.5`, `rqt-shell 1.0.2`, `rqt-srv 1.0.3`, `rqt-topic 1.5.1`.

### 빌드 도구

| 도구 | 버전 |
|------|------|
| `colcon-common-extensions` | 0.3.0 |
| `setuptools` | 59.6.0 |
| `catkin-pkg-modules` | 1.1.0 |
| `launch` / `launch-testing` | 1.0.14 |
| `launch-ros` / `launch-testing-ros` | 0.19.13 |

### Python 라이브러리 (로보틱스 / 클라우드)

| 패키지 | 버전 | 용도 |
|--------|------|------|
| `numpy` | 1.21.5 | 수치 계산 |
| `scipy` | 1.8.0 | 신호/최적화 |
| `opencv-python` (`cv2`) / `libopencv-dev` | 4.5.4 | 비전 |
| `tf2-py` / `tf2-geometry-msgs` / `tf2-kdl` / `tf2-msgs` / `tf2-ros-py` / `tf2-sensor-msgs` / `tf2-tools` | 0.25.20 | 좌표 프레임 |
| `rcl-interfaces` | 1.2.2 | ROS msg/log |
| `rosbag2-py` / `rosbag2-interfaces` | 0.15.16 | rosbag 기록·재생 |
| `firebase-admin` | 7.4.0 | RTDB 업로드 (`coord_service`, `log_bridge`) |

### Doosan Robotics 워크스페이스 (`~/cobot_ws/src/doosan-robot2`)

apt 미러에는 ROS2 Doosan 패키지가 없으며, 모두 소스 빌드.

| 항목 | 값 |
|------|-----|
| repo HEAD | `ec92425` — `chore: release 20260324 (#53)` (2026-03-24) |
| `dsr_bringup2` | 1.1.0 |
| 포함 패키지 | `dsr_bringup2`, `dsr_common2`, `dsr_controller2`, `dsr_description2`, `dsr_example2`, `dsr_gazebo2`, `dsr_hardware2`, `dsr_moveit2`, `dsr_msgs2`, `dsr_mujoco`, `dsr_tests` |
| 로봇 모델 | **m0609** 고정 (CLAUDE.md 규약) |

### 워크스페이스 디렉토리 구성 (`~/cobot_ws/src`)

```
DoosanBootcamInt1   # 부트캠프 베이스
cobot1              # 행동루프 (mono action / launch sequence)
doosan-robot2       # DSR 스택 소스
dsr_rokey2          # Rokey 통합
interfaces          # 내부 msg/srv
realtime_scan       # coord_service, log_bridge (Firebase 업로드)
robo_chef           # 레시피 실행기
robo_chef_interfaces
```
