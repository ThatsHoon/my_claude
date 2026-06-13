"""
decode_snippets.py
ConfigDB FlatBuffer BinData 디코딩 검증 완료 함수 모음.

모든 함수는 Wuthering Waves ConfigDB 역설계 세션에서 실제 검증됨.
사용법: 이 파일을 읽어서 필요한 함수를 추출 스크립트에 복사한다.
"""

import struct


# ─── FlatBuffer 기본 파서 ─────────────────────────────────────────────────────

def fb_vtable(buf, root_off):
    """vtable_pos, n_fields 반환."""
    soffset  = struct.unpack_from('<i', buf, root_off)[0]
    vtbl     = root_off - soffset
    vt_size  = struct.unpack_from('<H', buf, vtbl)[0]
    n_fields = (vt_size - 4) // 2
    return vtbl, n_fields


def fb_field_abs(buf, root_off, vtbl, fi):
    """field fi의 절대 위치 반환. 없으면 None."""
    fo = struct.unpack_from('<H', buf, vtbl + 4 + fi * 2)[0]
    return None if fo == 0 else root_off + fo


def fb_root(buf):
    """(root_off, vtbl, n_fields) 한번에 반환."""
    root_off = struct.unpack_from('<I', buf, 0)[0]
    vtbl, n  = fb_vtable(buf, root_off)
    return root_off, vtbl, n


# ─── 스칼라 읽기 ──────────────────────────────────────────────────────────────

def read_int32(buf, abs_p):
    return struct.unpack_from('<i', buf, abs_p)[0]

def read_uint32(buf, abs_p):
    return struct.unpack_from('<I', buf, abs_p)[0]

def read_float32(buf, abs_p):
    return struct.unpack_from('<f', buf, abs_p)[0]


# ─── String ───────────────────────────────────────────────────────────────────

def read_string(buf, abs_p, max_len=4096):
    """
    abs_p: relative-ref 위치 (i32 offset 저장됨).
    반환: str 또는 None.
    """
    rel    = struct.unpack_from('<i', buf, abs_p)[0]
    target = abs_p + rel
    buflen = len(buf)
    if target < 0 or target + 4 > buflen:
        return None
    slen = struct.unpack_from('<I', buf, target)[0]
    if not (0 < slen < max_len):
        return None
    return buf[target + 4 : target + 4 + slen].decode('utf-8', errors='replace')


# ─── Byte Vector (primary stat 등) ────────────────────────────────────────────

def decode_byte_vec(buf, abs_p):
    """
    abs_p: relative-ref 위치.
    반환: (bytes_data, count) 또는 (None, 0).

    weaponconf f10 예시: count=8, data = float32(base) + uint32(PropertyIndex_id)
    사용법:
        data, count = decode_byte_vec(buf, abs_p)
        if count >= 8:
            base = struct.unpack_from('<f', data, 0)[0]
            pid  = struct.unpack_from('<I', data, 4)[0]
    """
    rel    = struct.unpack_from('<i', buf, abs_p)[0]
    target = abs_p + rel
    buflen = len(buf)
    if target + 4 > buflen:
        return None, 0
    count = struct.unpack_from('<I', buf, target)[0]
    if count == 0 or count > 65536:
        return None, 0
    return buf[target + 4 : target + 4 + count], count


def decode_primary_stat(buf, abs_p):
    """weaponconf f10 → (float32 base, uint32 PropertyIndex_id)."""
    data, count = decode_byte_vec(buf, abs_p)
    if data is None or count < 8:
        return None, None
    base = struct.unpack_from('<f', data, 0)[0]
    pid  = struct.unpack_from('<I', data, 4)[0]
    return base, pid


# ─── Nested FlatBuffer Object ─────────────────────────────────────────────────

