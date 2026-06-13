#!/usr/bin/env python3
"""
scan_record.py — ConfigDB BinData 필드 자동 스캐너

모든 non-zero 필드를 i32/f32/string 자동 판별로 출력한다.
FlatBuffer 구조를 역설계할 때 첫 번째로 실행하는 도구.

사용법:
    C:/Python313/python.exe scan_record.py --db db_weapon.db --table weaponconf --key ItemId --id 21050066
    C:/Python313/python.exe scan_record.py --db db_weapon.db --table weaponreson --key ResonId --id 21050066
    C:/Python313/python.exe scan_record.py --db db_property.db --table propertyindex --key Id --id 31
"""

import sys
import struct
import sqlite3
import argparse

sys.stdout.reconfigure(encoding='utf-8')


# ─── FlatBuffer 기초 파서 ──────────────────────────────────────────────────────

def parse_flatbuffer(buf: bytes):
    """BinData 버퍼에서 vtable 구조를 파싱, 모든 field 절대 위치 반환."""
    if len(buf) < 8:
        return None, 0
    root_off = struct.unpack_from('<I', buf, 0)[0]
    if root_off >= len(buf):
        return None, 0
    soffset = struct.unpack_from('<i', buf, root_off)[0]
    vtbl = root_off - soffset
    if vtbl < 0 or vtbl + 4 > len(buf):
        return None, 0
    vt_size = struct.unpack_from('<H', buf, vtbl)[0]
    n_fields = (vt_size - 4) // 2
    return vtbl, n_fields, root_off


def field_abs(buf, root_off, vtbl, fi, n_fields):
    """field index fi의 절대 위치 반환. 없으면 None."""
    if fi >= n_fields:
        return None
    fo = struct.unpack_from('<H', buf, vtbl + 4 + fi * 2)[0]
    if fo == 0:
        return None
    return root_off + fo


# ─── 타입 판별 ─────────────────────────────────────────────────────────────────

def try_string(buf, abs_p):
    """abs_p에서 string 시도. 성공 시 (True, str) 반환."""
    try:
        rel = struct.unpack_from('<i', buf, abs_p)[0]
        target = abs_p + rel
        if target < 0 or target + 4 > len(buf):
            return False, None
        slen = struct.unpack_from('<I', buf, target)[0]
        if 0 < slen < 4096 and target + 4 + slen <= len(buf):
            s = buf[target + 4: target + 4 + slen].decode('utf-8', errors='replace')
            # 인쇄 가능한 문자 비율 확인
            printable = sum(1 for c in s if c.isprintable() or c in '\n\r\t')
            if printable / max(len(s), 1) > 0.8:
                return True, s
    except Exception:
        pass
    return False, None


def try_nested_fb(buf, abs_p):
    """abs_p가 nested FlatBuffer object를 가리키는지 확인."""
    try:
        rel = struct.unpack_from('<i', buf, abs_p)[0]
        target = abs_p + rel
        if target < 0 or target + 4 > len(buf):
            return False
        inner_soffset = struct.unpack_from('<i', buf, target)[0]
        inner_vtbl = target - inner_soffset
        if inner_vtbl < 0 or inner_vtbl + 4 > len(buf):
            return False
        vt_size = struct.unpack_from('<H', buf, inner_vtbl)[0]
        if 4 <= vt_size <= 256 and vt_size % 2 == 0:
            return True
    except Exception:
        pass
    return False


def try_vec(buf, abs_p):
    """abs_p에서 vec(배열) 시도. 성공 시 (True, count, elem_type_hint) 반환."""
    try:
        rel = struct.unpack_from('<i', buf, abs_p)[0]
        target = abs_p + rel
        if target < 0 or target + 4 > len(buf):
            return False, 0, None
        count = struct.unpack_from('<I', buf, target)[0]
        if count == 0 or count > 10000:
            return False, 0, None
        # byte vec: 8바이트짜리 (primary stat용)
        if target + 4 + count <= len(buf) and count == 8:
            return True, count, 'byte_vec_8'
        # int/float vec
        if target + 4 + count * 4 <= len(buf):
            return True, count, 'int_vec'
        return False, 0, None
    except Exception:
        pass
    return False, 0, None


