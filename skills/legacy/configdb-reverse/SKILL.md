---
name: configdb-reverse
description: Wuthering Waves ConfigDB(SQLite + FlatBuffer BLOB) 역설계 전문 스킬. 새로운 테이블 구조 파악, BinData 필드 디코딩, 참조 JSON 재현용 추출 스크립트 작성 시 사용. FlatBuffer 이진 파싱, KV vector, nested object, TextMap lookup, 에코/몬스터/무기 도메인 검증 패턴을 즉시 적용한다.
---

# ConfigDB 역설계 스킬

## 목적

ConfigDB는 SQLite .db 파일들로 구성되며, 각 레코드의 실제 데이터는 FlatBuffer로 인코딩된 `BinData` BLOB 컬럼에 저장된다. 이 스킬은 새로운 테이블을 빠르게 파악하고, 참조 JSON과 1:1 대응하는 추출 스크립트를 작성하는 전문 절차를 제공한다.

---

## 도메인별 빠른 진입점

| 도메인 | 주요 DB | 핵심 패턴 |
|--------|---------|----------|
| **무기** | db_weapon.db | weaponconf → weaponreson/weaponbreach; f19 param 2D vec |
| **에코(환상)** | db_phantom.db + db_calabash.db + db_damage.db | phantomitem fi[7]→PhantomSkillId; damage ID = PhantomSkillId×100+N |
| **몬스터** | db_monster_Info.db | monsterinfo f1=name_key, f2=rank, f3=icon, f6=element(byte) |
| **캐릭터** | db_role.db | roleinfo(f43=weapon,f7=tag_ids vec,f4-f6=TextMap keys,f15/19/20=icon/bg), roletag(f2=name_key,f3=icon,f4=color,f5=desc_key) |
| **아이템** | db_item.db | iteminfo f3=tagnum scalar vec, f10=QualityId scalar(함정!), f21=source vec |
| **하이퍼링크** | db_Term.db | termconfig f1=zh 직접, f3=param vec; TextMap: `Term{Id}_Title`/`Term{Id}_Desc` |

---

## 역설계 워크플로우

### Step 1 — DB 탐색

```python
import sqlite3, sys
sys.stdout.reconfigure(encoding='utf-8')
db = sqlite3.connect("path/to/target.db")
for t in db.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall():
    cols = [c[1] for c in db.execute(f"PRAGMA table_info({t[0]})").fetchall()]
    cnt  = db.execute(f"SELECT COUNT(*) FROM {t[0]}").fetchone()[0]
    print(f"{t[0]} ({cnt}): {cols}")
```

### Step 2 — BinData 포맷 확인 (FlatBuffer vs 단순 blob)

**먼저 BinData가 FlatBuffer인지 확인한다.** 일부 테이블은 FlatBuffer가 아니다:

```python
buf = bytes(row['BinData'])
root_off = struct.unpack_from('<I', buf, 0)[0]

# FlatBuffer 여부 판별
if root_off >= len(buf) or root_off < 4:
    # 단순 length-prefixed UTF-8 string
    slen = struct.unpack_from('<I', buf, 0)[0]
    text = buf[4:4+slen].decode('utf-8')
else:
    # FlatBuffer 정상 처리
    ...
```

**알려진 non-FlatBuffer 테이블**: `phantomtype` (단순 문자열 blob)

### Step 3 — 레코드 전체 필드 스캔

`scripts/scan_record.py`를 실행해 모든 non-zero 필드를 i32/f32/string 자동 판별로 출력한다:

```bash
C:/Users/erifkim/my_projects/.venv/Scripts/python skills/configdb-reverse/scripts/scan_record.py \
    --db db_phantom.db --table phantomitem --key ItemId --id 60000382
```

출력 예:
```
f0:  i32=60000382
f1:  i32=6000038
f3:  str='MonsterInfo_310000251_Name'
f7:  i32=200045          ← PhantomSkillId
f17: str='/Game/Aki/UI/.../T_IconMonsterGoods_988_UI...'
f21: i32=2               ← rank
```

### Step 4 — 참조 JSON과 1:1 매핑

스캔 출력 값을 참조 JSON의 각 필드에 대응시켜 `fi → semantic` 매핑을 확정한다.
- 숫자값 → i32/f32 직접값 또는 TextMap lookup 결과
- 문자열 → string 필드 또는 TextMap key (예: `PhantomSkill_200045_DescriptionEx`)
- 배열 → vec / KV vector / nested rank-param vec

