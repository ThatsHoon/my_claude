---
name: doosan-robotics
description: >
  Use this skill when the user asks about Doosan Robotics robot programming,
  DRL Python API, DRFL C++ API, DRFLEx functions, movej, movel, movec, moveb,
  movesx, movesj, move_spiral, move_periodic, servoj, servol, speedj, speedl,
  task_compliance_ctrl, set_desired_force, force control, compliance control,
  real-time RT control, digital I/O, analog I/O, modbus, serial communication,
  TCP/IP socket, vision integration, welding app, conveyor tracking, posj, posx,
  trans, fkin, ikin, threading, or any Doosan robot motion/control topic.
  Also activate when the user wants to generate Doosan robot code, debug DRFL/DRL
  programs, or uses keywords like "두산 로봇", "두산 로보틱스", "DRFL", "DRL",
  "CDRFLEx", "두산 협동로봇", "도산로봇".
argument-hint: [함수명 | 기능 키워드 | code:<작업설명> | workflow:<주제> | debug]
allowed-tools: [Read, Write, Edit, Glob, Grep, Bash]
---

# Doosan Robotics API Skill

**두 가지 API 인터페이스를 모두 지원합니다:**

| 인터페이스 | 언어 | 실행 위치 | 버전 |
|-----------|------|----------|------|
| **DRL** (Doosan Robot Language) | Python | 로봇 컨트롤러 내부 | v2.12.1 |
| **DRFL** C++ API | C++ | 외부 PC (CDRFLEx) | GL013303 v1.33.3 |

**인자:** `$ARGUMENTS`

---

## 인자 처리 방법

`$ARGUMENTS`를 파싱하여:
- **함수명** (예: `movej`, `movel`) → 해당 함수 전체 시그니처·파라미터·예제
- **`code:<설명>`** → 설명에 맞는 완전한 코드 생성 (연결~종료까지)
- **`workflow:<주제>`** → 주제별 단계별 절차 안내
- **`debug`** → 사용자 코드 분석 후 문제점 및 수정 방법 제시
- **인자 없음** → 전체 목차 및 주요 함수 목록 출력

---

# PART 1 — DRL (Python API, 컨트롤러 내부 실행)

DRL은 로봇 컨트롤러에서 직접 실행되는 Python 기반 스크립트 언어입니다.
Python 문법(들여쓰기, `#` 주석, if/while/for, list/dict 등)을 그대로 사용합니다.

---

## 1-1. 위치 타입 (Position Types)

```python
# 관절 공간 위치 — 6축 각도 [deg]
q = posj(J1=0, J2=0, J3=90, J4=0, J5=90, J6=0)
q = posj(0, 0, 90, 0, 90, 0)   # 위치 인자 순서대로도 가능

# 직교 공간 위치 — [X, Y, Z mm, A, B, C deg] (오일러각 ZYZ)
p = posx(X=559, Y=434, Z=651, A=0, B=180, C=0)
p = posx(559, 434, 651, 0, 180, 0)

# 블렌딩 세그먼트 (moveb 전용)
# seg_type: DR_LINE(선형) 또는 DR_CIRCLE(원호)
seg = posb(DR_LINE,   p1, radius=50)            # 선형 세그먼트
seg = posb(DR_CIRCLE, via, p2, radius=50)       # 원호 세그먼트
```

---

## 1-2. 전역 속도·가속도 설정

```python
# 관절 공간 기본값 설정
set_velj(vel)                           # 관절 속도 [deg/s]
set_accj(acc)                           # 관절 가속도 [deg/s²]

# 직교 공간 기본값 설정
set_velx(vel1, vel2=0, clamp=DR_CLAMPING_ON)
# vel1: 선속도 [mm/s], vel2: 각속도 [deg/s] (0이면 자동스케일)
set_accx(acc1, acc2=0)
# acc1: 선가속도 [mm/s²], acc2: 각가속도 [deg/s²]

# 예제
set_velj(30)     # 기본 관절속도 30 deg/s
set_accj(60)     # 기본 관절가속도 60 deg/s²
set_velx(100, 50)
set_accx(200, 100)
```

---

## 1-3. 동기 모션 함수 (Synchronous Motion)

> 동기(sync): 동작 완료 후 다음 줄 실행. 비동기는 `a` 접두사 (amovej, amovel, ...)

### movej — 관절 공간 PTP
```python
movej(pos, vel=None, acc=None, time=None, radius=0,
      mod=DR_MV_MOD_ABS, ref=None, ra=DR_MV_RA_DUPLICATE,
      v=None, a=None, t=None)
# pos    : posj 타입. 목표 관절각
# vel    : 관절 속도 [deg/s]. None이면 set_velj 값 사용
# acc    : 관절 가속도 [deg/s²]. None이면 set_accj 값 사용
# time   : 도달 시간 [sec]. 지정 시 vel/acc 무시
# radius : 블렌딩 반경 [mm] (0 = 완전 정지 후 이동)
# mod    : DR_MV_MOD_ABS(절대) | DR_MV_MOD_REL(상대)
# ra     : DR_MV_RA_DUPLICATE | DR_MV_RA_OVERRIDE (블렌딩 속도 타입)
# 반환   : None (블로킹)

# 예제
movej(posj(0, 0, 90, 0, 90, 0))                      # 기본값으로 이동
movej(posj(0, 0, 90, 0, 90, 0), vel=30, acc=60)
movej(posj(0, 0, 90, 0, 90, 0), time=3.0)            # 3초에 도달
movej(posj(30, 0, 90, 0, 90, 0), vel=30, acc=60, radius=50) # 50mm 블렌딩
```

### movel — 직선 경로 (직교 공간)
```python
movel(pos, vel=None, acc=None, time=None, radius=0,
      ref=DR_BASE, mod=DR_MV_MOD_ABS, ra=DR_MV_RA_DUPLICATE,
      v=None, a=None, t=None)
# pos  : posx 타입. 목표 TCP 위치 [mm, deg]
# vel  : [선속도 mm/s, 각속도 deg/s] 또는 단일 float (선속도만)
# acc  : [선가속도, 각가속도] 또는 단일 float
# ref  : DR_BASE | DR_TOOL | DR_WORLD | 사용자 좌표계

# 예제
p1 = posx(559, 434, 651, 0, 180, 0)
movel(p1)                                              # 기본값 사용
movel(p1, vel=100, acc=200)                           # 선속도 100mm/s
movel(p1, vel=[100, 50], acc=[200, 100])              # 선/각속도 개별 지정
movel(p1, time=2.0)                                   # 2초에 도달
# 툴 기준 +Z 방향으로 50mm 이동
movel(posx(0,0,50,0,0,0), vel=50, acc=100,
      ref=DR_TOOL, mod=DR_MV_MOD_REL)
```