def describe_field(buf, abs_p, fi):
    """field를 자동 판별해 설명 문자열 반환."""
    buflen = len(buf)
    if abs_p + 4 > buflen:
        return "  <out of bounds>"

    lines = []

    # 1. i32 / f32 direct scalar
    i32_val = struct.unpack_from('<i', buf, abs_p)[0]
    f32_val = struct.unpack_from('<f', buf, abs_p)[0]

    # 2. string 시도
    ok, s = try_string(buf, abs_p)
    if ok:
        lines.append(f"  str='{s[:120]}'")

    # 3. nested FB 시도
    if try_nested_fb(buf, abs_p):
        lines.append("  nested_fb (relative offset)")

    # 4. vec 시도
    vec_ok, count, vhint = try_vec(buf, abs_p)
    if vec_ok:
        if vhint == 'byte_vec_8':
            rel = struct.unpack_from('<i', buf, abs_p)[0]
            target = abs_p + rel
            f32 = struct.unpack_from('<f', buf, target + 4)[0]
            u32 = struct.unpack_from('<I', buf, target + 8)[0]
            lines.append(f"  byte_vec(8) → f32={f32:.6f}, u32={u32}")
        else:
            lines.append(f"  vec(count={count})")

    # 5. scalar fallback
    if not lines:
        if i32_val != 0:
            lines.append(f"  i32={i32_val}")
        if abs(-214748364) > abs(i32_val) or True:
            if abs(f32_val) < 1e9 and f32_val != 0.0:
                lines.append(f"  f32={f32_val:.6f}")

    if not lines:
        lines.append(f"  i32={i32_val}  f32={f32_val:.6f}")

    return '\n'.join(lines)


# ─── 메인 스캐너 ──────────────────────────────────────────────────────────────

def scan_record(db_path, table, key_col, record_id):
    db = sqlite3.connect(db_path)

    # 레코드 조회
    try:
        row = db.execute(f"SELECT BinData FROM [{table}] WHERE [{key_col}] = ?", (record_id,)).fetchone()
    except Exception as e:
        print(f"[ERROR] SQL 실패: {e}")
        return

    if row is None:
        # float 타입(buff.Id 등) 재시도
        try:
            row = db.execute(f"SELECT BinData FROM [{table}] WHERE CAST([{key_col}] AS INTEGER) = ?", (int(record_id),)).fetchone()
        except Exception:
            pass

    if row is None:
        print(f"[ERROR] 레코드 없음: {table}.{key_col}={record_id}")
        return

    buf = row[0]
    if not buf:
        print("[ERROR] BinData가 비어 있음")
        return

    buf = bytes(buf)
    print(f"\n=== {table} / {key_col}={record_id} ===")
    print(f"BinData 길이: {len(buf)} bytes\n")

    result = parse_flatbuffer(buf)
    if result[0] is None:
        print("[ERROR] FlatBuffer 파싱 실패")
        return

    vtbl, n_fields, root_off = result
    print(f"root_off={root_off}, vtbl={vtbl}, n_fields={n_fields}\n")

    for fi in range(n_fields):
        abs_p = field_abs(buf, root_off, vtbl, fi, n_fields)
        if abs_p is None:
            continue  # field absent (fo=0)

        desc = describe_field(buf, abs_p, fi)
        print(f"f{fi}:  (abs={abs_p})")
        print(desc)

    db.close()


def list_rows(db_path, table, key_col, limit=20):
    """테이블 레코드 목록 출력 (첫 N개)."""
    db = sqlite3.connect(db_path)
    try:
        rows = db.execute(f"SELECT [{key_col}] FROM [{table}] LIMIT {limit}").fetchall()
        print(f"\n=== {table} 레코드 목록 (상위 {limit}개) ===")
        for r in rows:
            print(f"  {key_col}={r[0]}")
    except Exception as e:
        print(f"[ERROR] {e}")
    db.close()


def list_tables(db_path):
    """DB 내 테이블 목록 출력."""
    db = sqlite3.connect(db_path)
    tables = db.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    print(f"\n=== {db_path} 테이블 목록 ===")
    for t in tables:
        name = t[0]
        cols = [c[1] for c in db.execute(f"PRAGMA table_info({name})").fetchall()]
        cnt = db.execute(f"SELECT COUNT(*) FROM [{name}]").fetchone()[0]
        print(f"  {name} ({cnt} rows): {cols}")
    db.close()


# ─── CLI ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description='ConfigDB BinData 필드 자동 스캐너',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예시:
  # weaponconf 레코드 스캔
  python scan_record.py --db db_weapon.db --table weaponconf --key ItemId --id 21050066

  # DB 테이블 목록 보기
  python scan_record.py --db db_weapon.db --list-tables

  # 테이블 레코드 목록
  python scan_record.py --db db_weapon.db --table weaponreson --key ResonId --list-rows
        '''
    )
    parser.add_argument('--db', required=True, help='SQLite DB 경로')
    parser.add_argument('--table', help='테이블 이름')
    parser.add_argument('--key', default='Id', help='키 컬럼 이름 (기본: Id)')
    parser.add_argument('--id', type=int, help='조회할 레코드 ID')
    parser.add_argument('--list-tables', action='store_true', help='DB 내 테이블 목록 출력')
    parser.add_argument('--list-rows', action='store_true', help='테이블 레코드 목록 출력 (--table 필요)')

    args = parser.parse_args()

    if args.list_tables:
        list_tables(args.db)
    elif args.list_rows:
        if not args.table:
            parser.error('--list-rows는 --table 필요')
        list_rows(args.db, args.table, args.key)
    elif args.id is not None:
        if not args.table:
            parser.error('--id는 --table 필요')
        scan_record(args.db, args.table, args.key, args.id)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
