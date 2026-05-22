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

`plugins/known_marketplaces.json` 에 정의된 마켓을 등록한다. 현재는 다음 하나뿐이다:

```
github:anthropics/claude-plugins-official
```

Claude Code CLI 안에서:

```
/plugin marketplace add anthropics/claude-plugins-official
```

## 3. 플러그인 설치

`plugins/installed_plugins.json` 에 나열된 모든 플러그인을 사용자(user) 스코프로
설치한다. 각 플러그인은 `<이름>@claude-plugins-official` 형식이다.

설치 명령 (Claude Code CLI 안에서, 각 플러그인마다 1회):

```
/plugin install <이름>@claude-plugins-official
```

설치할 플러그인 목록 (현재 17 개):

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

## 4. 활성화 상태 동기화

`plugins/enabled_plugins.json` 의 키들이 모두 `true` 인지 확인.
필요하면 `~/.claude/settings.json` 의 `enabledPlugins` 섹션을 이 파일과 일치시킨다.
`theme` 등 다른 설정은 사용자의 PC 환경을 우선한다.

## 5. 사용자 스킬 배치

`skills/` 아래의 각 스킬 폴더를 `~/.claude/skills/` 로 그대로 복사한다.
이미 같은 이름이 있으면 사용자에게 덮어쓸지 확인.

| 소스 (이 레포) | 대상 경로 | 비고 |
| --- | --- | --- |
| `skills/web-slide/` | `~/.claude/skills/web-slide/` | |
| `skills/isaac-sim-bridge/` | `~/.claude/skills/isaac-sim-bridge/` | |
| `skills/isaac-sim-mcp/` | `~/.claude/skills/isaac-sim-mcp/` | |
| `skills/ros2-architect/` | `~/.claude/skills/ros2-architect/` | m0609 없어도 배치 |
| `skills/doosan-robotics/` | `~/.claude/skills/doosan-robotics/` | m0609 없어도 배치 |
| `skills/mcp-builder/` | `~/.claude/skills/mcp-builder/` | MCP 서버 빌드 가이드 |
| `skills/build-mcpb/` | `~/.claude/skills/build-mcpb/` | MCP 서버 개발 도구 |
| `skills/gp-quadruped/` | `~/.claude/skills/gp-quadruped/` | GP 4족 보행 컨텍스트 |

`~/.claude/skills/` 가 없으면 먼저 생성한다.

`isaac-sim-mcp` 스킬은 `whats2000/isaacsim-mcp-server` (별도 설치, §7 참고) 사용법을 다룬다.
MCP 서버 미설치 PC 에서도 배치 자체는 진행 — 향후 설치 시 자동 활성화됨.

## 6. Node.js 설치 (npx 기반 MCP 활성화 — 모든 PC)

`chrome-devtools` 와 `playwright` MCP 는 `npx` 로 spawn 되므로 Node.js 필요. 미설치
시 두 MCP 가 "Failed to connect" 로 잠자고, `web-slide` 의 라이브 검증 워크플로우가
동작 안 함.

```bash
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs
node --version    # v20.x 확인
```

설치 후 Claude Code 세션 재시작 → `claude mcp list` 에서 `playwright` 와
`chrome-devtools-mcp` 가 ✓ Connected 로 바뀜.

## 7. (선택) isaac-sim-mcp MCP 서버 설치

Isaac Sim 라이브 제어를 Claude 가 직접 하려면 MCP 서버가 필요하다. Isaac Sim 사용
계획이 있는 PC 에서만 실행 (없으면 건너뜀).

### 6-1. `uv` (Astral 패키지 매니저) 설치
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.local/bin:$PATH"
```

### 6-2. isaacsim-mcp-server 레포 클론
```bash
git clone https://github.com/whats2000/isaacsim-mcp-server.git ~/dev_ws/isaacsim-mcp-server
```

### 6-3. 의존성 설치
```bash
cd ~/dev_ws/isaacsim-mcp-server
uv sync
```

### 6-4. Claude Code 에 MCP 서버 등록
```bash
claude mcp add isaac-sim --scope user -- \
  uv run --directory ~/dev_ws/isaacsim-mcp-server isaacsim-mcp-server
```
확인:
```bash
claude mcp list | grep isaac-sim
```

### 6-5. Isaac Sim 빌드의 python.sh 패치 (packman USD 경로 추가)
소스 빌드 케이스에서 `pxr` 모듈이 PYTHONPATH 누락. `python.sh` 의 `source setup_python_env.sh` 다음 줄에 추가:
```bash
_PACKMAN_USD=$(ls -d ${HOME}/.cache/packman/chk/usd.py311*/*/lib/python 2>/dev/null | head -1)
if [ -n "$_PACKMAN_USD" ]; then
    export PYTHONPATH=$PYTHONPATH:$_PACKMAN_USD
fi
```

### 6-6. `~/.bashrc` 에 alias 추가
```bash
alias isaac-mcp='~/dev_ws/isaac_sim/isaacsim/_build/linux-x86_64/release/isaac-sim.sh \
  --ext-folder ~/dev_ws/isaacsim-mcp-server/ \
  --enable isaac.sim.mcp_extension'
```

이후 새 터미널에서 `isaac-mcp` 로 Isaac Sim 띄우면 extension 자동 로드 (localhost:8766).

### 6-7. 진단
`isaac-sim-mcp` 스킬에 헬스체크 스크립트 포함:
```bash
python3 ~/.claude/skills/isaac-sim-mcp/scripts/check_mcp_health.py
```

## 8. 보고

완료 후 사용자에게 다음을 보고:

- 배치한 CLAUDE.md 파일 경로
- 등록한 마켓플레이스
- 설치한 플러그인 목록 (성공/실패 분리)
- 배치한 사용자 스킬 목록
- (시도했다면) MCP 서버 설치 결과 — `claude mcp list` 출력 포함
- 건너뛴 항목과 이유
