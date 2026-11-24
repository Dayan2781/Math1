#!/usr/bin/env python3
"""Гэрийн даалгаврын бодолтыг хугацаа болтол сайтаас хасах.

Энэ скрипт зөвхөн CI дээр (`.github/workflows/deploy.yml`), `pretext build html`-ээс
ӨМНӨ ажиллана. `homework-schedule.json`-д бичсэн гэрийн даалгавар бүрийн хувьд,
өгсөн өдрөөс `delay_days` хоног өнгөрөөгүй бол тухайн хэсгийн <solution>, <answer>
элементүүдийг эх файлаас (CI-ийн түр хуулбараас) устгаж, оронд нь "Бодолт ...-нд
нээгдэнэ" гэсэн мөр нэмнэ. Ингэснээр бодолт нь нийтлэгдсэн HTML-д огт ордоггүй.

Репозитор дахь эх файлууд өөрчлөгдөхгүй (CI зөвхөн түр хуулбар дээр ажилладаг).
Гараар туршихдаа:  python3 scripts/gate_homework_solutions.py --dry-run
Огноог дуурайх:     python3 scripts/gate_homework_solutions.py --dry-run --today 2026-12-01
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SCHEDULE = ROOT / "homework-schedule.json"
SOURCE = ROOT / "source"

SECTION_OPEN = re.compile(r"<section\b[^>]*>")
SECTION_ANY = re.compile(r"<section\b[^>]*>|</section>")
HIDDEN = re.compile(r"[ \t]*<(solution|answer)\b[^>]*>.*?</\1>[ \t]*\n?", re.S)


def find_section(text: str, xml_id: str) -> tuple[int, int] | None:
    """Return (start, end) of the <section> whose xml:id is xml_id."""
    for m in SECTION_OPEN.finditer(text):
        if f'xml:id="{xml_id}"' not in m.group(0):
            continue
        depth = 0
        for t in SECTION_ANY.finditer(text, m.start()):
            depth += -1 if t.group(0) == "</section>" else 1
            if depth == 0:
                return m.start(), t.end()
    return None


def mn_date(d: dt.date) -> str:
    return f"{d.year} оны {d.month}-р сарын {d.day}"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="файл бичихгүй, зөвхөн тайлагнана")
    ap.add_argument("--today", help="өнөөдрийн огноог дуурайх (YYYY-MM-DD)")
    args = ap.parse_args()

    cfg = json.loads(SCHEDULE.read_text(encoding="utf-8"))
    delay = dt.timedelta(days=int(cfg.get("delay_days", 14)))
    tz = dt.timezone(dt.timedelta(hours=float(cfg.get("timezone_offset_hours", 8))))
    today = dt.date.fromisoformat(args.today) if args.today else dt.datetime.now(tz).date()

    files = {p: p.read_text(encoding="utf-8") for p in SOURCE.rglob("*.ptx")}
    changed: set[pathlib.Path] = set()
    ok = True

    for hw in cfg["homework"]:
        sec_id = hw["section"]
        released = hw.get("released") or ""
        open_on = dt.date.fromisoformat(released) + delay if released else None
        is_open = open_on is not None and today >= open_on

        hits = [(p, r) for p, t in files.items() if (r := find_section(t, sec_id))]
        if not hits:
            print(f"АЛДАА: '{sec_id}' хэсэг олдсонгүй", file=sys.stderr)
            ok = False
            continue
        path, (a, b) = hits[0]
        if is_open:
            print(f"Лекц {hw['lecture']:>2}: нээлттэй ({open_on})  {sec_id}")
            continue

        body = files[path][a:b]
        new_body, n = HIDDEN.subn("", body)
        when = mn_date(open_on) + "-нд" if open_on else "дараа"
        note = (
            f"\n    <p><alert>Анхааруулга.</alert> Энэ гэрийн даалгаврын бодолт "
            f"{when} нээгдэнэ. Түүнээс өмнө өөрөө бодож үзээрэй; "
            f"заавар (hint) одоо ч харагдана.</p>"
        )
        if n:
            new_body = new_body.replace("</title>", "</title>" + note, 1)
            files[path] = files[path][:a] + new_body + files[path][b:]
            changed.add(path)
        print(f"Лекц {hw['lecture']:>2}: хаалттай (нээгдэх: {open_on or '—'}), {n} бодолт нуусан  {sec_id}")

    if not args.dry_run:
        for p in changed:
            p.write_text(files[p], encoding="utf-8")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