### Step 5 — decode 함수 작성

`references/decode_snippets.py`의 검증된 함수들을 복사해 사용한다.

주요 함수: `read_string`, `decode_kv_vector`, `decode_param`, `decode_primary_stat`,
`decode_secondary_stat`, `decode_1elem_vec`, `decode_rank_param_vec`, `read_lenpfx_blob`

### Step 6 — 전체 추출 후 diff 검증

```python
gen = json.load(open("out/ko/6000038.json", encoding="utf-8"))
ref = json.load(open("ref/ko/6000038.json",  encoding="utf-8"))
diffs = [(k, gen.get(k), ref.get(k)) for k in ref if gen.get(k) != ref.get(k)]
print(f"diffs: {len(diffs)}")  # 목표: 0
```

---

## FlatBuffer 파싱 규칙

### 구조 개요

```
buf[0:4]                 → root_off (u32 LE)
buf[root_off:root_off+4] → soffset  (i32 signed)
vtable_pos = root_off - soffset

vtable 레이아웃:
  [vt_size: u16][obj_size: u16][field_0: u16][field_1: u16]...
  n_fields = (vt_size - 4) // 2

field[i]:
  fo = u16 at (vtable_pos + 4 + i*2)   → 0이면 필드 없음
  abs_p = root_off + fo                → 실제 필드 위치

모든 참조 (string / vec / nested object):
  rel    = i32 at abs_p  (signed)
  target = abs_p + rel
```

### 타입 판별 순서 (abs_p에서)

1. `target`의 slen(u32) → `0 < slen < 4096` → **string**: `buf[target+4 : target+4+slen]`
2. slen이 8이고 내용이 binary → **byte vec** (f32+u32, primary stat에 사용)
3. target의 i32가 다시 vtable 구조를 가리킴 → **nested FlatBuffer object**
4. `target[0:4]` = count + count개의 상대 오프셋 목록 → **vec of objects** (KV vec 등)
5. **위 해당 없음 → abs_p 자체가 direct scalar** (i32 / f32)

> **스칼라 vs 포인터 판별 함정**: 동일한 abs_p를 `read_string()`으로 읽으면 우연히 유효한 문자열처럼 보일 수 있다. 도메인 지식(예: "이 필드는 energy=260이다")으로 스칼라 여부를 먼저 확정한 뒤 읽어야 한다. `decode_1elem_vec()`은 `[count=1, value]` 패턴을 올바르게 처리한다.

### 1-element vector 패턴 (damage 테이블 등)

일부 스칼라 값이 `[count=1, value]` 형태의 1-원소 벡터로 저장된다:

```python
# abs_p → rel → t: [count=1, val]
rel   = struct.unpack_from('<i', buf, abs_p)[0]
t     = abs_p + rel
count = struct.unpack_from('<I', buf, t)[0]   # == 1
val   = struct.unpack_from('<i', buf, t+4)[0] # 실제 값
```

→ `decode_1elem_vec(buf, abs_p)` 사용

### 핵심 파이썬 스니펫

```python
import struct

def vtable_info(buf, root_off):
    soffset  = struct.unpack_from('<i', buf, root_off)[0]
    vtbl     = root_off - soffset
    vt_size  = struct.unpack_from('<H', buf, vtbl)[0]
    n_fields = (vt_size - 4) // 2
    return vtbl, n_fields

def field_abs(buf, root_off, vtbl, fi):
    fo = struct.unpack_from('<H', buf, vtbl + 4 + fi * 2)[0]
    return None if fo == 0 else root_off + fo

def read_string(buf, abs_p):
    rel = struct.unpack_from('<i', buf, abs_p)[0]
    t   = abs_p + rel
    sl  = struct.unpack_from('<I', buf, t)[0]
    return buf[t+4 : t+4+sl].decode('utf-8', errors='replace') if 0 < sl < 4096 else None
```

전체 함수는 `references/decode_snippets.py` 참조.

---

## 주요 DB 파일 및 테이블

전체 구조는 `references/db_structure.md` 참조.

