# APPLY — 새 PC 에 설정 적용 절차 (AI 용)

이 문서는 새 PC 에서 Claude Code 를 띄운 AI 가 따르는 체크리스트다.
**순서대로** 실행하고, 각 단계 끝에 사용자에게 결과를 보고한다.

## 1. CLAUDE.md 배치

다음 두 파일을 절대 경로에 그대로 쓴다 (이미 존재하면 사용자에게 덮어쓸지 확인).

| 소스 (이 레포) | 대상 경로 |
| --- | --- |
| `claude_md/global.md` | `~/CLAUDE.md` |
| `claude_md/cobot_ws.md` | `~/cobot_ws/CLAUDE.md` |

`~/cobot_ws/` 가 없는 PC 라면 두 번째 파일은 건너뛰고 사용자에게 알린다.

## 2. 플러그인 마켓플레이스 등록

`plugins/known_marketplaces.json` 에 정의된 마켓을 등록한다.

```
github:anthropics/claude-plugins-official
github:anthropics/skills            # anthropic-agent-skills (document-skills 번들 출처)
github:forrestchang/andrej-karpathy-skills
github:bradautomates/claude-video
github:Lum1104/Understand-Anything
```

Claude Code CLI 안에서:

```
/plugin marketplace add anthropics/claude-plugins-official
/plugin marketplace add anthropics/skills
/plugin marketplace add forrestchang/andrej-karpathy-skills
/plugin marketplace add bradautomates/claude-video
/plugin marketplace add Lum1104/Understand-Anything
```

## 3. 플러그인 설치

`plugins/installed_plugins.json` 의 `marketplaces.<이름>` 배열에 나열된 모든
플러그인을 사용자(user) 스코프로 설치한다.

설치 명령 (Claude Code CLI 안에서):

```
/plugin install <이름>@<마켓이름>
```

### 3-1. `claude-plugins-official` 에서 설치 (20 개)

- `frontend-design`
- `context7`
- `skill-creator`
- `playwright`
- `code-simplifier`
- `github`
- `claude-md-management`
- `superpowers`
- `feature-dev`
- `security-guidance`
- `chrome-devtools-mcp`
- `huggingface-skills`
- `playground`
- `code-review`
- `supabase`
- `claude-code-setup`
- `typescript-lsp`
- `ralph-loop`
- `commit-commands`
- `pr-review-toolkit`

### 3-2. `anthropic-agent-skills` 에서 설치 (1 개)

- `document-skills`

### 3-3. `karpathy-skills` 에서 설치 (1 개)

- `andrej-karpathy-skills`

### 3-4. `claude-video` 에서 설치 (1 개)

- `watch`

### 3-5. `understand-anything` 에서 설치 (1 개)

- `understand-anything`

## 4. 활성화 상태 동기화

`plugins/enabled_plugins.json` 의 키/값을 그대로 `~/.claude/settings.json` 의
`enabledPlugins` 섹션에 반영. 24개 모두 `true`.

`theme` 등 다른 설정은 사용자의 PC 환경을 우선한다.

## 5. 사용자 스킬 배치

### 5-1. 필수 스킬 (항상 설치)

`skills/` 루트 아래의 각 스킬 폴더를 `~/.claude/skills/` 로 그대로 복사한다.
(`skills/legacy/` 는 제외.) 이미 같은 이름이 있으면 사용자에게 덮어쓸지 확인.

| 소스 (이 레포) | 대상 경로 | 비고 |
| --- | --- | --- |
| `skills/html-ppt/` | `~/.claude/skills/html-ppt/` | PPT 데크 (36 테마, 31 레이아웃, presenter mode) |
| `skills/ros2-architect/` | `~/.claude/skills/ros2-architect/` | ROS 2 아키텍처 |
| `skills/mcp-builder/` | `~/.claude/skills/mcp-builder/` | MCP 서버 빌드 가이드 |
| `skills/build-mcpb/` | `~/.claude/skills/build-mcpb/` | MCP 서버 패키징 |

`~/.claude/skills/` 가 없으면 먼저 생성한다.

### 5-2. 레거시 스킬 (설치하지 않음)

`skills/legacy/` 아래의 스킬은 과거에 사용했으나 현재는 **비활성**이다.
새 PC 에는 설치하지 않는다. 포함된 스킬:
`architecture-diagram`, `configdb-reverse`, `doosan-robotics`, `gp-quadruped`,
`isaac-sim-bridge`, `isaac-sim-mcp`, `rive-web`

## 6. Node.js 확인 (npx 기반 MCP 활성화)

`chrome-devtools`, `playwright`, `context7`, `drawio` 등 MCP 는 `npx` 로 spawn 되므로 Node.js 필요.

```bash
node --version   # v20+ 권장
```

## 7. 보고

완료 후 사용자에게 다음을 보고:

- 배치한 CLAUDE.md 파일 경로
- 등록한 마켓플레이스 (5 개)
- 설치한 플러그인 목록 (26 개 — 성공/실패 분리)
- 배치한 필수 스킬 목록 (4 개)
- Node.js 버전 (`node --version`)
- 건너뛴 항목과 이유
