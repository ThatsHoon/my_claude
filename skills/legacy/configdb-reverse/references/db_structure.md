---
name: db_structure
description: Wuthering Waves ConfigDB 전체 DB 파일 목록, 테이블 구조, 컬럼 레이아웃 참조
type: reference
---

# ConfigDB DB 파일 및 테이블 구조

베이스 경로: `Extract/Exports/Client/Content/Aki/ConfigDB/`

---

## db_weapon.db

### weaponconf
| 컬럼 | 타입 | 설명 |
|------|------|------|
| ItemId | INT PK | 무기 고유 ID (예: 21050066) |
| IsShow | INT | 표시 여부 (1=공개) |
| BinData | BLOB | FlatBuffer 인코딩 데이터 |

**BinData 필드 인덱스 (검증 완료)**:
| fi | 타입 | 의미 |
|----|------|------|
| f0 | i32 | ItemId (direct) |
| f2 | string | name TextMap key |
| f3 | i32 | rarity (1-5) |
| f4 | i32 | weapon type (1=대검, 2=직검, 3=권총, 4=권갑, 5=증폭기) |
| f10 | byte vec 8B | primary stat: `float32 base` + `u32 PropertyIndex_id` |
| f12 | nested FB | secondary stat: f0=PropertyIndex_id, f1=float32 base |
| f14 | i32 | ResonId → weaponreson.ResonId (기술 효과 참조) |
| f18 | string | effect TextMap key |
| f19 | nested vec | param 2D string array (스킬 효과 수치) |
| f22 | string | lore/desc TextMap key |
| f23 | string | icon path (/Game/Aki/...) |

### weaponreson
무기 공명(기술 효과) 레벨별 데이터.

| 컬럼 | 타입 | 설명 |
|------|------|------|
| Id | INT | sequential 순번 (무기 ID 아님!) |
| ResonId | INT | weaponconf.f14 값과 일치 (join key) |
| Level | INT | 공명 레벨 (1-5) |
| BinData | BLOB | FlatBuffer |

**TextMap key 패턴**: `WeaponReson_{ResonId}_Name` (Id가 아닌 ResonId 사용!)

### weaponbreach
무기 돌파(성장) 단계별 데이터.

| 컬럼 | 타입 | 설명 |
|------|------|------|
| Id | INT | sequential 순번 |
| BreachId | INT | weaponconf.ItemId와 일치 (join key) |
| Level | INT | 돌파 레벨 (0-6) |
| BinData | BLOB | FlatBuffer |

**주요 BinData 필드**:
- f4: MaxLevel (i32) — 해당 돌파 단계의 최대 레벨 (20/40/50/60/70/80/90)
- f5: item 재료 목록 (KV vector: Key=ItemId, Value=count)
- f6: 골드 비용 (i32) — Level 6(최고 돌파)에는 없음 → `{key:2, value:0}` 출력

**중요 — BreachId 없는 무기 예외 처리**:

일부 무기는 `weaponconf`에 존재하지만 `weaponbreach`에 자신의 `BreachId` 항목이 없다.
이 경우 동일한 돌파 재료를 공유하는 다른 무기의 `BreachId`로 fallback해야 한다.
스탯 base값(f10, f12)은 각 무기가 독립 보유 — 재료(f5)만 공유.

검증된 fallback (WW 2.x):
- 21010045 → 21010066
- 21020045 → 21020076
- 21030045 → 21030046
- 21040045 → 21040056
- 21050045 → 21021140

탐지: `SELECT DISTINCT BreachId FROM weaponbreach`와 `weaponconf.ItemId` 비교로 누락 무기 확인.

### weaponlevel
무기 레벨업 재료 소모 테이블.

| 컬럼 | 타입 | 설명 |
|------|------|------|
| Id | INT | sequential |
| Level | INT | 레벨 |
| BinData | BLOB | FlatBuffer |

### weaponskin
무기 외형(스킨) 데이터.

| 컬럼 | 타입 | 설명 |
|------|------|------|
| Id | INT | 스킨 Id |
| WeaponSkinType | INT | 무기 타입 |
| BinData | BLOB | FlatBuffer |

**주요 BinData 필드**:
- f2: WeaponSkinType (i32)
- f3: name TextMap key (string)
- f5: rank/rarity (i32)
- f13: desc TextMap key (string)
- f15: icon path (string)

---

## db_property.db

### propertyindex
스탯 속성 정의 테이블 (ATK, DEF, HP, 치명타율 등).