```
db_weapon.db          → weaponconf, weaponreson, weaponbreach, weaponskin
db_phantom.db         → phantomitem, phantomskill, phantomfetter, phantomfettergroup, phantomtype ...
db_calabash.db        → calabashdevelopreward (echo↔monster 연결, code, area_id)
db_damage.db          → damage (Id=DOUBLE!, PhantomSkillId×100+N)
db_monster_Info.db    → monsterinfo
db_property.db        → propertyindex, weaponpropertygrowth
db_model_config_preload.db → modelconfigpreload (3D 모델 경로)
db_role.db, db_skill.db, db_buff.db

db_item.db            → iteminfo (1909행), itemshowtype, typeinfo, qualityinfo, previewitem
db_Term.db            → termconfig (476행 = hyperlink), term

TextMap (2가지 방식):
  {lang}/lang_multi_text.db → MultiText(Id TEXT, Content TEXT)   [무기/캐릭터]
  data/configdb/TextMap/{lang}/MultiText.json → {key: value}     [에코/환상]
```

---

## 필드 인덱스 참조 (검증 완료)

### weaponconf

| fi  | 타입        | 의미 |
|-----|-------------|------|
| f0  | i32         | ItemId |
| f2  | string      | name TextMap key |
| f3  | i32         | rarity (1-5) |
| f4  | i32         | weapon type (1=대검 2=직검 3=권총 4=권갑 5=증폭기) |
| f10 | byte vec 8B | primary stat: float32 base + u32 PropertyIndex_id |
| f12 | nested FB   | secondary stat: f0=pid, f1=base(f32) |
| f14 | i32         | ResonId → weaponreson.ResonId |
| f18 | string      | effect TextMap key |
| f19 | nested vec  | param 2D string array |
| f22 | string      | lore/desc TextMap key |
| f23 | string      | icon path |

### phantomitem (db_phantom.db)

| fi  | 타입   | 의미 |
|-----|--------|------|
| f0  | i32    | ItemId |
| f1  | i32    | MonsterId (echo ID) |
| f3  | string | MonsterInfo_{monster_id}_Name TextMap key |
| f7  | i32    | **PhantomSkillId** → phantomskill.PhantomSkillId |
| f15 | string | PhantomItem_{base_id}_TypeDescription TextMap key |
| f17 | string | icon path (IconMonsterGoods) |
| f21 | i32    | rarity/rank (2-5) |
| f32 | vec    | group ID 목록 → phantomfettergroup.Id |

### phantomskill (db_phantom.db)

| fi  | 타입   | 의미 |
|-----|--------|------|
| f0  | i32    | Id (sequential) |
| f1  | i32    | PhantomSkillId (join key) |
| f6  | i32    | base skill group ID |
| f7  | i32(→float) | cooldown (IEEE float, 예: 0x41000000=8.0s) |
| f8  | string | desc TextMap key (`PhantomSkill_{id}_DescriptionEx`) |
| f9  | string | simple_desc TextMap key (`PhantomSkill_{id}_SimplyDescription`) |
| f12 | nested rank vec | skill.param: 5-rank × N strings (→ `decode_rank_param_vec`) |
| f13 | string | skill icon path |

### damage (db_damage.db)

**Id는 DOUBLE 타입.** 에코 스킬 damage ID = `PhantomSkillId * 100 + N` (N=01부터).

| fi  | 타입         | 의미 |
|-----|--------------|------|
| f4  | i32 scalar   | element (1=Fire 2=Ice 3=Electric 4=Aero 5=Spectro 6=Havoc) |
| f8  | i32 scalar   | type |
| f13 | 1-elem vec   | weakness_lvl |
| f14 | 1-elem vec   | hardness_lv |
| f15 | 1-elem vec   | tough_lv |
| f16 | 1-elem vec   | energy |
| f17 | 1-elem vec   | element_power |

### iteminfo (db_item.db)

| fi  | 타입          | 의미 |
|-----|---------------|------|
| f0  | i32 scalar    | Id |
| f1  | i32 scalar    | ItemType |
| f2  | string        | name TextMap key (`ItemInfo_{Id}_Name`) |
| f3  | i32 scalar vec| tagnum 목록 → `ItemShowType_{n}_Name` |
| f4  | string        | attr desc TextMap key (`ItemInfo_{Id}_AttributesDescription`) |
| f5  | string        | bg desc TextMap key (`ItemInfo_{Id}_BgDescription`) |
| f6  | string        | icon path (IconA) |
| f10 | **i32 scalar**| QualityId/rarity (1-5) ← 스캐너 오독 함정! |
| f21 | i32 scalar vec| AccessPath ID 목록 → `AccessPath_{id}_Description` (획득 경로) |
| f25 | string        | ObtainedShowDescription TextMap key |