### movec — 원호 경로
```python
movec(pos1, pos2, vel=None, acc=None, time=None, radius=None,
      ref=None, mod=DR_MV_MOD_ABS, angle=None,
      ra=DR_MV_RA_DUPLICATE, ori=DR_MV_ORI_TEACH, app_type=DR_MV_APP_NONE)
# pos1    : 경유점 posx (중간 웨이포인트)
# pos2    : 목표점 posx (끝점)
# angle   : float — 원호 총 각도 [deg] (0이면 pos1~pos2 호 자동)
#           list[2] — [angle1, angle2]: 정속 각도, 가감속 구간 각도
#           총 이동각 = angle1 + 2×angle2
# ori     : DR_MV_ORI_TEACH(기본) | DR_MV_ORI_FIXED | DR_MV_ORI_RADIAL | DR_MV_ORI_INTENT
# mod     : DR_MV_MOD_REL 시 pos1=시작점 대비, pos2=pos1 대비 상대좌표

# 예제
via = posx(559, 434, 451, 0, 180, 0)
tgt = posx(559, 434, 251, 0, 180, 0)
movec(via, tgt, vel=100, acc=200)

# 360도 원 (원호 각도 명시)
movec(via, tgt, vel=100, acc=200, angle1=360)
```

### moveb — 혼합 경로 블렌딩
```python
moveb(pos_list, vel=None, acc=None, time=None,
      ref=DR_BASE, mod=DR_MV_MOD_ABS, app_type=DR_MV_APP_NONE)
# pos_list : posb 세그먼트 리스트 (최대 50개)
# 각 세그먼트: posb(seg_type, posx1, posx2=None, radius=반경)
# 마지막 세그먼트의 radius는 무시됨 (0으로 처리)
# 블렌딩 구간에서 등속도 유지

# 예제
p1 = posx(500, 200, 600, 0, 180, 0)
p2 = posx(600, 300, 600, 0, 180, 0)
via = posx(650, 250, 550, 0, 180, 0)
p3 = posx(700, 200, 600, 0, 180, 0)

segs = [
    posb(DR_LINE,   p1,  radius=50),         # 선형 → p1, 50mm 블렌딩
    posb(DR_CIRCLE, via, p2, radius=50),     # 원호 via→p2
    posb(DR_LINE,   p3,  radius=0),          # 선형 → p3 (마지막은 0)
]
moveb(segs, vel=100, acc=200)
```

### movejx — 직교 좌표 목표를 관절 공간으로
```python
movejx(pos, sol=0, vel=None, acc=None, time=None, radius=0,
       ref=DR_BASE, mod=DR_MV_MOD_ABS, ra=DR_MV_RA_DUPLICATE)
# pos  : posx 타입. 목표 TCP 직교 좌표
# sol  : 솔루션 스페이스 0~7 (비트: bit2=Shoulder, bit1=Elbow, bit0=Wrist)
#        255 = 자동 (현재 자세 기준 최소 이동)
# 반환 : None

# 예제
p = posx(559, 434, 651, 0, 180, 0)
movejx(p, sol=2, vel=30, acc=60)    # Lefty+Above+NoFlip
movejx(p, sol=255, vel=30, acc=60)  # 자동 형상 선택
```

### movesj — 관절 공간 스플라인
```python
movesj(pos_list, vel=None, acc=None, time=None, mod=DR_MV_MOD_ABS)
# pos_list: posj 위치 리스트 (최대 100개 웨이포인트)
# vel/acc : 최대값 (컨트롤러가 세그먼트별 자동 분배)

# 예제
waypoints = [
    posj(0, 0, 90, 0, 90, 0),
    posj(30, 0, 90, 0, 90, 0),
    posj(30, 30, 90, 0, 90, 0),
    posj(0, 0, 90, 0, 90, 0),
]
movesj(waypoints, vel=30, acc=60)
```

### movesx — 직교 공간 스플라인
```python
movesx(pos_list, vel=None, acc=None, time=None,
       ref=None, mod=DR_MV_MOD_ABS, vel_opt=DR_MVS_VEL_NONE)
# pos_list : posx 위치 리스트
# vel_opt  : DR_MVS_VEL_NONE(변속, 기본) | DR_MVS_VEL_CONST(등속)
#            등속 조건 미충족 시 자동으로 변속모션으로 전환
# 블렌딩(온라인) 지원 안함

# 예제
traj = [posx(500,200,600,0,180,0), posx(550,250,580,0,180,0),
        posx(600,300,600,0,180,0)]
movesx(traj, vel=[100, 30], acc=[200, 60], vel_opt=DR_MVS_VEL_NONE)
# 등속 이동 (가감속구간 제외)
movesx(traj, vel=[100, 30], acc=[200, 60], vel_opt=DR_MVS_VEL_CONST)
```

### move_spiral — 나선형 경로
```python
move_spiral(rev=10, rmax=None, lmax=0, vel=None, acc=None, time=None,
            axis=DR_AXIS_Z, ref=DR_TOOL,
            pos=None, mod=DR_MV_MOD_ABS,
            rad_dir=DR_SPIRAL_OUTWARD, rot_dir=DR_ROT_FORWARD,
            radius=None, ra=DR_MV_RA_DUPLICATE)
# rev     : 총 회전수 (>0, 기본 10)
# rmax    : spiral 최대 반경 [mm] (>0)
# lmax    : axis 방향 이동 거리 [mm] (음수 = -axis 방향)
# vel/acc : 속도/가속도 (None이면 set_velx 첫 번째 값 사용)
# time    : 총 수행 시간 [sec] (지정 시 vel/acc 무시)
# axis    : DR_AXIS_X | DR_AXIS_Y | DR_AXIS_Z
# ref     : DR_TOOL(기본) | DR_BASE | DR_WORLD | 사용자좌표계
# pos     : 목표점 좌표 [X,Y,Z] 또는 posx (rmax 대신 사용 가능)
# rad_dir : DR_SPIRAL_OUTWARD(외향, 기본) | DR_SPIRAL_INWARD(내향)
# rot_dir : DR_ROT_FORWARD(정방향+, 기본) | DR_ROT_REVERSE(역방향-)

# 예제 — Z축 나선형 삽입 (5바퀴, 반경 20mm, 깊이 10mm)
movej(posj(0, 0, 90, 0, 90, 0), vel=100, acc=100)
move_spiral(rev=5, rmax=20.0, lmax=-10, v=40, a=40,
            axis=DR_AXIS_Z, ref=DR_TOOL,
            rad_dir=DR_SPIRAL_OUTWARD, rot_dir=DR_ROT_FORWARD, r=20)
move_spiral(rev=5, rmax=20.0, lmax=-10, v=40, a=40,
            axis=DR_AXIS_Z, ref=DR_TOOL,
            rad_dir=DR_SPIRAL_INWARD, rot_dir=DR_ROT_FORWARD)
```