def decode_nested_fb(buf, abs_p):
    """
    abs_p: relative-ref 위치 → nested FB object 디코딩.
    반환: {fi: raw_i32} dict (caller가 추가 해석).
    """
    rel     = struct.unpack_from('<i', buf, abs_p)[0]
    sub_pos = abs_p + rel
    buflen  = len(buf)
    if sub_pos + 4 > buflen:
        return {}
    sub_soff = struct.unpack_from('<i', buf, sub_pos)[0]
    sub_vtbl = sub_pos - sub_soff
    if sub_vtbl < 0 or sub_vtbl + 4 > buflen:
        return {}
    sub_vt_size = struct.unpack_from('<H', buf, sub_vtbl)[0]
    n = (sub_vt_size - 4) // 2
    fields = {}
    for fi in range(n):
        fo = struct.unpack_from('<H', buf, sub_vtbl + 4 + fi * 2)[0]
        if fo == 0:
            continue
        fp = sub_pos + fo
        if fp + 4 > buflen:
            continue
        fields[fi] = struct.unpack_from('<i', buf, fp)[0]
    return fields


def decode_secondary_stat(buf, abs_p):
    """
    weaponconf f12 → (PropertyIndex_id, float32 base).
    nested FB sub-table: f0=pid(i32), f1=base(f32 재해석).
    """
    rel     = struct.unpack_from('<i', buf, abs_p)[0]
    sub_pos = abs_p + rel
    buflen  = len(buf)
    if sub_pos + 4 > buflen:
        return None, None
    sub_soff = struct.unpack_from('<i', buf, sub_pos)[0]
    sub_vtbl = sub_pos - sub_soff
    if sub_vtbl < 0 or sub_vtbl + 4 > buflen:
        return None, None
    vt_size = struct.unpack_from('<H', buf, sub_vtbl)[0]
    n = (vt_size - 4) // 2
    pid  = None
    base = None
    for fi in range(n):
        fo = struct.unpack_from('<H', buf, sub_vtbl + 4 + fi * 2)[0]
        if fo == 0:
            continue
        fp = sub_pos + fo
        if fp + 4 > buflen:
            continue
        if fi == 0:
            pid  = struct.unpack_from('<i', buf, fp)[0]
        elif fi == 1:
            base = struct.unpack_from('<f', buf, fp)[0]
    return pid, base


# ─── KV Vector ────────────────────────────────────────────────────────────────

def decode_kv_vector(buf, abs_p):
    """
    KV vector (weaponbreach.f5 BreachConsume, skillTree.Consume 등).
    반환: [{'key': int, 'value': int}, ...] 또는 [].

    구조:
      abs_p → relative offset → vec_pos
      vec_pos[0:4] = count
      vec_pos+4+i*4 = 상대 오프셋 → FB sub-table {Key, Value}
    """
    buflen = len(buf)
    if abs_p + 4 > buflen:
        return []
    raw = struct.unpack_from('<I', buf, abs_p)[0]
    if not (0 < raw < buflen):
        return []
    vp = abs_p + raw
    if vp + 4 > buflen:
        return []
    count = struct.unpack_from('<I', buf, vp)[0]
    if not (0 < count <= 100):
        return []

    result = []
    for i in range(count):
        ep = vp + 4 + i * 4
        if ep + 4 > buflen:
            break
        elem_off = struct.unpack_from('<I', buf, ep)[0]
        if elem_off == 0:
            result.append({'key': 0, 'value': 0})
            continue
        tbl_pos = ep + elem_off
        if tbl_pos + 4 > buflen:
            continue
        soff    = struct.unpack_from('<i', buf, tbl_pos)[0]
        vt_pos  = tbl_pos - soff
        if vt_pos < 0 or vt_pos + 4 > buflen:
            continue
        vt_size = struct.unpack_from('<H', buf, vt_pos)[0]
        n       = (vt_size - 4) // 2
        fields  = {}
        for fi in range(n):
            fop = vt_pos + 4 + fi * 2
            fo  = struct.unpack_from('<H', buf, fop)[0]
            if fo == 0:
                continue
            fp = tbl_pos + fo
            if fp + 4 > buflen:
                continue
            fields[fi] = struct.unpack_from('<i', buf, fp)[0]
        fkeys = sorted(fields.keys())
        if len(fkeys) >= 2:
            result.append({'key': fields[fkeys[-2]], 'value': fields[fkeys[-1]]})
        elif len(fkeys) == 1:
            result.append({'key': fields[fkeys[0]], 'value': 0})

    return result