> **f10 함정**: abs_p에서 rel로 이동 시 우연히 유효한 문자열처럼 보임. 반드시 scalar로 직접 읽을 것.

### roleinfo (db_role.db)

SQLite columns: `Id (INT PK), QualityId (INT), RoleType (INT), BinData (BLOB)`
플레이어블 캐릭터 = `RoleType=1`, 126개 행 중 51개.

| fi  | 타입           | 의미 |
|-----|----------------|------|
| f4  | string         | name TextMap key (`RoleInfo_{Id}_Name`) |
| f5  | string         | nick_name TextMap key (`RoleInfo_{Id}_NickName`) |
| f6  | string         | info/desc TextMap key (`FavorRoleInfo_{Id}_Info`) |
| f7  | vec of i32     | tag_ids → roletag.Id 목록 |
| f15 | string         | icon path (T_IconRoleHead256) |
| f19 | string         | background path (T_IconRole_Pile) |
| f20 | string         | background_stand path |
| f43 | i32 scalar     | weapon type (1=대검 2=직검 3=권총 4=권갑 5=증폭기) |
| f46 | string         | model/ABP path → 캐릭터 영문명 추출 |

`element = (Id // 100) % 10` (버전 배치 코드, 1=v1.1, 2=v1.2, …)

**TextMap 키 패턴** (`data/configdb/TextMap/{lang}/MultiText.json` JSON 파일):
- 이름/칭호: `RoleInfo_{Id}_Name`, `RoleInfo_{Id}_NickName`
- 설명/프로필: `FavorRoleInfo_{Id}_Info`, `FavorRoleInfo_{Id}_Birthday/Sex/Country/Influence/TalentName/TalentDoc/TalentCertification/CN/JP/KO/EN`
- 스토리: `FavorStory_{Id*100+n}_Title/Content`
- 대화: `FavorWord_{Id*100+n}_Title/Content`
- 호감 아이템: `FavorGoods_{Id*100+n}_Title/Content`

**캐릭터명 추출** (model_path f46): `/Game/Aki/Character/Role/{BodyType}/{CharName}/...`
- `live2d = CharName + "1"`, `audio = CharName.lower() + "1"`

### roletag (db_role.db)

| fi  | 타입   | 의미 |
|-----|--------|------|
| f2  | string | name TextMap key (`RoleTag{Id}`) |
| f3  | string | icon path |
| f4  | string | color hex (예: "ff4040") |
| f5  | string | desc TextMap key (`RoleTag{Id}_TagDesc`) |

### termconfig (db_Term.db)

| fi  | 타입       | 의미 |
|-----|------------|------|
| f0  | i32 scalar | Id |
| f1  | string     | zh 이름 **(TextMap key 아님, 원문 직접 저장)** |
| f2  | i32 scalar | type 코드 (주로 12) |
| f3  | string vec | param 목록 (없으면 빈 vec) |

TextMap key: `Term{Id}_Title` (이름), `Term{Id}_Desc` (설명) — echo 도메인 TextMap 사용.

### phantomfettergroup (db_phantom.db)

| fi  | 타입   | 의미 |
|-----|--------|------|
| f0  | i32    | group Id |
| f3  | string | name TextMap key (`PhantomFetter_{id}_Name`) |
| f7  | string | color hex (예: "FFFFFF00") |
| f8  | i32    | 아이콘 관련 offset |

---

## 알려진 함정 (반드시 확인)