### move_periodic — 주기적 진동 경로
```python
move_periodic(amp, period, atime=0.0, repeat=1, ref=DR_TOOL)
# amp    : list(float[6]) — [Ax, Ay, Az mm, ARx, ARy, ARz deg] 진폭
#          비활성 축은 0으로 입력
# period : float 또는 list(float[6]) — 1주기 소요 시간 [sec], 0이면 해당 축 미수행
# atime  : 가감속 시간 [sec] (기본 0, 입력값과 max_period*0.25 중 큰 값 적용)
# repeat : 가장 큰 period 축 기준 반복 횟수 (기본 1)
# ref    : DR_TOOL(기본) | DR_BASE | DR_WORLD | 사용자좌표계
# 최대속도 = 진폭 × 2π / 주기 (예: 10mm, 1sec → 62.83mm/s)

# 예제 1 — Tool 좌표계 X축 10mm/1초 + Ry 30deg/1초, 5회 반복
move_periodic(amp=[10, 0, 0, 0, 30, 0], period=1.0, atime=0.2, repeat=5, ref=DR_TOOL)

# 예제 2 — BASE X축(10mm/1초) + Z축(20mm/1.5초) 동시, 3회
move_periodic(amp=[10, 0, 20, 0, 0.5, 0],
              period=[1, 0, 1.5, 0, 0, 0],
              atime=0.5, repeat=3, ref=DR_BASE)
```

---

## 1-4. 서보/속도 제어

### servoj — 관절 임피던스 서보
```python
servoj(pos, vel=None, acc=None, time=None, mod=DR_SERVO_OVERRIDE)
# pos  : posj 타입 목표 관절각 (list float[6] 가능)
# vel  : 최대 속도 [deg/s] (None이면 set_velj 값 사용)
# acc  : 최대 가속도 [deg/s²] (None이면 set_accj 값 사용)
# time : 목표 도달 시간 [sec]
# mod  : DR_SERVO_OVERRIDE — 최신 목표값만 추종
#        DR_SERVO_QUEUE    — 큐에 최대 100개 저장, 순차 추종
# 비동기 함수 — 즉시 반환, 다음 servoj 호출로 연속 제어

# 예제 — 연속 관절 추종 제어
set_velj(30)
set_accj(60)

Xt = posj(0, 0, 0, 0, 0, 0)
servoj(Xt)
target = posj(90, 0, 120, -50, 50, -90)
del_t = [3, 0.1, 3, -3, 3, -3]

while True:
    for i in range(6):
        Xt[i] = Xt[i] + del_t[i]
        if del_t[i] > 0:
            if Xt[i] > target[i]: Xt[i] = target[i]
        else:
            if Xt[i] < target[i]: Xt[i] = target[i]
    servoj(Xt)
```

### servol — 직교 임피던스 서보
```python
servol(pos, vel=None, acc=None, time=None)
# pos  : posx 타입 목표 TCP 위치 (list float[6] 가능)
# vel  : 최대 속도 [mm/s] 또는 [mm/s, deg/s] (None이면 set_velx 값)
# acc  : 최대 가속도 [mm/s²] 또는 [mm/s², deg/s²]
# 비동기 함수 — 가장 최근 목표 TCP 위치를 추종

# 예제
set_velx(50); set_accx(100)
movej(posj(0, 0, 90, 0, 90, 0))

Xt = posx(368, 34.5, 442.5, 50.26, -180, 50.26)
servol(Xt, v=[100, 100], a=[200, 300])
```

### speedj — 관절 속도 제어
```python
speedj(vel, acc=None, time=None)
# vel  : list(float[6]) — 각 관절 목표 속도 [deg/s]
# acc  : 최대 가속도 [deg/s²] 또는 list(float[6])
# time : 도달 시간 [sec]
# 정지 시: vel=[0,0,0,0,0,0] 또는 stop() 호출
# 비동기 — DR_SERVO_OVERRIDE 방식 (항상 최신 속도 추종)

# 예제 — 1축 왕복 속도 제어
movej(posj(0, 0, 90, 0, 90, 0), v=30, a=60)
go_plus = True
while True:
    q = get_desired_posj()
    if go_plus:
        speedj([30, 5, 5, 5, 5, 5], a=60)
        if q[0] > 90: go_plus = False
    else:
        speedj([-30, -5, -5, -5, -5, -5], a=60)
        if q[0] < -90: go_plus = True
```

### speedl — 직교 속도 제어
```python
speedl(vel, acc=None, time=None, ref=DR_BASE)
# vel  : list(float[6]) — TCP 속도 [mm/s, mm/s, mm/s, deg/s, deg/s, deg/s]
# acc  : 가속도 (단일 float 또는 list)
# time : 지속 시간 [sec]
```

---

## 1-5. 비동기 모션 (Async Motion)

모든 동기 함수에 `a` 접두사를 붙이면 비동기 버전:

```python
amovej, amovel, amovec, amoveb, amovejx, amovesj, amovesx
amove_spiral, amove_periodic
```

비동기 함수는 동작 시작 직후 반환하며, `check_motion()`으로 완료 확인:

```python
amovel(p1, vel=100, acc=200)         # 비동기 시작
# ... 다른 작업 수행 ...
while check_motion():                 # 0=완료, 1=진행중
    wait(0.01)
```

---

## 1-6. 모션 보조 함수

```python
mwait(time=0)             # 모션 완료 대기 (time=0이면 현재 동작 완료까지)
check_motion()            # 모션 상태: 0=완료, 1=진행중
stop(st_mode)             # 정지: DR_STOP_TYPE_SLOW | DR_STOP_TYPE_FAST
motion_pause()            # 일시 정지
motion_resume()           # 재개
change_operation_speed(speed)  # 속도 배율 변경 [%]: 1~100

# 블렌딩 구간 지정 (begin_blend ~ end_blend 사이 모든 모션 자동 블렌딩)
begin_blend(radius=0)
movel(p1, vel=100, acc=200)
movel(p2, vel=100, acc=200)
movel(p3, vel=100, acc=200)
end_blend()

# 동적 경로 수정 (외부 신호로 실시간 오프셋 적용)
enable_alter_motion(n=6, mode=DR_ALTER_TOOL_MOTION,
                   ref=DR_TOOL, limit_dPOS=None, limit_dPOS_per=None)
alter_motion(dpos)        # dpos: [dx,dy,dz,drx,dry,drz] 오프셋
disable_alter_motion()
```