# ─── Param (2D string array, weaponconf f19) ───────────────────────────────────

def _decode_string_vec(buf, target, buflen):
    """string vec: count + count개의 relative offset → string list."""
    count = struct.unpack_from('<I', buf, target)[0]
    if count == 0 or count > 50:
        return None
    strings = []
    for j in range(count):
        ref_pos = target + 4 + j * 4
        if ref_pos + 4 > buflen:
            return None
        ref     = struct.unpack_from('<i', buf, ref_pos)[0]
        str_pos = ref_pos + ref
        if str_pos < 0 or str_pos + 4 > buflen:
            return None
        slen = struct.unpack_from('<I', buf, str_pos)[0]
        if slen > 200:
            return None
        strings.append(
            buf[str_pos + 4 : str_pos + 4 + slen].decode('utf-8', errors='replace')
        )
    return strings


def _find_string_vec_in_nested(buf, obj_pos, buflen):
    """nested FB object 안에서 첫 번째 string vec 필드를 찾아 반환."""
    if obj_pos + 4 > buflen:
        return None
    soffset = struct.unpack_from('<i', buf, obj_pos)[0]
    vtbl    = obj_pos - soffset
    if vtbl < 0 or vtbl + 4 > buflen:
        return None
    vt_size = struct.unpack_from('<H', buf, vtbl)[0]
    n_f     = (vt_size - 4) // 2
    for fi in range(n_f):
        fo = struct.unpack_from('<H', buf, vtbl + 4 + fi * 2)[0]
        if fo == 0:
            continue
        abs_p = obj_pos + fo
        if abs_p + 4 > buflen:
            continue
        val    = struct.unpack_from('<i', buf, abs_p)[0]
        target = abs_p + val
        if target < 0 or target + 4 > buflen:
            continue
        sv = _decode_string_vec(buf, target, buflen)
        if sv:
            return sv
    return None


def decode_param(buf, abs_p):
    """
    weaponconf f19 → 2D string array (param).
    구조: abs_p → outer vec → nested FB objects → string vecs

    반환: [['12%','15%',...], ['12','12',...], ...]
    """
    buflen = len(buf)
    val    = struct.unpack_from('<i', buf, abs_p)[0]
    outer  = abs_p + val
    if outer + 4 > buflen:
        return []
    count = struct.unpack_from('<I', buf, outer)[0]
    if count == 0 or count > 20:
        return []
    param = []
    for j in range(count):
        ref_pos     = outer + 4 + j * 4
        if ref_pos + 4 > buflen:
            break
        ref         = struct.unpack_from('<i', buf, ref_pos)[0]
        inner_pos   = ref_pos + ref
        strs        = _find_string_vec_in_nested(buf, inner_pos, buflen)
        if strs:
            param.append(strs)
    return param


# ─── Int / Float Vector ───────────────────────────────────────────────────────

def decode_int_vec(buf, abs_p, signed=True):
    """일반 int32 벡터. weaponreson f4 등."""
    buflen = len(buf)
    if abs_p + 4 > buflen:
        return []
    raw = struct.unpack_from('<I', buf, abs_p)[0]
    if raw == 0:
        return []
    vp = abs_p + raw
    if vp + 4 > buflen:
        return []
    count = struct.unpack_from('<I', buf, vp)[0]
    if count == 0 or count > 200:
        return []
    fmt   = '<i' if signed else '<I'
    items = []
    for i in range(count):
        ep = vp + 4 + i * 4
        if ep + 4 > buflen:
            break
        items.append(struct.unpack_from(fmt, buf, ep)[0])
    return items


def decode_float64_vec(buf, abs_p):
    """
    float64(double) 벡터. buff 테이블의 id vec 등에 사용.
    주의: buff.Id 컬럼 자체는 DOUBLE 타입 SQLite 컬럼.
    """
    buflen = len(buf)
    if abs_p + 4 > buflen:
        return []
    raw = struct.unpack_from('<I', buf, abs_p)[0]
    if raw == 0:
        return []
    vp = abs_p + raw
    if vp + 4 > buflen:
        return []
    count = struct.unpack_from('<I', buf, vp)[0]
    if count == 0 or count > 200:
        return []
    items = []
    for i in range(count):
        ep = vp + 4 + i * 8
        if ep + 8 > buflen:
            break
        items.append(struct.unpack_from('<d', buf, ep)[0])
    return items