| 상황 | 잘못된 접근 | 올바른 접근 |
|------|------------|------------|
| weaponreson 조회 | `WHERE Id = weapon_id` | `WHERE ResonId = weaponconf.f14` |
| 무기 모델 경로 | weaponconf에서 찾기 | `db_model_config_preload.db` BinData 바이트 스캔 |
| TextMap key 패턴 | `WeaponReson_{Id}_Name` | `WeaponReson_{ResonId}_Name` (ResonId 사용) |
| f19 param 디코딩 | outer vec → 바로 string 읽기 | outer vec → nested FB obj → f0 → string vec |
| KV vector 원소 | 직접 int 쌍 읽기 | FB sub-table (soffset → vtable → 2 fields) |
| is_percent 판별 | f7 값으로 판별 | f9: string → True; int 28 → False; int 32 → ratio |
| buff.Id 쿼리 | `WHERE Id = int` | DOUBLE 타입; `WHERE CAST(Id AS INTEGER) = n` |
| damage.Id 쿼리 | `WHERE Id = 20004501` | DOUBLE 타입; 동일하게 float 비교 or CAST |
| phantomtype BinData | FlatBuffer로 파싱 | 단순 4-byte len prefix + UTF-8 string blob |
| damage 스칼라 vs vec | read_i32로 읽기 | f14-f17은 1-elem vec → `decode_1elem_vec` |
| PhantomSkillId 찾기 | phantomskill.Id 조회 | phantomitem.f7 → PhantomSkillId join |
| skill.param 파싱 | outer vec → string 직접 | outer vec → rank FB obj → inner string vec |
| TextMap 위치 (에코) | lang_multi_text.db | `data/configdb/TextMap/{lang}/MultiText.json` |
| weaponbreach 없는 무기 | "데이터 없음" 처리 | 동일 재료 BreachId로 fallback (아래 참조) |
| PropertyGrowth | 무기별 별도 curve | CurveId=1(ATK)/2(secondary) 전체 공유 |
| iteminfo.f10 (QualityId) | string으로 읽기 | scalar i32 직접 읽기: `struct.unpack_from('<i', buf, abs_p)[0]` |
| iteminfo.f3/f21 | vec of objects | scalar int32 vec: `[count][i32_0][i32_1]...` (상대 오프셋 없음) |
| termconfig.f1 | TextMap key로 취급 | zh 원문 직접 저장; 현지화는 `Term{Id}_Title` 사용 |
| hyperlink TextMap | lang_multi_text.db | echo 도메인과 동일: `data/configdb/TextMap/{lang}/MultiText.json` |
| item source 필드 | ObtainedShowDescription | iteminfo.f21 = AccessPath ID vec → `AccessPath_{id}_Description` |
| roleinfo string 읽기 | `buf[abs_p+soffset:]` until null | FlatBuffer string = **4-byte length + chars**: `start = abs_p + soffset + 4` |
| roleinfo element 필드 | BinData 필드 탐색 | `element = (Id // 100) % 10` (버전 배치 코드, BinData에 별도 필드 없음) |
| roleinfo tag 찾기 | roletag 별도 join key | `f7` = vec of i32 tag IDs; roletag.Id로 바로 lookup |

### TextMap 이중 경로

에코/환상 도메인과 무기/캐릭터 도메인은 TextMap 소스가 다르다:

```python
# 무기/캐릭터: SQLite DB
db = sqlite3.connect("ko/lang_multi_text.db")
def loc(key): return db.execute("SELECT Content FROM MultiText WHERE Id=?", (key,)).fetchone()[0]

# 에코/환상: JSON 파일
import json
with open("data/configdb/TextMap/ko/MultiText.json", encoding='utf-8') as f:
    tm = json.load(f)
def loc(key): return tm.get(key, "")
```

### damage ID 패턴

```python
# PhantomSkillId → damage ID 목록 조회
skill_id = 200045
cur.execute("SELECT Id FROM damage WHERE Id >= ? AND Id < ? ORDER BY Id",
            (skill_id * 100, skill_id * 100 + 100))
damage_ids = [int(r[0]) for r in cur.fetchall()]
# 예: [20004501]
```

### weaponbreach 공유 패턴 (Breach Fallback)

일부 5성 무기는 `weaponbreach`에 자신의 `BreachId` 항목이 없다. 동일 재료 구성 무기의 BreachId로 fallback.

```python
BREACH_FALLBACK = {
    21010045: 21010066,
    21020045: 21020076,
    21030045: 21030046,
    21040045: 21040056,
    21050045: 21021140,
}
breach_id = BREACH_FALLBACK.get(item_id, item_id)
```

> **새 버전 업데이트 시**: `SELECT DISTINCT BreachId FROM weaponbreach`와 `weaponconf.ItemId` 비교로 누락 무기 재확인.

---

## 빠른 참조

- **FlatBuffer 전체 디코더 함수**: `references/decode_snippets.py`
- **DB 파일 및 테이블 상세**: `references/db_structure.md`
- **CLI 스캐너**: `scripts/scan_record.py --db <db> --table <t> --key <k> --id <id>`