---

## 1-7. 힘·컴플라이언스 제어

### task_compliance_ctrl — 컴플라이언스 활성화
```python
task_compliance_ctrl(stx=[3000,3000,3000,200,200,200], time=0)
# stx  : float[6] — [Kx, Ky, Kz N/m, KRx, KRy, KRz N·m/rad]
#        기본값: [3000, 3000, 3000, 200, 200, 200]
#        병진 강성: 값이 낮을수록 유연(부드러움), 높을수록 딱딱함
#        Non-FTS 모델: float[3]으로도 사용 가능 (Translation 강성만)
# time : 강성 전환 시간 [sec] (범위: 0~1.0, 선형 보간)

# 관련 함수
set_stiffnessx(stx, time=0)     # 컴플라이언스 중 강성 업데이트
release_compliance_ctrl()        # 컴플라이언스 해제
set_damping_factor(factor, time=0)   # 감쇠 계수 설정
set_force_factor(factor, time=0)     # 힘 계수 설정
```

### set_desired_force — 목표 힘 설정
```python
set_desired_force(fd=[0,0,0,0,0,0], dir=[0,0,0,0,0,0],
                  time=0, mod=DR_FC_MOD_ABS)
# ※ 기준 좌표계는 set_ref_coord()로 사전 설정 (기본 DR_BASE)
# fd   : list(float[6]) — [Fx, Fy, Fz N, Mx, My, Mz N·m] 목표 힘/토크
# dir  : list(int[6])   — 각 축 제어 방식 (1=힘제어, 0=컴플라이언스제어)
# time : 힘 증가 시간 [sec] (범위: 0~1.0)
# mod  : DR_FC_MOD_ABS — 센서값 그대로 참조 (절대)
#        DR_FC_MOD_REL — 힘제어 시작 시점 기준 상대 외력만 참조
# Non-FTS 모델: fd/dir를 float[3]으로도 사용 가능 (Translation만)

release_force(time=0)           # 힘 제어 해제

# 힘 조건 확인
check_force_condition(axis, min=None, max=None, ref=DR_TOOL)
# axis : DR_AXIS_X~Z, DR_AXIS_A~C
# 반환 : True(조건 만족) / False

# 현재 툴 힘 측정 [N, N·m]
force = get_tool_force(ref=DR_TOOL)
# force[0~2]: Fx, Fy, Fz [N]
# force[3~5]: Mx, My, Mz [N·m]
```

**완전한 힘 제어 예제 — Z방향 20N 삽입:**
```python
# 1. 초기 자세로 이동
q0 = posj(0.0, 0.0, 90.0, 0.0, 90.0, 0.0)
set_velj(30.0); set_accj(60.0)
movej(q0)

# 2. 접근 (Base 기준 -Z방향 100mm)
set_velx(75.0); set_accx(100.0)
movel(posx(0, 0, -100, 0, 0, 0), mod=DR_MV_MOD_REL)

# 3. 컴플라이언스 + 힘 제어 시작 (Base 기준 -Z방향 20N)
k_d = [3000.0, 3000.0, 3000.0, 200.0, 200.0, 200.0]
task_compliance_ctrl(k_d)
set_desired_force([0, 0, -20, 0, 0, 0], dir=[0, 0, 1, 0, 0, 0])

# 4. 20N 힘 감지 시 y방향 이동
while True:
    if check_force_condition(DR_AXIS_Z, max=20.0) == 0:
        break
movel(posx(0, 200, 0, 0, 0, 0), mod=DR_MV_MOD_REL)

# 5. 종료 후 복귀
release_force()
wait(0.5)
release_compliance_ctrl()
movel(posx(0, 0, 150, 0, 0, 0), mod=DR_MV_MOD_REL)
movej(q0)
```

---

## 1-8. 디지털 / 아날로그 I/O

```python
# ── 디지털 출력 ──────────────────────────────
set_digital_output(index, val=None)
# index: 1~16 (val 있을 때), 또는 1~16/-1~-16 (val 없을 때: 양수=ON, 음수=OFF)
# val: 1(ON) / 0(OFF) / None(index 부호로 결정)
# 예: set_digital_output(1, ON)  # 1번 ON
#     set_digital_output(-3)     # 3번 OFF (val 생략)
#     set_digital_output(index, val, time, val2)  # pulse 출력
set_digital_outputs(bit_list)           # 여러 채널 동시: [(1,ON),(2,OFF),...]
set_digital_outputs(bit_start, bit_end, val)  # 범위 지정

# ── 디지털 입력 ──────────────────────────────
get_digital_input(index)                # 반환: ON/OFF
get_digital_inputs(bit_list)            # 여러 채널 동시 읽기
wait_digital_input(index, val, timeout=None)  # 특정 상태까지 대기

# ── 툴 플랜지 디지털 ─────────────────────────
set_tool_digital_output(index, val)
get_tool_digital_input(index)
wait_tool_digital_input(index, val, timeout=None)

# ── 아날로그 I/O ─────────────────────────────
set_mode_analog_output(ch, mod)         # ch:1~2, mod: DR_ANALOG_VOLTAGE|DR_ANALOG_CURRENT
set_mode_analog_input(ch, mod)
set_analog_output(ch, val)              # 전압: 0~10V, 전류: 4~20mA
get_analog_input(ch)                    # 반환: float

# ── 대기 함수 ────────────────────────────────
wait_analog_input(ch, condition, val, timeout=None)
# condition: DR_COND_GT(>), DR_COND_LT(<), DR_COND_EQ(==), DR_COND_NE(!=)
```

**그리퍼 제어 예제:**
```python
# 그리퍼 잡기 (DIO 1 ON)
set_digital_output(1, ON)

# 부품 감지 대기 (DIO 2 ON 될 때까지, 최대 5초)
wait_digital_input(2, ON, timeout=5)

# 그리퍼 열기 (DIO 1 OFF)
set_digital_output(1, OFF)
```

---

## 1-9. 좌표 변환 및 기구학

