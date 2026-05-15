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
| `skills/<이름>/` | `~/.claude/skills/<이름>/` 에 그대로 복사할 사용자 스킬 |

## 포함된 사용자 스킬

마켓플레이스 플러그인에 없는, 로컬에서 직접 만든 스킬을 같이 미러링한다.
새 PC 에서는 `skills/<이름>/` 폴더를 `~/.claude/skills/<이름>/` 로 복사하면 된다.

- `web-slide` — 16:9 PPT 스타일 단일 HTML 슬라이드 생성
- `isaac-sim-bridge` — NVIDIA Isaac Sim / Isaac Lab / Isaac ROS 도메인 지식 (USD/PhysX/OG)
- `isaac-sim-mcp` — `isaac-sim-mcp` 서버를 통한 라이브 Isaac Sim 제어 playbook (도구 선택·검증·디버깅 패턴). `isaac-sim-bridge` 와 보완관계
- `ros2-architect` — ROS 2 아키텍처/엔지니어링 전반
- `doosan-robotics` — Doosan m0609 (DRL/DRFL/doosan-robot2) 작업용
