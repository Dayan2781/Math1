#!/usr/bin/env bash
# Лекцийн LaTeX эх файлуудаас PDF үүсгэнэ.
#
#   ./latex/build.sh            # бүх лекц
#   ./latex/build.sh lec06      # нэг лекц (нэрийн эхлэлээр)
#
# PDF-үүд source/external/lectures/ хавтсанд гарна. `pretext build html`
# энэ хавтсыг вэб сайт руу хуулдаг тул сайтаас шууд татаж болно.
# GitHub Actions push бүр дээр үүнийг автоматаар ажиллуулна.
#
# Шинэ лекц нэмэх: файлаа latex/lectures/ дотор хийгээд доорх LECTURES
# жагсаалтад "дугаар|файлын нэр|гарчиг" мөр нэмнэ. Гарчиг нь файл
# \chapter{...}-ээр эхлэхгүй үед л хэрэглэгдэнэ.

set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
OUT="${OUT:-$HERE/../source/external/lectures}"
BUILD="$HERE/_build"

LECTURES=(
  "1|lec01-logic|"
  "2|lec02-sets-functions|"
  "3|lec03-numbers|Тоон олонлогууд"
  "4|lec04-basic-functions|Функцийн ойлголт, олон гишүүнт ба рационал функц"
  "5|lec05-trig-exp-log|Тригонометр, илтгэгч ба логарифм функц"
  "6|lec06-limit-1|"
  "7|lec07-limit-2|Дарааллын хязгаар"
  "8|lec08-continuity-derivative|"
  "9|lec09-derivative-2|"
  "10|lec10-derivative-3|"
  "11|lec11-mean-value-theorems|"
  "12|lec12-concavity-taylor|"
  "13|lec13-antiderivative|"
  "14|lec14-integration-techniques|"
  "15|lec15-definite-integral|"
  "16|lec16-improper-integral|"
  "0|seminars|"
  "0|homework|"
)

mkdir -p "$OUT" "$BUILD"
filter="${1:-}"
failed=()

for entry in "${LECTURES[@]}"; do
  IFS='|' read -r num name title <<<"$entry"
  [[ -n "$filter" && "$name" != "$filter"* ]] && continue

  src="$HERE/lectures/$name.tex"
  wrapper="$BUILD/$name.tex"
  {
    echo '\input{../preamble}'
    echo '\begin{document}'
    if [[ "$num" != 0 ]]; then
      echo "\\setcounter{chapter}{$((num - 1))}"
      # Файл \chapter-ээр эхлэхгүй бол гарчгийг нь энд нэмнэ
      if ! grep -v '^\s*%' "$src" | grep -m1 -E '\\(chapter|section)' | grep -q '\\chapter'; then
        echo "\\chapter{$title}"
      fi
    fi
    echo "\\input{../lectures/$name}"
    echo '\end{document}'
  } >"$wrapper"

  echo "==> $name"
  ok=1
  for _ in 1 2; do
    if ! (cd "$BUILD" && xelatex -interaction=nonstopmode -halt-on-error "$name.tex" >"$name.out" 2>&1); then
      ok=0
      break
    fi
  done
  if [[ $ok == 1 ]]; then
    cp "$BUILD/$name.pdf" "$OUT/$name.pdf"
  else
    echo "    АЛДАА: $BUILD/$name.log-г харна уу"
    grep -m5 -A3 '^!' "$BUILD/$name.log" || true
    failed+=("$name")
  fi
done

if ((${#failed[@]})); then
  echo "Амжилтгүй болсон: ${failed[*]}"
  exit 1
fi
echo "PDF-үүд: $OUT"