```python
# 좌표계 변환
result = trans(pos, delta, ref=None, ref_out=DR_BASE)
# pos    : 원본 위치 (posx 또는 list float[6])
# delta  : 오프셋 [dx,dy,dz,drx,dry,drz] 또는 posx
# ref    : 입력 기준 좌표계 (None이면 _g_coord 사용)
#          DR_TOOL일 때 ref_out은 무시되고 동일 좌표계로 반환
# ref_out: 출력 기준 좌표계 (기본 DR_BASE)
# 반환   : posx list(float[6])

# 순방향 기구학 (관절각 → TCP 좌표)
tcp_pos = fkin(pos, ref=DR_BASE)        # pos: posj → 반환: posx

# 역방향 기구학 (TCP 좌표 → 관절각)
joint_pos = ikin(pos, sol_space=0, ref=DR_BASE)  # pos: posx → 반환: posj

# 현재 상태 조회
cur_j = get_current_posj()              # 현재 관절각 [deg] → posj
cur_x = get_current_posx(ref=DR_BASE)  # 현재 TCP 위치 → posx
cur_vj = get_current_velj()             # 현재 관절 속도
cur_vx = get_current_velx(ref=DR_BASE) # 현재 TCP 속도
cur_torque = get_joint_torque()         # 관절 토크 [N·m]
ext_torque = get_external_torque()      # 외력 토크
rotm = get_current_rotm(ref=DR_BASE)   # 현재 회전 행렬 (3×3)

# 위치 연산 유틸리티
p_sum  = add_pose(posx1, posx2)        # 위치 덧셈
p_diff = subtract_pose(posx1, posx2)   # 위치 뺄셈
p_inv  = inverse_pose(posx1)            # 역변환
dist   = get_distance(posx1, posx2)    # 두 점 거리 [mm]
mid    = get_intermediate_pose(posx1, posx2, alpha=0.5)  # 보간 위치

# 좌표계 생성
coord = calc_coord(x1, x2, x3, x4, ref=DR_BASE, mod=0)
user_id = set_user_cart_coord(pos, ref=DR_BASE)  # 사용자 좌표계 등록
```

---

## 1-10. 회전 / 수학 함수

```python
# 각도 변환
d2r(deg)            # 도 → 라디안
r2d(rad)            # 라디안 → 도

# 삼각함수 (라디안 입력)
sin(x), cos(x), tan(x)
asin(x), acos(x), atan(x), atan2(y, x)

# 선형대수
norm(x)             # 벡터 노름
rotx(a), roty(a), rotz(a)   # 단축 회전 행렬 (라디안)

# 회전 표현 변환
rotm2eul(rotm)           # 회전행렬 → 오일러각 [ZYZ]
rotm2rotvec(rotm)        # 회전행렬 → 회전벡터
eul2rotm([a, b, g])      # 오일러각 → 회전행렬
eul2rotvec([a, b, g])    # 오일러각 → 회전벡터
rotvec2rotm([rx,ry,rz])  # 회전벡터 → 회전행렬
htrans(posx1, posx2)     # 동차 변환
```

---

## 1-11. 외부 통신

### 시리얼 통신
```python
ser = serial_open(port=None, baudrate=115200,
                  bytesize=DR_EIGHTBITS,
                  parity=DR_PARITY_NONE,
                  stopbits=DR_STOPBITS_ONE)
serial_write(ser, tx_data)                 # 전송
data = serial_read(ser, length=-1, timeout=-1) # 수신
serial_close(ser)
```

### TCP/IP 클라이언트
```python
sock = client_socket_open(ip, port)
client_socket_write(sock, tx_data)
data = client_socket_read(sock, length=-1, timeout=-1)
client_socket_close(sock)
```

### TCP/IP 서버
```python
sock = server_socket_open(port)
server_socket_write(sock, tx_data)
data = server_socket_read(sock, length=-1, timeout=-1)
server_socket_close(sock)
```

### Modbus TCP
```python
# 신호 등록
add_modbus_signal(ip, port, name, reg_type, index, value=0, slaveid=255)
# reg_type: DR_HOLDING_REGISTER | DR_INPUT_REGISTER | DR_COIL | DR_DISCRETE_INPUT

# 신호 읽기/쓰기
val = get_modbus_input(name)
set_modbus_output(name, value)
wait_modbus_input(name, val, timeout=None)

# 다중 신호
add_modbus_signal_multi(ip, port, slaveid=255, name=None,
                        reg_type=DR_HOLDING_REGISTER,
                        start_address=0, cnt=1)
vals = get_modbus_input_multi(name)   # 반환: 리스트

del_modbus_signal(name)               # 삭제
```

### EtherNet/IP / PROFINET
```python
set_output_register_bit(address, val)
set_output_register_int(address, val)
set_output_register_float(address, val)
get_input_register_bit(address)
get_input_register_int(address)
get_input_register_float(address)
```

---

## 1-12. 스레딩

```python
def my_thread():
    while True:
        # 백그라운드 작업 (예: 센서 폴링)
        sensor_val = get_analog_input(1)
        wait(0.1)

th_id = thread_run(my_thread, loop=False)  # loop=True면 함수 종료 후 재시작
thread_pause(th_id)
thread_resume(th_id)
thread_stop(th_id)
state = thread_state(th_id)  # 0=정지, 1=실행중, 2=일시정지
```

---

## 1-13. TP (티치 펜던트) UI

```python
tp_popup(message, pm_type=DR_PM_MESSAGE, button_type=0)
# pm_type: DR_PM_MESSAGE | DR_PM_WARNING | DR_PM_ALARM
# button_type: 0=확인만, 1=확인+취소, 2=예+아니오

tp_log(message)                           # 로그 출력
val = tp_get_user_input(message, input_type)  # 사용자 입력 받기
```

---

## 1-14. 비전 통합

### Doosan SVM (내장 비전)
```python
svm_connect(ip="192.168.137.5", port=20)
svm_set_job(job_id)
svm_detect_landmark(job_id)              # 랜드마크 감지
info = svm_get_vision_info(job_id)       # 비전 결과
offset = svm_get_offset_pos(robot_init_pos, job_id, tool_id)
svm_disconnect()
```

### Pickit 3D 비전
```python
pickit_connect(ip)
pickit_change_configuration(setup_id, product_id)
pickit_detection(offset_z=0)             # 물체 감지
pickit_next_object(offset_z=0)           # 다음 물체
pickit_disconnect()
```

### Cognex 2D 비전
```python
vs_connect(ip_addr, port_num=9999)
vs_set_job(job_name)
vs_trigger()
vs_set_init_pos(vision_posx_init, robot_posx_init)
offset = vs_get_offset_pos(vision_posx_meas)
vs_disconnect()
```