# ─── TextMap ──────────────────────────────────────────────────────────────────

def make_textmap_lookup(lang_folder, configdb_dir):
    """
    TextMap SQLite lookup 함수 반환.
    사용법: loc = make_textmap_lookup('ko', CONFIGDB_DIR)
            loc('WeaponConf_21050066_WeaponName')  → '잊혀진 피안의 슬픈 악장'
    """
    import sqlite3
    from pathlib import Path
    db = sqlite3.connect(str(Path(configdb_dir) / lang_folder / "lang_multi_text.db"))
    def loc(key):
        if not key:
            return ""
        r = db.execute("SELECT Content FROM MultiText WHERE Id=?", (key,)).fetchone()
        return r[0] if r else ""
    return loc


# ─── 모델 경로 (db_model_config_preload.db) ───────────────────────────────────

def get_weapon_model(item_id, configdb_dir):
    """
    db_model_config_preload.db → BinData 바이트 스캔으로 /Model/ 경로 반환.
    weaponconf f26이 아닌 이 함수를 사용해야 올바른 3D 모델 경로를 얻는다.
    """
    import sqlite3
    from pathlib import Path
    db  = sqlite3.connect(str(Path(configdb_dir) / "db_model_config_preload.db"))
    row = db.execute(
        "SELECT BinData FROM modelconfigpreload WHERE Id=?", (item_id,)
    ).fetchone()
    if not row:
        return None
    buf    = bytes(row[0])
    buflen = len(buf)
    pos = 0
    while pos < buflen - 4:
        try:
            slen = struct.unpack_from('<I', buf, pos)[0]
            if 4 < slen < 300:
                s = buf[pos + 4 : pos + 4 + slen].decode('utf-8')
                if s.startswith('/Game/') and '/Model/' in s:
                    return s
        except Exception:
            pass
        pos += 1
    return None


# ─── Non-FlatBuffer Blob (phantomtype 등) ─────────────────────────────────────

def read_lenpfx_blob(buf):
    """
    단순 4-byte 길이 접두사 + UTF-8 문자열 blob 디코딩.
    FlatBuffer가 아닌 테이블(예: phantomtype)에 사용.

    판별 방법:
      root_off = struct.unpack_from('<I', buf, 0)[0]
      if root_off >= len(buf):  # FlatBuffer가 아님
          return read_lenpfx_blob(buf)
    """
    if len(buf) < 4:
        return ""
    slen = struct.unpack_from('<I', buf, 0)[0]
    if slen == 0 or 4 + slen > len(buf):
        return ""
    return buf[4:4 + slen].decode('utf-8', errors='replace')


# ─── 1-element Vector (damage 테이블 등) ──────────────────────────────────────

def decode_1elem_vec(buf, abs_p, signed=True):
    """
    일부 스칼라 필드가 [count=1, value] 1-원소 벡터로 저장되는 패턴.
    db_damage.db의 energy, hardness_lv, tough_lv, element_power, weakness_lvl 등.

    반환: int 값 또는 None.

    예:
        energy    = decode_1elem_vec(buf, field_abs(buf, root_off, vtbl, 16))
        hardness  = decode_1elem_vec(buf, field_abs(buf, root_off, vtbl, 14))
        tough     = decode_1elem_vec(buf, field_abs(buf, root_off, vtbl, 15))
    """
    buflen = len(buf)
    if abs_p is None or abs_p + 4 > buflen:
        return None
    rel = struct.unpack_from('<i', buf, abs_p)[0]
    t   = abs_p + rel
    if t < 0 or t + 8 > buflen:
        return None
    count = struct.unpack_from('<I', buf, t)[0]
    if count != 1:
        return None
    fmt = '<i' if signed else '<I'
    return struct.unpack_from(fmt, buf, t + 4)[0]


