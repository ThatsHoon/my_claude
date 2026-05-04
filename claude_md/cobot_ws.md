# cobot_ws — Doosan m0609 프로젝트 규칙

이 파일은 `~/cobot_ws/` 안에서 작업할 때만 로드된다.

## 프로젝트 컨텍스트

- 메인 노드: 로봇 팔과 직접 연결된 PC. 현재 PC 는 **서브 노드**.
- 로봇: **Doosan m0609** (협동로봇).
- 워크스페이스: `~/cobot_ws/`. 빌드 후 `source install/setup.bash` 필수.
- 코드 작성 시 `ROBOT_MODEL = "m0609"` 로 고정. `m1013` 등 다른 모델명 사용 금지.

## 자동 활성화되는 스킬

두산 작업 관련 키워드/맥락이 보이면 다음이 자동 트리거된다:

- **`doosan-robotics`** — DRL/DRFL/DSR_ROBOT2, 코드베이스 분석, 161개 인터페이스, 두산 함정 모음.
- **`ros2-architect`** — vendor-neutral ROS 2 패턴 (QoS, lifecycle, executor, rqt, RViz plugin 등).

서비스/토픽 정확한 사양은 `/home/hoon/Documents/services/<카테고리>/` 와 `/home/hoon/Documents/topics/`
가 1차 자료. 스킬의 `references/dev-docs-index.md` 가 사용법을 정리한다.

## 자동 개선 규칙

- 새 함정/오류는 doosan-robotics 스킬의 `references/*.md` 에 추가.
- 서비스/토픽 동작이 dev-docs 와 다르면 `/home/hoon/Documents/services|topics/<name>.md` 의 §5
  비고 갱신.
- 두산 코드 수정 후 `simplify` 스킬 적용해 품질 점검.