---

## 1-15. 용접 (Welding) 어플리케이션

### 아날로그 용접
```python
app_weld_enable_analog(
    ch_v_out=[1,0], spec_v_out=[0,0,0,0],   # 전압 출력 채널/스펙
    ch_f_out=[2,0], spec_f_out=[0,0,0,0],   # 와이어 속도 출력
    ch_v_in=[1,0], spec_v_in=[0,0,0,0],     # 전압 피드백 입력
    ch_c_in=[2,0], spec_c_in=[0,0,0,0],     # 전류 피드백 입력
    ch_arc_on=1, ch_gas_on=2               # 아크 ON/가스 ON 채널
)
app_weld_set_weld_cond_analog(
    flag_dry_run=0, v_target=0, f_target=0,
    vel_target=0, vel_min=0, vel_max=0,
    weld_proc_param=[0.2,0.2,0.5,0.5,0.5,0.2,0.2,0.5,0.5]
)
app_weld_disable_analog()
```

### 위빙 패턴
```python
# 지그재그 위빙
app_weld_weave_cond_zigzag(
    wv_offset=[0,0], wv_ang=0,
    wv_param=[3, 0.6]  # [폭mm, 주기sec]
)
# 사다리꼴 위빙
app_weld_weave_cond_trapezoidal(
    wv_offset=[0,0], wv_ang=0,
    wv_param=[0, 1.5, 0, -1.5, 0.3, 0.1, 0.3, 0.3, 0.1, 0.3]
)
# 원형 위빙
app_weld_weave_cond_circular(wv_offset=[0,0], wv_ang=0, wv_param=[3,3,0.3,0.3])
# 사인파 위빙
app_weld_weave_cond_sinusoidal(wv_offset=[0,0], wv_ang=0, wv_param=[3,0.6])
```

---

## 1-16. 컨베이어 트래킹

```python
set_conveyor_ex(
    name="conv1", conv_type=0,
    encoder_channel=1,              # 엔코더 채널
    count_per_dist=5000,            # 펄스/mm
    conv_coord=posx(0,0,0,0,0,0),  # 컨베이어 좌표계
    ref=DR_BASE,
    conv_speed=100.0,               # 최대 속도 [mm/s]
    min_dist=0.0, max_dist=1000.0  # 트래킹 범위
)
obj = get_conveyor_obj(conv_id, timeout=None, container_type=DR_FIFO)
tracking_conveyor(conv_id, time=0.3)    # 트래킹 시작
# ... 작업 수행 ...
untracking_conveyor(conv_id, time=0.3)  # 트래킹 종료
```

---

## 1-17. 시스템 / 유틸리티

```python
wait(time)           # 대기 [sec]
exit()               # 프로그램 종료
sub_program_run(name)  # 서브 프로그램 실행

# 안전
change_collision_sensitivity(value)  # 충돌 감도 0~100
set_singularity_handling(mode)       # 특이점 처리 모드

# 정보 조회
model = get_robot_model()
sn = get_robot_serial_num()
speed = get_operation_speed_ratio()

# 타이머
start_timer()
elapsed = end_timer()  # [sec]
```

---

## 1-18. DRL 상수 빠른 참조

```python
# 좌표계
DR_BASE   = 0    # 베이스 좌표계
DR_WORLD  = 1    # 월드 좌표계
DR_TOOL   = 2    # 툴 좌표계

# 모션 모드
DR_MV_MOD_ABS = 0   # 절대 좌표
DR_MV_MOD_REL = 1   # 상대 좌표

# 블렌딩 타입
DR_MV_RA_DUPLICATE = 0  # 감속 후 재가속
DR_MV_RA_OVERRIDE  = 1  # 속도 유지 블렌딩

# posb 세그먼트 타입 (moveb/amoveb에서 사용)
DR_LINE   = 0  # 선형 세그먼트
DR_CIRCLE = 1  # 원호 세그먼트

# movec 방향 제어
DR_MV_ORI_TEACH  = 0  # 티치 방향 (시작→끝 보간)
DR_MV_ORI_FIXED  = 1  # 고정 방향 (현재 자세 유지)
DR_MV_ORI_RADIAL = 2  # 원주구속 방향
DR_MV_ORI_INTENT = 3  # 사용자설정 (pos1 자세 경유)

# move_spiral 반경/회전 방향
DR_SPIRAL_OUTWARD = 0  # 외향 (현재→rmax)
DR_SPIRAL_INWARD  = 1  # 내향 (rmax→중심)
DR_ROT_FORWARD    = 0  # 정방향 (+)
DR_ROT_REVERSE    = 1  # 역방향 (-)

# servoj 모드
DR_SERVO_OVERRIDE = 0  # 최신 명령 추종
DR_SERVO_QUEUE    = 1  # 큐 모드 (최대 100개)

# movesx 속도 옵션
DR_MVS_VEL_NONE  = 0  # 변속 (기본)
DR_MVS_VEL_CONST = 1  # 등속

# 축 상수
DR_AXIS_X = 0; DR_AXIS_Y = 1; DR_AXIS_Z = 2
DR_AXIS_A = 3; DR_AXIS_B = 4; DR_AXIS_C = 5

# 힘 제어 모드
DR_FC_MOD_ABS = 0   # 절대 힘
DR_FC_MOD_REL = 1   # 상대 힘

# 아날로그 모드
DR_ANALOG_VOLTAGE = 0
DR_ANALOG_CURRENT = 1

# 조건 상수 (wait_analog_input 등)
DR_COND_GT = 0  # >
DR_COND_LT = 1  # <
DR_COND_EQ = 2  # ==
DR_COND_NE = 3  # !=

# 정지 타입
DR_STOP_TYPE_SLOW = 0
DR_STOP_TYPE_FAST = 1

# 시리얼 설정
DR_EIGHTBITS   = 8
DR_PARITY_NONE = 'N'
DR_STOPBITS_ONE = 1

# TP 팝업
DR_PM_MESSAGE = 0
DR_PM_WARNING = 1
DR_PM_ALARM   = 2

# ON/OFF
ON  = 1
OFF = 0
```

---

## 1-19. DRL 완전 예제 — 픽앤플레이스