| 컬럼 | 타입 | 설명 |
|------|------|------|
| Id | INT PK | PropertyIndex ID |
| BinData | BLOB | FlatBuffer |

**주요 BinData 필드**:
- f0: Id (i32)
- f7: Key string (예: "Attr_Prop_Atk")
- f9: is_percent 판별 필드
  - string `"PropertyIndex_{n}_Dec"` → is_percent=True (백분율)
  - int 28 → is_percent=False (절대값)
  - int 32 → ratio (×100 표시)

### weaponpropertygrowth
무기 성장 곡선 테이블. **모든 무기가 동일한 2개 곡선 공유**.

| 컬럼 | 타입 | 설명 |
|------|------|------|
| Id | INT | sequential |
| CurveId | INT | 1=primary(ATK), 2=secondary |
| Level | INT | 레벨 (1-90) |
| BreachLevel | INT | 돌파 레벨 (0-6) |
| BinData | BLOB | FlatBuffer |

**BinData 필드**:
- f4: growth factor (i32) — 실제값 = base × (factor / 10000)

**사용법**: base_primary × (curve1_factor/10000), base_secondary × (curve2_factor/10000)

---

## db_model_config_preload.db

### modelconfigpreload
무기/캐릭터 3D 모델 경로.

| 컬럼 | 타입 | 설명 |
|------|------|------|
| Id | INT | weapon ItemId 또는 캐릭터 Id |
| BinData | BLOB | FlatBuffer (여러 경로 포함) |

**주의**: 모델 경로는 weaponconf BinData가 아닌 이 테이블에서 추출해야 함.
BinData를 바이트 스캔하여 `/Model/` 포함 문자열 찾기:
```python
while pos < buflen - 4:
    slen = struct.unpack_from('<I', buf, pos)[0]
    if 4 < slen < 300:
        s = buf[pos+4:pos+4+slen].decode('utf-8', errors='replace')
        if s.startswith('/Game/') and '/Model/' in s:
            return s
    pos += 1
```

---

## {lang}/lang_multi_text.db

TextMap (텍스트 현지화) 데이터베이스.

경로: `{lang}/lang_multi_text.db` (lang = ko, en, zh-Hans, ja 등)

### MultiText
| 컬럼 | 타입 | 설명 |
|------|------|------|
| Id | TEXT PK | TextMap 키 (예: "WeaponConf_21050066_WeaponName") |
| Content | TEXT | 현지화된 텍스트 |

**주요 TextMap 키 패턴**:
- 무기 이름: `WeaponConf_{ItemId}_WeaponName`
- 무기 효과: `WeaponConf_{ItemId}_Desc`
- 무기 설명: `WeaponConf_{ItemId}_BgDescription`
- 공명 효과 이름: `WeaponReson_{ResonId}_Name` ← ResonId 사용!
- 공명 효과 설명: `WeaponReson_{ResonId}_Desc`
- 캐릭터 이름: `RoleInfo_{RoleId}_Name`
- 스킬 이름: `Skill_{SkillId}_Name`

---

## db_role.db

캐릭터(역할) 기본 정보.

### RoleInfo
| 컬럼 | 타입 | 설명 |
|------|------|------|
| Id | INT PK | 캐릭터 Id (예: 1102 = 산화) |
| BinData | BLOB | FlatBuffer |

**주요 필드**: 이름키, 닉네임키, 희귀도, 무기타입, 속성, 아이콘 경로, 태그

### RoleBreach
캐릭터 돌파 데이터.

| 컬럼 | 타입 | 설명 |
|------|------|------|
| Id | INT | sequential |
| RoleId | INT | 캐릭터 Id |
| Level | INT | 돌파 레벨 |
| BinData | BLOB | KV vector 재료 포함 |

### RoleSkin
캐릭터 스킨.

| 컬럼 | 타입 | 설명 |
|------|------|------|
| Id | INT | 스킨 Id |
| RoleId | INT | 캐릭터 Id |
| BinData | BLOB | 모델 경로, FormationSpineSkeletonData 포함 |

---

## db_skill.db

### Skill
스킬 기본 정보.

| 컬럼 | 타입 | 설명 |
|------|------|------|
| Id | INT PK | 스킬 Id |
| BinData | BLOB | DamageList, Params, SkillGroupId 포함 |

**DamageList 디코딩**: int32 쌍 → float64 → Damage.Id

### SkillDescription
스킬 설명 (레벨별).

