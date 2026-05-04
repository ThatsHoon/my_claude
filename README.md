# my_claude — Claude Code 설정 미러

다른 PC 에서 Claude Code 를 설치할 때, AI 가 이 레포의 내용을 그대로 읽어
**현재 PC 의 Claude Code 설정을 복제**하도록 만든 저장소다.

> 사용 방법: 새 PC 에서 Claude Code 를 띄우고 다음과 같이 지시하면 된다.
>
> > "https://github.com/ThatsHoon/my_claude 의 내용을 그대로 적용해줘."

AI 는 [APPLY.md](APPLY.md) 의 절차를 따라 CLAUDE.md 와 플러그인을 동일하게 세팅한다.

## 레포 구성

| 경로 | 내용 |
| --- | --- |
| `APPLY.md` | 새 PC 에서 적용할 때 AI 가 따라야 할 절차 |
| `claude_md/global.md` | `~/CLAUDE.md` (사용자 전역 규칙) 의 내용 |
| `claude_md/cobot_ws.md` | `~/cobot_ws/CLAUDE.md` (Doosan m0609 워크스페이스 규칙) 의 내용 |
| `plugins/enabled_plugins.json` | `~/.claude/settings.json` 의 `enabledPlugins` 섹션 |
| `plugins/installed_plugins.json` | `~/.claude/plugins/installed_plugins.json` 의 마켓플레이스 플러그인 목록 |
| `plugins/known_marketplaces.json` | `~/.claude/plugins/known_marketplaces.json` (플러그인 마켓 출처) |

## 제외 항목

다음은 **로컬 전용 스킬**이라 의도적으로 미러링하지 않는다 (해당 PC 의 두산 작업
컨텍스트에서만 의미가 있고, 이미 마켓플레이스 플러그인 목록에도 포함되지 않는다):

- `ros2-architect`
- `doosan-robotics`