```python
# ─── 두산 로봇 픽앤플레이스 DRL 예제 ───────────
# 설정
set_velj(30);  set_accj(60)
set_velx(100); set_accx(200)

HOME    = posj(0, 0, 90, 0, 90, 0)
PICK_UP = posx(400, 200, 500, 0, 180, 0)   # 픽 위 대기 위치
PICK    = posx(400, 200, 350, 0, 180, 0)   # 실제 픽 위치
PLACE_UP = posx(600, -200, 500, 0, 180, 0)
PLACE    = posx(600, -200, 350, 0, 180, 0)

GRIPPER_OUT = 1   # 그리퍼 디지털 출력 채널
SENSOR_IN   = 2   # 부품 감지 센서 입력 채널

# 그리퍼 초기화 (열기)
set_digital_output(GRIPPER_OUT, OFF)

# 메인 루프
for cycle in range(5):
    # 1. 홈으로
    movej(HOME)

    # 2. 픽 위치 이동 (블렌딩으로 부드럽게)
    movel(PICK_UP)
    movel(PICK)

    # 3. 그리퍼 닫기 및 부품 감지 확인
    set_digital_output(GRIPPER_OUT, ON)
    wait_digital_input(SENSOR_IN, ON, timeout=3)

    # 4. 들어올리기
    movel(PICK_UP)

    # 5. 플레이스 이동
    movel(PLACE_UP)
    movel(PLACE)

    # 6. 그리퍼 열기
    set_digital_output(GRIPPER_OUT, OFF)
    wait(0.3)

    # 7. 복귀
    movel(PLACE_UP)

tp_log("픽앤플레이스 완료!")
```

---

# PART 2 — DRFL C++ API (외부 PC, CDRFLEx)

외부 PC에서 C++로 로봇을 제어하는 라이브러리입니다.
모든 함수는 `CDRFLEx` 클래스 멤버이며 `DRFLEx.h`에 선언됩니다.

```cpp
#include "DRFLEx.h"
using namespace DRAFramework;
CDRFLEx drfl;
```

---

## 2-1. 연결 / 모드 관리

```cpp
// 연결
drfl.open_connection("192.168.137.100", 12345);
drfl.close_connection();

// 모드 조회·변경 (주의: set_robot_mode 반환 0=성공, 1=실패 — 다른 함수와 반대!)
ROBOT_MODE mode = drfl.get_robot_mode();
bool err = drfl.set_robot_mode(ROBOT_MODE_AUTONOMOUS);

// 상태 조회
ROBOT_STATE state = drfl.get_robot_state();

// 현재 위치
LPROBOT_POSE  x = drfl.get_current_posx(COORDINATE_SYSTEM_BASE);
LPROBOT_JOINT q = drfl.get_current_posj();
```

---

## 2-2. DRFL 모션 함수

```cpp
// movej (오버로드 1: 균일 속도)
bool drfl.movej(float fTargetPos[6], float fTargetVel, float fTargetAcc,
                float fTargetTime=0.f, MOVE_MODE eMoveMode=MOVE_MODE_ABSOLUTE,
                float fBlendingRadius=0.f,
                BLENDING_SPEED_TYPE eBlendingType=BLENDING_SPEED_TYPE_DUPLICATE);

// movej (오버로드 2: 축별 속도)
bool drfl.movej(float fTargetPos[6], float fTargetVel[6], float fTargetAcc[6],
                float fTargetTime=0.f, MOVE_MODE eMoveMode=MOVE_MODE_ABSOLUTE,
                float fBlendingRadius=0.f,
                BLENDING_SPEED_TYPE eBlendingType=BLENDING_SPEED_TYPE_DUPLICATE);

// movel — 직선 경로
bool drfl.movel(float fTargetPos[6],   // [X,Y,Z mm, Rx,Ry,Rz deg]
                float fTargetVel[2],   // [선속도 mm/s, 각속도 deg/s]
                float fTargetAcc[2],   // [선가속도, 각가속도]
                float fTargetTime=0.f,
                MOVE_MODE eMoveMode=MOVE_MODE_ABSOLUTE,
                MOVE_REFERENCE eMoveReference=MOVE_REFERENCE_BASE,
                float fBlendingRadius=0.f,
                BLENDING_SPEED_TYPE eBlendingType=BLENDING_SPEED_TYPE_DUPLICATE,
                DR_MV_APP eAppType=DR_MV_APP_NONE);

// movec — 원호 경로 (DRCF v2 전용)
bool drfl.movec(float fTargetPos[2][6],  // [0]=경유점, [1]=목표점
                float fTargetVel[2], float fTargetAcc[2],
                float fTargetTime=0.f,
                MOVE_MODE eMoveMode=MOVE_MODE_ABSOLUTE,
                MOVE_REFERENCE eMoveReference=MOVE_REFERENCE_BASE,
                float fTargetAngle1=0.f, float fTargetAngle2=0.f,
                float fBlendingRadius=0.f,
                BLENDING_SPEED_TYPE eBlendingType=BLENDING_SPEED_TYPE_DUPLICATE,
                MOVE_ORIENTATION eOrientation=DR_MV_ORI_TEACH,
                DR_MV_APP eAppType=DR_MV_APP_NONE);

// movejx — 직교 목표 관절 이동
bool drfl.movejx(float fTargetPos[6], unsigned char iSolutionSpace,
                 float fTargetVel, float fTargetAcc,
                 float fTargetTime=0.f,
                 MOVE_MODE eMoveMode=MOVE_MODE_ABSOLUTE,
                 MOVE_REFERENCE eMoveReference=MOVE_REFERENCE_BASE,
                 float fBlendingRadius=0.f,
                 BLENDING_SPEED_TYPE eBlendingType=BLENDING_SPEED_TYPE_DUPLICATE);
// iSolutionSpace: 0~7 또는 255(자동)

// movesj — 관절 스플라인
bool drfl.movesj(float fTargetPos[100][6], unsigned char nPosCount,
                 float fTargetVel, float fTargetAcc,
                 float fTargetTime=0.f, MOVE_MODE eMoveMode=MOVE_MODE_ABSOLUTE);

// moveb — 혼합 경로
// MOVE_POSB 구조체: {float _fTargetPos[2][6], float _fBlendRad, uchar _blendType}
bool drfl.moveb(MOVE_POSB tTargetPos[25], unsigned char nPosCount,
                float fTargetVel[2], float fTargetAcc[2],
                float fTargetTime=0.f,
                MOVE_MODE eMoveMode=MOVE_MODE_ABSOLUTE,
                MOVE_REFERENCE eMoveReference=MOVE_REFERENCE_BASE,
                DR_MV_APP eAppType=DR_MV_APP_NONE);
```

---

## 2-3. DRFL I/O

