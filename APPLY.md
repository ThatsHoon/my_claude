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

### 3-1. `claude-plugins-official` 에서 설치 (22 개)

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
- `serena`
- `slack`
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

## 4. 활성화 상태 동기화 (중요 — context7/serena 비활성)

`plugins/enabled_plugins.json` 의 키/값을 그대로 `~/.claude/settings.json` 의
`enabledPlugins` 섹션에 반영. **특히 `context7@claude-plugins-official`,
`serena@claude-plugins-official` 두 개는 `false`** — AIRIS Gateway 가 내부에
포함하므로 의도적으로 중복 제거. 나머지 25개는 모두 `true`.

`theme` 등 다른 설정은 사용자의 PC 환경을 우선한다.

## 5. 사용자 스킬 배치

### 5-1. 필수 스킬 (항상 설치)

`skills/` 아래의 각 스킬 폴더를 `~/.claude/skills/` 로 그대로 복사한다.
이미 같은 이름이 있으면 사용자에게 덮어쓸지 확인.

| 소스 (이 레포) | 대상 경로 | 비고 |
| --- | --- | --- |
| `skills/html-ppt/` | `~/.claude/skills/html-ppt/` | PPT 데크 (36 테마, 31 레이아웃, presenter mode) |
| `skills/architecture-diagram/` | `~/.claude/skills/architecture-diagram/` | 다크 SVG 인프라 다이어그램 |
| `skills/ros2-architect/` | `~/.claude/skills/ros2-architect/` | m0609 없어도 배치 |
| `skills/doosan-robotics/` | `~/.claude/skills/doosan-robotics/` | m0609 없어도 배치 |
| `skills/mcp-builder/` | `~/.claude/skills/mcp-builder/` | MCP 서버 빌드 가이드 |
| `skills/build-mcpb/` | `~/.claude/skills/build-mcpb/` | MCP 서버 패키징 |
| `skills/rive-web/` | `~/.claude/skills/rive-web/` | Rive 웹 통합 |

`~/.claude/skills/` 가 없으면 먼저 생성한다.

### 5-2. 선택 스킬 (사용자에게 반드시 확인 후 설치)

`skills/optional/` 아래의 스킬은 **특정 환경에서만 필요**하므로,
설치 전에 사용자에게 **각 스킬을 개별적으로** 설치할지 물어봐야 한다.
사용자가 "예" 라고 답한 스킬만 `~/.claude/skills/` 로 복사한다.

| 스킬 | 소스 (이 레포) | 대상 경로 | 언제 필요한가 |
| --- | --- | --- | --- |
| `isaac-sim-bridge` | `skills/optional/isaac-sim-bridge/` | `~/.claude/skills/isaac-sim-bridge/` | NVIDIA Isaac Sim / Isaac Lab / Isaac ROS 작업 PC |
| `isaac-sim-mcp` | `skills/optional/isaac-sim-mcp/` | `~/.claude/skills/isaac-sim-mcp/` | Isaac Sim MCP 서버로 라이브 제어하는 PC |
| `gp-quadruped` | `skills/optional/gp-quadruped/` | `~/.claude/skills/gp-quadruped/` | Boston Dynamics Spot (cobot3 GP) 경계초소 작업 PC |

**확인 방법**: 각 스킬에 대해 사용자에게 다음과 같이 질문한다.

> `<스킬명>` 스킬을 설치할까요? (`<언제 필요한가>` 환경에서만 필요합니다.)

## 6. AIRIS MCP Gateway 설치 (필수 — MCP 단일 허브)