| 컬럼 | 타입 | 설명 |
|------|------|------|
| Id | INT PK | = SkillLevelGroupId * 1000 + level |
| SkillLevelGroupId | INT | 스킬 레벨 그룹 |
| BinData | BLOB | Description TextMap 키, SkillAttribute 포함 |

### SkillTree
스킬 트리 노드.

| 컬럼 | 타입 | 설명 |
|------|------|------|
| Id | INT PK | 노드 Id |
| BinData | BLOB | Consume KV vector 포함 |

---

## db_buff.db

### Buff
버프 효과 정의.

| 컬럼 | 타입 | 설명 |
|------|------|------|
| Id | DOUBLE | float64 타입! int 비교 불가 |
| BinData | BLOB | FlatBuffer |

**주의**: `WHERE Id = 123` 불가 → `WHERE CAST(Id AS INTEGER) = 123` 또는 float 값 사용

---

---

## db_phantom.db

에코(환상/Phantom) 관련 전체 데이터. 가장 복잡한 DB 중 하나.

### phantomtype
에코 종류 카테고리 (5행).

| 컬럼 | 타입 | 설명 |
|------|------|------|
| Id | INT | 1~5 |
| BinData | BLOB | **FlatBuffer 아님!** 단순 4-byte len + UTF-8 string |

```python
# 올바른 디코딩
slen = struct.unpack_from('<I', buf, 0)[0]
name_zh = buf[4:4+slen].decode('utf-8')
# 예: 1='畸形种', 2='畸幻种', 3='畸龙种', 4='探索型幻象', 5='战斗型幻象'
```

### phantomitem
에코 아이템 (735행). 등급별 아이템이 여러 행이므로 `MonsterId`로 그룹핑 필요.

| 컬럼 | 타입 | 설명 |
|------|------|------|
| ItemId | INT | 에코 아이템 ID (예: 60000382) |
| MonsterId | INT | 에코(몬스터) ID (예: 6000038) |
| ParentMonsterId | INT | 부모 ID (0이면 루트) |
| BinData | BLOB | FlatBuffer |

**BinData 필드 인덱스 (검증 완료)**:
| fi | 타입 | 의미 |
|----|------|------|
| f0 | i32 | ItemId |
| f1 | i32 | MonsterId (echo ID) |
| f3 | string | `MonsterInfo_{monster_id}_Name` TextMap key |
| f7 | i32 | **PhantomSkillId** (→ phantomskill.PhantomSkillId) |
| f10 | i32 | PhantomSkillId (f7과 동일, 보조) |
| f17 | string | icon path (`T_IconMonsterGoods_*`) |
| f21 | i32 | rarity/rank (2-5) |
| f32 | vec | resonance group ID 목록 (→ phantomfettergroup.Id) |

**에코 유효성 기준**: `COUNT(ItemId) >= 4` AND `MonsterId ∈ calabashdevelopreward.MonsterId`

### phantomskill
에코 스킬 데이터 (218행).

| 컬럼 | 타입 | 설명 |
|------|------|------|
| Id | INT | sequential |
| PhantomSkillId | INT | join key (phantomitem.f7과 일치) |
| BinData | BLOB | FlatBuffer |

**BinData 필드 인덱스 (검증 완료)**:
| fi | 타입 | 의미 |
|----|------|------|
| f0 | i32 | Id (sequential) |
| f1 | i32 | PhantomSkillId |
| f6 | i32 | base skill group ID |
| f7 | i32(float) | 쿨다운(초) — IEEE float로 재해석. 예: `0x41000000` = 8.0s |
| f8 | string | desc TextMap key (`PhantomSkill_{id}_DescriptionEx`) |
| f9 | string | simple_desc TextMap key (`PhantomSkill_{id}_SimplyDescription`) |
| f12 | rank param vec | skill.param 2D 배열 (→ `decode_rank_param_vec`) |
| f13 | string | skill icon path (`T_MstSkil_*`) |
| f14 | string | skill icon path (f13과 동일) |

### phantomfettergroup
에코 공명(세트) 그룹 (28행).

| 컬럼 | 타입 | 설명 |
|------|------|------|
| Id | INT | group Id |
| BinData | BLOB | FlatBuffer |

**BinData 필드 인덱스**:
| fi | 의미 |
|----|------|
| f0 | group Id (i32) |
| f3 | name TextMap key string (`PhantomFetter_{id}_Name`) |
| f7 | color hex string (예: `"FFFFFF00"`) |

### phantomfetter
에코 세트 효과 (53행). 각 group의 2pc/5pc 효과.

| 컬럼 | 타입 | 설명 |
|------|------|------|
| Id | INT | sequential |
| BinData | BLOB | FlatBuffer |

