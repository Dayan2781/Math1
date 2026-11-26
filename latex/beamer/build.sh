#!/usr/bin/env bash
# Бүх лекцийн слайд ба хэвлэх PDF-ийг локал компьютер дээр үүсгэнэ (xelatex хэрэгтэй).
#   ./build.sh            # 16 лекцийн слайд + 16 хэвлэх + бүтэн ном
#   ./build.sh 05         # зөвхөн 5-р лекц (слайд + хэвлэх)
# PDF-үүд pdf/ хавтсанд гарна.
set -uo pipefail
cd "$(dirname "$0")"
mkdir -p _build pdf
run() { # $1 үндсэн файл, $2 LECTURE, $3 гаралтын нэр
  for _ in 1 2; do
    xelatex -interaction=nonstopmode -halt-on-error -output-directory=_build \
      -jobname="$3" "\\def\\LECTURE{$2}\\input{$1}" >"_build/$3.stdout" 2>&1 || {
      echo "АЛДАА: $3 (_build/$3.log)"; grep -m3 -A4 '^!' "_build/$3.log"; return 1; }
  done
  cp "_build/$3.pdf" pdf/ && echo "OK  pdf/$3.pdf"
}
fail=0
lecs=("${1:-}"); [[ -z "${1:-}" ]] && lecs=(01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16)
for n in "${lecs[@]}"; do
  run slides "$n" "lec$n-slides" || fail=1
  run print "$n" "lec$n-print" || fail=1
done
[[ -z "${1:-}" ]] && { run print all math1-book || fail=1; }
exit $fail