이 PC 는 [AIRIS MCP Gateway](https://github.com/agiletec-inc/airis-mcp-gateway)
를 단일 허브로 사용. context7, serena, chrome-devtools, supabase, github, stripe,
twilio, cloudflare, figma, magic, postgres, memory, mindbase, morphllm,
sequential-thinking, filesystem, git, time, fetch, tavily 등 20+ MCP 서버를
게이트웨이 뒤에 집약.

### 6-1. 사전 요구

- Docker 28+ + Docker Compose v2
- `curl`
- 포트 9400 사용 가능

확인:
```bash
docker --version && docker compose version && curl --version | head -1
ss -tlnp | grep :9400 || echo "9400 free"
```

### 6-2. 설치 (Docker 이미지 + CLI + Claude Code 자동 등록)

```bash
curl -fsSL https://raw.githubusercontent.com/agiletec-inc/airis-mcp-gateway/main/install.sh \
  | AIRIS_VERSION=main bash
```

> `AIRIS_VERSION=main` 필수. 기본값 `latest` 는 git 태그로 존재하지 않아 다운로드 실패.

설치 후 다음이 만들어진다:
- 컨테이너 3 개: `airis-mcp-gateway` (port 9400), `airis-serena`, `airis-docker-mcp-gateway`
- 파일: `~/.local/share/airis-mcp-gateway/` (compose.yaml, mcp-config.json)
- CLI: `~/.local/bin/airis-gateway`
- 레지스트리: `~/.airis/mcp/registry.json`
- `~/.claude.json` 에 `airis-mcp-gateway: http://localhost:9400/sse` 자동 등록

### 6-3. 검증

```bash
curl -s http://localhost:9400/health        # {"status":"healthy"}
docker ps --filter "name=airis"             # 3개 healthy
claude mcp list | grep airis                # ✓ Connected
```

### 6-4. 운영 명령

```bash
airis-gateway up | down | logs -f | status | servers | doctor
airis-gateway --uninstall
```

## 7. Node.js 설치 (npx 기반 MCP 활성화)

`chrome-devtools` 와 `playwright` MCP 는 `npx` 로 spawn 되므로 Node.js 필요.

```bash
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs
node --version
```

설치 후 Claude Code 세션 재시작 → `claude mcp list` 에서 `playwright` 와
`chrome-devtools-mcp` 가 ✓ Connected.

## 8. (선택) isaac-sim-mcp MCP 서버 설치

Isaac Sim 라이브 제어를 Claude 가 직접 하려면 필요. Isaac Sim 사용 PC 만.
§5-2 에서 `isaac-sim-mcp` 스킬 설치에 동의한 경우에만 진행한다.

### 8-1. `uv` 설치
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.local/bin:$PATH"
```

### 8-2. 레포 클론 + 의존성
```bash
git clone https://github.com/whats2000/isaacsim-mcp-server.git ~/dev_ws/isaacsim-mcp-server
cd ~/dev_ws/isaacsim-mcp-server && uv sync
```

### 8-3. Claude Code MCP 등록
```bash
claude mcp add isaac-sim --scope user -- \
  uv run --directory ~/dev_ws/isaacsim-mcp-server isaacsim-mcp-server
claude mcp list | grep isaac-sim
```

### 8-4. Isaac Sim python.sh 패치 (소스 빌드 케이스)
`python.sh` 의 `source setup_python_env.sh` 다음 줄에 추가:
```bash
_PACKMAN_USD=$(ls -d ${HOME}/.cache/packman/chk/usd.py311*/*/lib/python 2>/dev/null | head -1)
if [ -n "$_PACKMAN_USD" ]; then
    export PYTHONPATH=$PYTHONPATH:$_PACKMAN_USD
fi
```

### 8-5. `~/.bashrc` alias
```bash
alias isaac-mcp='~/dev_ws/isaac_sim/isaacsim/_build/linux-x86_64/release/isaac-sim.sh \
  --ext-folder ~/dev_ws/isaacsim-mcp-server/ \
  --enable isaac.sim.mcp_extension'
```

### 8-6. 헬스체크
```bash
python3 ~/.claude/skills/isaac-sim-mcp/scripts/check_mcp_health.py
```

## 9. 보고

완료 후 사용자에게 다음을 보고:

- 배치한 CLAUDE.md 파일 경로
- 등록한 마켓플레이스 (2 개)
- 설치한 플러그인 목록 (성공/실패 분리)
- 비활성화한 플러그인 (context7, serena — AIRIS 중복 방지)
- 배치한 필수 스킬 목록 (7 개)
- 배치한 선택 스킬 목록 (설치한 것 / 건너뛴 것 분리)
- 설치한 플러그인 목록 (총 26 개 — 성공/실패 분리)
- 비활성화한 플러그인 (context7, serena — AIRIS 중복 방지)
- AIRIS Gateway 설치 결과 (`claude mcp list | grep airis` 출력)
- (시도했다면) isaac-sim-mcp 서버 설치 결과
- Node.js 버전 (`node --version`)
- 건너뛴 항목과 이유
