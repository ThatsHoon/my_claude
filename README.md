# My Claude Code Configuration

개인 Claude Code 환경 설정 — MCP 서버 및 Skills 목록 정리

- **OS**: Windows 11
- **Model**: claude-sonnet-4-6
- **Last updated**: 2026-04-16

---

## MCP Servers

| 이름 | 상태 | 설명 |
|------|------|------|
| `context7` (local) | ✓ Connected | 라이브러리·프레임워크 최신 공식 문서 조회 (`npx @upstash/context7-mcp`) |
| `claude.ai Context7` | ✓ Connected | Anthropic 호스팅 Context7 (Smithery) |
| `sequential-thinking` | ✓ Connected | 복잡한 문제를 단계별로 분해하는 추론 도구 (`npx @modelcontextprotocol/server-sequential-thinking`) |
| `playwright` | ✓ Connected | 브라우저 자동화 — 웹 크롤링, 스크린샷, UI 테스트 (`npx @playwright/mcp`) |
| `serena` | ✓ Connected | 시맨틱 코드 탐색 — 심볼 검색, 파일 구조 분석 (`uvx` + GitHub 소스) |
| `claude.ai Google Calendar` | ⚠ Needs Auth | Google Calendar 연동 |
| `claude.ai Gmail` | ⚠ Needs Auth | Gmail 연동 |
| `claude.ai Google Drive` | ⚠ Needs Auth | Google Drive 연동 |

### MCP 등록 명령어

```bash
# sequential-thinking
claude mcp add sequential-thinking -- npx -y @modelcontextprotocol/server-sequential-thinking

# playwright
claude mcp add playwright -- npx -y @playwright/mcp

# context7 (local)
claude mcp add context7 -- npx -y @upstash/context7-mcp

# serena (로컬 uvx 경로 사용)
claude mcp add serena -- \
  "C:/Users/ErifKim/AppData/Roaming/Python/Python314/Scripts/uvx.exe" \
  --from git+https://github.com/oraios/serena \
  serena start-mcp-server
```

---

## Skills (Plugins)

### 1. doosan-robotics (커스텀)

두산 로보틱스 전용 DRL/DRFL API 레퍼런스 + 코드 생성 skill.

| 항목 | 내용 |
|------|------|
| **경로** | `~/.claude/plugins/doosan-robotics/skills/doosan-robotics/SKILL.md` |
| **커버** | DRL Python v2.12.1 전체 함수 + DRFL C++ API (CDRFLEx, GL013303) |
| **트리거** | movej, movel, DRL, DRFL, CDRFLEx, 두산 로봇 등 키워드 자동 활성화 |
| **명시 호출** | `/doosan-robotics [함수명\|code:<설명>\|workflow:<주제>\|debug]` |

**커버 범위:**
- 위치 타입: `posj`, `posx`, `posb`, `trans`, `fkin`, `ikin`
- 동기 모션: `movej`, `movel`, `movejx`, `movec`, `movesj`, `movesx`, `moveb`, `move_spiral`, `move_periodic`, `move_home`
- 비동기 모션: `amovej`, `amovel`, `amovec`, ... (a 접두사 전체)
- 서보/속도: `servoj`(Override/Queue 모드), `servol`, `speedj`, `speedl`
- 힘/컴플라이언스: `task_compliance_ctrl`, `set_desired_force`, `release_force`, `set_stiffnessx`
- I/O: Digital/Analog, Tool Flange, Modbus, EtherNet/IP, PROFINET, FOCAS
- 통신: Serial, TCP Client/Server
- 비전: SVM(두산내장), Pickit 3D, Cognex/SICK/VISOR
- Application: 용접(Digital/Analog), 위빙 5종, Conveyor Tracking
- 수학: 삼각함수, 선형대수, 회전 변환
- Threading, TP UI, 시스템 유틸리티
- DRFL C++ RT 제어 (1kHz UDP, `servoj_rt`, `servoL_rt`)

---

### 2. awesome-skills (ComposioHQ)

출처: [github.com/ComposioHQ/awesome-claude-skills](https://github.com/ComposioHQ/awesome-claude-skills)

| Skill | 설명 | 호출 |
|-------|------|------|
| `mcp-builder` | MCP 서버 설계·구현 가이드 (Node.js/Python) | `/mcp-builder` |
| `webapp-testing` | 웹앱 E2E 테스트 자동화 | `/webapp-testing` |
| `skill-creator` | 새 Claude Code skill 생성 | `/skill-creator` |
| `artifacts-builder` | 아티팩트(번들) 생성 | `/artifacts-builder` |
| `changelog-generator` | 변경 로그 자동 생성 | `/changelog-generator` |
| `langsmith-fetch` | LangSmith 트레이스 조회 | `/langsmith-fetch` |
| `developer-growth-analysis` | 개발자 성장 분석 | `/developer-growth-analysis` |

---

### 3. claude-plugins-official (마켓플레이스)

| Plugin | Skills |
|--------|--------|
| `claude-code-setup` | `claude-automation-recommender` |
| `claude-md-management` | `claude-md-improver` |
| `frontend-design` | `frontend-design` |
| `hookify` | `writing-rules` |
| `math-olympiad` | `math-olympiad` |
| `mcp-server-dev` | `build-mcp-app`, `build-mcp-server`, `build-mcpb` |
| `playground` | `playground` |
| `plugin-dev` | `agent-development`, `command-development`, `hook-development`, `mcp-integration`, `plugin-settings` |
| `discord` (external) | `access`, `configure` |
| `imessage` (external) | `access`, `configure` |
| `telegram` (external) | `access`, `configure` |

---

## Skills 작동 방식

```
자동 활성화: description 키워드 매칭 시 자동 로드
명시 호출:  /skill-name [arguments]  →  $ARGUMENTS 변수에 전달
```

skills는 `~/.claude/plugins/<plugin-name>/skills/<skill-name>/SKILL.md` 에 저장됩니다.