```cpp
// 디지털 출력
bool drfl.set_digital_output(GPIO_CTRLBOX_DIGITAL_INDEX eGpioIndex, bool bOnOff);
// eGpioIndex: GPIO_CTRLBOX_DIGITAL_INDEX_1 ~ _16

// 디지털 입력
bool drfl.get_digital_input(GPIO_CTRLBOX_DIGITAL_INDEX eGpioIndex);

// 아날로그
bool drfl.set_analog_output(GPIO_CTRLBOX_ANALOG_INDEX eGpioIndex, float fValue);
float drfl.get_analog_input(GPIO_CTRLBOX_ANALOG_INDEX eGpioIndex);

// 툴 플랜지
bool drfl.set_tool_digital_output(GPIO_TOOL_DIGITAL_INDEX eGpioIndex, bool bOnOff);
bool drfl.get_tool_digital_input(GPIO_TOOL_DIGITAL_INDEX eGpioIndex);
```

---

## 2-4. DRFL 힘/컴플라이언스

```cpp
// 컴플라이언스 활성화
// fTargetStiffness: [Kx,Ky,Kz N/m 0~20000, KRx,KRy,KRz N·m/rad 0~400]
bool drfl.task_compliance_ctrl(float fTargetStiffness[6],
                                COORDINATE_SYSTEM eForceReference=COORDINATE_SYSTEM_TOOL,
                                float fTargetTime=0.f);
bool drfl.release_compliance_ctrl();

// 목표 힘 설정
bool drfl.set_desired_force(float fTargetForce[6],      // [Fx,Fy,Fz N, Mx,My,Mz N·m]
                             unsigned char fDir[6],       // 적용 여부 0/1
                             COORDINATE_SYSTEM eRef=COORDINATE_SYSTEM_TOOL,
                             int iSign=0);               // 0=양방향, 1=양방향, -1=음방향

// 힘 조건 확인
bool drfl.check_force_condition(FORCE_AXIS eAxis, float fMin, float fMax,
                                 COORDINATE_SYSTEM eRef=COORDINATE_SYSTEM_TOOL);

// 툴 힘 측정
LPROBOT_FORCE drfl.get_tool_force(COORDINATE_SYSTEM eRef=COORDINATE_SYSTEM_TOOL);
```

---

## 2-5. DRFL 실시간(RT) 제어 — 1kHz UDP

```cpp
// RT 연결 및 설정
bool drfl.connect_rt_control("192.168.137.100", 12347);
bool drfl.set_rt_control_input("v1.0", 0.001f, 4);   // 버전, 주기[sec], 손실 허용
bool drfl.set_rt_control_output("v1.0", 0.001f, 4);
bool drfl.start_rt_control();

// RT 관절 서보 (비동기 — 즉시 반환)
bool drfl.servoj_rt(float fTargetPos[6],  // 목표 관절각 [deg]
                    float fTargetVel[6],  // -10000: 자동계산
                    float fTargetAcc[6],  // -10000: 자동계산
                    float fTargetTime);   // 권장: >= 20×통신주기

// RT TCP 서보
bool drfl.servoL_rt(float fTargetPos[6], float fTargetVel[2],
                    float fTargetAcc[2], float fTargetTime);

// RT 데이터 읽기
LPRT_OUTPUT_DATA_LIST data = drfl.read_data_rt();
// data->actual_joint_position[6] : 현재 관절각 [deg]
// data->actual_joint_velocity[6] : 현재 관절속도 [deg/s]
// data->actual_joint_torque[6]   : 현재 관절토크 [Nm]

bool drfl.stop_rt_control();
bool drfl.disconnect_rt_control();
```

**DRFL RT 제어 완전 예제:**
```cpp
drfl.open_connection("192.168.137.100", 12345);
drfl.set_robot_mode(ROBOT_MODE_AUTONOMOUS);

drfl.connect_rt_control("192.168.137.100", 12347);
drfl.set_rt_control_input("v1.0", 0.001f, 4);
drfl.set_rt_control_output("v1.0", 0.001f, 4);
drfl.start_rt_control();

float pos[6] = {0,0,0,0,0,0};
float vel[6] = {-10000,-10000,-10000,-10000,-10000,-10000};
float acc[6] = {-10000,-10000,-10000,-10000,-10000,-10000};

for (int i = 0; i < 5000; ++i) {
    auto data = drfl.read_data_rt();
    if (data) {
        float curJ[6];
        memcpy(curJ, data->actual_joint_position, sizeof(float)*6);
    }
    pos[0] = 20.f * sinf(i * 0.001f * 2.f * M_PI * 0.2f);  // 0.2Hz 사인파
    drfl.servoj_rt(pos, vel, acc, 0.008f);
    std::this_thread::sleep_for(std::chrono::milliseconds(1));
}

drfl.stop_rt_control();
drfl.disconnect_rt_control();
drfl.close_connection();
```

---

## 2-6. DRFL 모니터링 콜백

```cpp
// 상태 변경 콜백
drfl.set_on_monitoring_state([](const ROBOT_STATE eState) {
    printf("State: %d\n", (int)eState);
});

// 주기적 모니터링 데이터 콜백
drfl.set_on_monitoring_data([](const LPMONITORING_DATA pData) {
    if (!pData) return;
    for (int i = 0; i < 6; i++)
        printf("J%d: %.2f  ", i+1, pData->actual_joint_position[i]);
    printf("\n");
});

// I/O 상태 콜백
drfl.set_on_monitoring_ctrl_io([](const LPMONITORING_CTRL_IO pData) {
    // pData->ctrl_box_digital_output_status 등 확인
});
```

---

## 주요 에러 해결

| 증상 | 원인 | 해결법 |
|------|------|--------|
| movej/movel 응답 없음 | Auto 모드 아님 | `set_robot_mode(ROBOT_MODE_AUTONOMOUS)` |
| `set_robot_mode` 반환 1 | 보호 정지·비상 정지 | 상태 확인 후 `release_protective_stop()` |
| RT 서보 진동/떨림 | `fTargetTime` 너무 짧음 | `>= 20×1ms = 0.02f` 권장 |
| `movec` 오류 | DRCF 버전 불일치 | DRCF_VERSION==2 확인 |
| `moveb` 에러 | `_fBlendRad==0` | 모든 세그먼트 `radius > 0` 설정 |
| `read_data_rt` nullptr | RT 미시작 or 패킷 미수신 | `start_rt_control()` 후 약 100ms 대기 |
| DRL servoj 진동 | `time` 너무 짧음 | `time >= 0.01` (10ms) 권장 |
| 힘 제어 불안정 | 강성값 너무 높음 | 병진 1500~2500 N/m, 회전 100~200 N·m/rad |