**주요 필드**:
- group_id (FlatBuffer i32) → phantomfettergroup.Id
- set_size: 2 또는 5
- desc TextMap key → `PhantomFetter_{group_id}_{set_size}_Desc`
- param: string vec (효과 수치)

---

## db_calabash.db

에코↔몬스터 연결 테이블.

### calabashdevelopreward

| 컬럼 | 타입 | 설명 |
|------|------|------|
| MonsterId | INT | echo ID (= phantomitem.MonsterId) |
| InteractAreaId | INT | |
| BinData | BLOB | FlatBuffer |

**BinData 필드 인덱스 (검증 완료)**:
| fi | 타입 | 의미 |
|----|------|------|
| f3 | i32 | ref_monster_id (→ monsterinfo.Id, 에코가 기반한 몬스터) |
| f5 | i32 | area_id (강도 결정에 사용) |
| f10 | string | echo code (예: `"H19-"`) |

---

## db_damage.db

에코 스킬 피해 행동 데이터.

### damage

| 컬럼 | 타입 | 설명 |
|------|------|------|
| Id | **DOUBLE** | 피해 행동 ID. `PhantomSkillId * 100 + N` 패턴 (N=1부터) |
| BinData | BLOB | FlatBuffer (root_off 큼, 복잡한 구조) |

**Id 쿼리 주의**: DOUBLE 타입이므로 `CAST(Id AS INTEGER)` 또는 float 비교 사용.

**BinData 필드 인덱스 (검증 완료)**:
| fi | 타입 | 의미 |
|----|------|------|
| f4 | i32 scalar | element (1~6) |
| f8 | i32 scalar | type |
| f13 | 1-elem vec | weakness_lvl |
| f14 | 1-elem vec | hardness_lv (예: 10000) |
| f15 | 1-elem vec | tough_lv (예: 11000) |
| f16 | 1-elem vec | energy (예: 260) |
| f17 | 1-elem vec | element_power |

**스칼라 vs 1-elem vec 판별**: fi=4,8은 직접 i32 스칼라. fi=13~17은 `[count=1, value]` 벡터.

---

## db_monster_Info.db

### monsterinfo

| 컬럼 | 타입 | 설명 |
|------|------|------|
| Id | INT | 몬스터 Id (예: 310000251) |
| BinData | BLOB | FlatBuffer |

**BinData 필드 인덱스 (검증 완료)**:
| fi | 타입 | 의미 |
|----|------|------|
| f1 | string | name TextMap key (`MonsterInfo_{id}_Name`) |
| f2 | i32 | rank (강도 수치) |
| f3 | string | icon path |
| f6 | 1-byte string | element (첫 번째 바이트가 element int) |
| f9 | string | UndiscoveredDes key (`MonsterInfo_{target_id}_UndiscoveredDes`) — 350xxx 몬스터의 원본 몬스터 역추적에 사용 |

---

## TextMap 이중 경로

도메인에 따라 TextMap 소스가 다르다:

| 도메인 | TextMap 경로 | 포맷 |
|--------|-------------|------|
| 무기/캐릭터 | `{lang}/lang_multi_text.db` | SQLite (`MultiText.Id`, `MultiText.Content`) |
| 에코/환상 | `data/configdb/TextMap/{lang}/MultiText.json` | JSON `{key: value}` |

**언어 폴더명**: `en`, `ko`, `zh-Hans`, `ja`

**에코 도메인 TextMap 키 패턴**:
| 키 패턴 | 의미 |
|---------|------|
| `PhantomHandBook_{echo_id}_TypeDescrtption` | 에코 종류 (예: "변이 동물") |
| `PhantomHandBook_{echo_id}_Intensity` | 강도 명칭 (예: "경파급") |
| `PhantomHandBook_{echo_id}_Place` | 서식지 (예: "황룡") |
| `PhantomHandBook_{echo_id}_Name` | 환상 전용 이름 |
| `PhantomSkill_{PhantomSkillId}_DescriptionEx` | 스킬 설명 (플레이스홀더 포함) |
| `PhantomSkill_{PhantomSkillId}_SimplyDescription` | 스킬 간단 설명 |
| `PhantomFetter_{group_id}_Name` | 세트 그룹 이름 |
| `MonsterInfo_{monster_id}_Name` | 몬스터/에코 이름 |

---

---

## db_item.db

범용 아이템 데이터 (재료, 소모품, 화폐 등).