# ─── Rank-Param Vec (phantomskill f12) ────────────────────────────────────────

def decode_rank_param_vec(buf, abs_p):
    """
    에코 스킬 param 2D 배열 디코딩 (phantomskill fi=12).
    구조: abs_p → outer vec(5 rank entries) → each rank = nested FB obj
          rank obj fi=0 → inner string vec (각 rank의 param 문자열들)

    반환: [['30.00%+60', '8'], ['34.50%+69', '8'], ...] (5 ranks)

    사용 예:
        root_off, vtbl, _ = fb_root(buf)
        abs12 = fb_field_abs(buf, root_off, vtbl, 12)
        params = decode_rank_param_vec(buf, abs12)
    """
    buflen = len(buf)
    if abs_p is None or abs_p + 4 > buflen:
        return []

    rel   = struct.unpack_from('<i', buf, abs_p)[0]
    outer = abs_p + rel
    if outer < 0 or outer + 4 > buflen:
        return []

    count = struct.unpack_from('<I', buf, outer)[0]
    if count == 0 or count > 20:
        return []

    result = []
    for j in range(count):
        ep = outer + 4 + j * 4
        if ep + 4 > buflen:
            break
        rank_rel  = struct.unpack_from('<i', buf, ep)[0]
        rank_root = ep + rank_rel
        if rank_root < 0 or rank_root + 4 > buflen:
            result.append([])
            continue

        # rank_root = nested FB object; fi=0 = string vec
        rank_soff = struct.unpack_from('<i', buf, rank_root)[0]
        rank_vtbl = rank_root - rank_soff
        if rank_vtbl < 0 or rank_vtbl + 6 > buflen:
            result.append([])
            continue

        rank_fo = struct.unpack_from('<H', buf, rank_vtbl + 4)[0]  # fi=0
        if rank_fo == 0:
            result.append([])
            continue

        sv_ap  = rank_root + rank_fo
        sv_rel = struct.unpack_from('<i', buf, sv_ap)[0]
        sv_t   = sv_ap + sv_rel
        if sv_t < 0 or sv_t + 4 > buflen:
            result.append([])
            continue

        sv_count = struct.unpack_from('<I', buf, sv_t)[0]
        strs = []
        for k in range(min(sv_count, 50)):
            spos = sv_t + 4 + k * 4
            if spos + 4 > buflen:
                break
            srel  = struct.unpack_from('<i', buf, spos)[0]
            st    = spos + srel
            if st < 0 or st + 4 > buflen:
                break
            slen  = struct.unpack_from('<I', buf, st)[0]
            if slen == 0 or st + 4 + slen > buflen:
                strs.append("")
            else:
                strs.append(buf[st + 4:st + 4 + slen].decode('utf-8', errors='replace'))
        result.append(strs)

    return result


# ─── PropertyIndex 유틸 ───────────────────────────────────────────────────────

def get_property_info(pid, lang_folder, configdb_dir):
    """
    PropertyIndex.Id → (name_str, is_percent).
    is_percent 판별:
      f9 = string starting with "PropertyIndex_" → True
      f9 = int 28 → False (raw unit)
      f9 = int 32 → False (ratio, ×100 for display)
    """
    import sqlite3
    from pathlib import Path
    db_p = sqlite3.connect(str(Path(configdb_dir) / "db_property.db"))
    loc  = make_textmap_lookup(lang_folder, configdb_dir)

    row = db_p.execute("SELECT BinData FROM propertyindex WHERE Id=?", (pid,)).fetchone()
    if not row:
        return "", False

    buf    = bytes(row[0])
    buflen = len(buf)
    root_off, vtbl, n_fields = fb_root(buf)

    name_key   = None
    is_percent = False

    for fi in range(n_fields):
        abs_p = fb_field_abs(buf, root_off, vtbl, fi)
        if abs_p is None:
            continue
        if fi == 2:
            name_key = read_string(buf, abs_p)
        elif fi == 9:
            # f9가 string이면 is_percent=True
            s9 = read_string(buf, abs_p)
            if s9 and s9.startswith("PropertyIndex_"):
                is_percent = True

    return loc(name_key), is_percent
