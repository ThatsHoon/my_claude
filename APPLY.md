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

## 5. 제외 (미러링 대상 아님)

다음은 **로컬 스킬**이라 이 절차로 설치하지 않는다. 사용자가 별도로 안내한다.

- `ros2-architect`
- `doosan-robotics`

## 6. 보고

완료 후 사용자에게 다음을 보고:

- 배치한 CLAUDE.md 파일 경로
- 등록한 마켓플레이스
- 설치한 플러그인 목록 (성공/실패 분리)
- 건너뛴 항목과 이유