### iteminfo
| 컬럼 | 타입 | 설명 |
|------|------|------|
| Id | INT PK | 아이템 Id |
| ItemType | INT | 아이템 타입 코드 |
| BinData | BLOB | FlatBuffer |

**BinData 필드 인덱스 (검증 완료)**:
| fi | 타입 | 의미 |
|----|------|------|
| f0 | i32 scalar | Id |
| f1 | i32 scalar | ItemType |
| f2 | string | name TextMap key (`ItemInfo_{Id}_Name`) |
| f3 | i32 scalar vec | tagnum 목록 (→ `ItemShowType_{n}_Name`) |
| f4 | string | attr desc TextMap key (`ItemInfo_{Id}_AttributesDescription`) |
| f5 | string | bg desc TextMap key (`ItemInfo_{Id}_BgDescription`) |
| f6 | string | icon path (IconA) |
| f7 | string | icon160 path |
| f8 | string | icon80 path |
| f9 | string | 3D mesh path |
| f10 | **i32 scalar** | QualityId/rarity (1-5) ← scanner가 string으로 오독할 수 있는 함정! |
| f16 | i32 scalar | max stack (999 등) |
| f21 | i32 scalar vec | AccessPath ID 목록 (→ `AccessPath_{id}_Description` = 획득 경로) |
| f24 | i32 scalar | is_show (1=공개) |
| f25 | string | ObtainedShowDescription TextMap key |

**텍스트맵**: `{lang}/lang_multi_text.db` (무기/캐릭터 도메인과 동일)

**주의**: f10 = QualityId는 scalar i32. 스캐너가 포인터로 오독해 garbled 문자열처럼 보일 수 있다.
  직접 `struct.unpack_from('<i', buf, abs_p)[0]`으로 읽어야 한다.

### itemshowtype
태그 이름 매핑 테이블 (60행).

| 컬럼 | 타입 | 설명 |
|------|------|------|
| Id | INT | tagnum 값 |
| BinData | BLOB | FlatBuffer |

**BinData 필드**: f1 = `ItemShowType_{Id}_Name` TextMap key

### typeinfo, qualityinfo, previewitem
- **typeinfo** (38행): 아이템 타입 설정 (필드 인덱스 미확인)
- **qualityinfo** (5행): 등급(rarity) 설정
- **previewitem** (229행): 특수 미리보기 아이템 (iteminfo와 Id 겹치지 않음)

**추출 대상**: `iteminfo` 1909행이 주 데이터. MotorDIY 스티커(89101xxx 등) 79개는 별도 DB에 있음.

---

## db_Term.db

게임 내 색상 텍스트 링크(하이퍼링크) 용어 설명 데이터.

### termconfig
hyperlink.json의 주 소스 (476행, Id 범위: 100001~851116).

| 컬럼 | 타입 | 설명 |
|------|------|------|
| Id | INT | 하이퍼링크 Id |
| Term | TEXT | zh 원문 이름 (직접 저장, TextMap key 아님) |
| BinData | BLOB | FlatBuffer |

**BinData 필드 인덱스 (검증 완료)**:
| fi | 타입 | 의미 |
|----|------|------|
| f0 | i32 scalar | Id |
| f1 | string | zh 이름 (직접 저장, 현지화는 TextMap 사용) |
| f2 | i32 scalar | type 코드 (주로 12, 일부 28/32/40/44/48/52/56/64/68 등) |
| f3 | string vec | param 목록 (없으면 비어있음; 일부 스킬 연관 항목은 ["40","8","1.5%"] 형태) |

**TextMap key 패턴** (에코 도메인 TextMap 사용):
- 이름: `Term{Id}_Title`
- 설명: `Term{Id}_Desc`

**TextMap 소스**: `data/configdb/TextMap/{lang}/MultiText.json` (에코 도메인과 동일)

### term
term 테이블 (185행, Id 범위: 800001~850173). termconfig와 유사한 구조.
현재 hyperlink.json은 termconfig 기반으로 생성.

---

## 공통 주의사항

1. **sequential Id vs domain Id**: weaponreson.Id ≠ weapon.ItemId; ResonId/BreachId가 실제 join key
2. **모델 경로**: weaponconf BinData가 아닌 db_model_config_preload.db에서 추출
3. **TextMap 언어 폴더**: zh → "zh-Hans" 폴더명 사용
4. **BinData 파싱 시작점**: buf[0:4] = root_off (u32 LE), 항상 이것부터
5. **is_percent 판별**: PropertyIndex.f9 타입 확인 필수 (string/int28/int32 세 가지 경우)
