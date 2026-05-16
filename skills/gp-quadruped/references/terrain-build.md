# terrain-build.md — 절차적 볼록 산악 지형 + D2 클램프

GP 지형 생성. USD/PhysX 일반은 [[isaac-sim-bridge]] — 여기서는 **GP 볼록 지형
+ flat 정책 운용 클램프** 패턴.

## 목차
1. 원칙 (볼록 + D2 클램프)
2. heightfield 생성 (가우시안 산괴 + ridged fBm)
3. USD 메시 작성 (제자리 덮어쓰기 — 레이스 회피)
4. 정적 삼각 collider
5. 텍스처/철조망
6. 함정 체크리스트

---

## 1. 원칙

- 라이브러리에 실 산악 에셋 없음(조사 완료) → **절차적 생성이 정석**.
- 사진(GP)처럼 **z 볼록**(가운데 솟음) + 울퉁불퉁.
- **D2 클램프(불변식 2)**: 번들 ANYmal flat 정책이 견디도록 국소 경사·진폭
  제한. 클램프는 우회가 아니라 *운용 조건*. 진짜 험지 = P4 재학습.
- 권장 클램프: 인접 셀 경사 ≲ 15°, 잔굴곡 진폭 ≲ ~0.12 m(ANYmal foot
  clearance 이내). 큰 윤곽(완만 볼록)은 OK, 고주파 굴곡만 제한.

## 2. heightfield 생성

```python
import numpy as np
S, N = 35.0, 220                  # ±35 m, 그리드
xs = np.linspace(-S, S, N+1)
gx, gy = np.meshgrid(xs, xs, indexing="ij")
rng = np.random.default_rng(11)
z = np.zeros_like(gx)
# (a) 큰 볼록 산괴: 다중 가우시안 — 전체 z 볼록 윤곽
for _ in range(4):
    cx, cy = rng.uniform(-S*0.6, S*0.6, 2)
    z += rng.uniform(8, 16) * np.exp(-((gx-cx)**2+(gy-cy)**2)/(2*rng.uniform(9,13)**2))
# (b) 거친 잔굴곡: value-noise fBm + ridged (저진폭으로 제한 → D2)
def vnoise(freq):
    gs=max(3,int(2*S*freq)+2); lat=rng.standard_normal((gs,gs))
    u=(gx-gx.min())/(gx.max()-gx.min())*(gs-1); v=(gy-gy.min())/(gy.max()-gy.min())*(gs-1)
    x0=np.floor(u).astype(int);y0=np.floor(v).astype(int)
    x1=np.clip(x0+1,0,gs-1);y1=np.clip(y0+1,0,gs-1)
    fx=u-x0;fy=v-y0;sx=fx*fx*(3-2*fx);sy=fy*fy*(3-2*fy)
    nx0=lat[x0,y0]*(1-sx)+lat[x1,y0]*sx; nx1=lat[x0,y1]*(1-sx)+lat[x1,y1]*sx
    return nx0*(1-sy)+nx1*sy
rough = np.zeros_like(gx); f,a = 0.04, 1.0
for _ in range(5):
    n=vnoise(f); rough += a*n + (a*0.8)*(1-np.abs(n)); f*=2; a*=0.5
# --- D2 클램프: 잔굴곡 진폭 제한 ---
AMP = 0.12
rough = AMP * rough / (np.abs(rough).max() + 1e-9)
z = z + rough
z -= z.min()                       # 바닥 0
# (옵션) 경사 클램프: 인접 셀 기울기 제한
dz = np.gradient(z)                 # 필요 시 max slope 로 z 평활
```

> 큰 윤곽 진폭(가우시안)은 *완만*하면 경사 자체가 작아 flat 정책이 견딘다.
> 핵심은 (b) 고주파 굴곡을 `AMP` 로 강하게 제한하는 것.

## 3. USD 메시 작성 (제자리 덮어쓰기)

⚠️ `stage.RemovePrim(path)` 직후 같은 경로 `UsdGeom.Mesh.Define()` 는
**제거 레이스**로 갱신이 누락될 수 있다(실측 확인됨). → 기존 메시의
points/topology 를 **제자리 덮어쓰기**:

```python
from pxr import UsdGeom, Gf, Vt, UsdPhysics
pts = Vt.Vec3fArray([Gf.Vec3f(float(gx[i,j]),float(gy[i,j]),float(z[i,j]))
                     for i in range(N+1) for j in range(N+1)])
idx=[]
for i in range(N):
    for j in range(N):
        a=i*(N+1)+j; idx += [a,a+1,a+N+2,a+N+1]
t = stage.GetPrimAtPath("/World/Terrain")
if not t.IsValid():
    t = UsdGeom.Mesh.Define(stage, "/World/Terrain").GetPrim()
m = UsdGeom.Mesh(t)
m.GetPointsAttr().Set(pts)
m.GetFaceVertexCountsAttr().Set(Vt.IntArray([4]*(N*N)))
m.GetFaceVertexIndicesAttr().Set(Vt.IntArray(idx))
m.GetSubdivisionSchemeAttr().Set("none")
```

MCP 환경이면 결과를 `/tmp` 파일에 쓰고 Bash 로 검증([[isaac-sim-mcp]]).

## 4. 정적 삼각 collider

지형은 정적 → 삼각 메시 collider 허용(동적이면 불가).

```python
UsdPhysics.CollisionAPI.Apply(t)
UsdPhysics.MeshCollisionAPI.Apply(t).CreateApproximationAttr("none")  # 삼각 그대로
```

마찰 0.8 권장. 동적 바디에 trimesh 금지(PhysX 가 convexHull 로 자동 강등).

## 5. 텍스처 / 철조망

- 머티리얼: OmniPBR + Poly Haven / ambientCG(CC0) 적설·암벽. GUI Materials
  드래그도 가능. 옵션 P4: 국토지리정보원 실 DEM heightfield 임포트.
- `/World/Fence`(철조망): 시각 메시는 디테일, **충돌은 박스/실린더 proxy
  로 분리**(나선 메시 그대로 collider → 폴리곤 폭증). 시각 prim 과
  collision proxy 를 별도 child 로.

## 6. 함정 체크리스트

- [ ] (b) 고주파 굴곡 `AMP` 클램프 적용(D2). 누락 시 보행 붕괴.
- [ ] RemovePrim+Define 동일경로 금지 → 제자리 덮어쓰기.
- [ ] collider approximation="none" + 정적(RigidBody 없음).
- [ ] 철조망 충돌은 proxy 분리.
- [ ] 로봇 시작 z 를 지형 표면 위로(`z.max()` 부근 + clearance).
- [ ] 변경 후 영향: route waypoint z, 로봇 스폰 위치 재확인.
