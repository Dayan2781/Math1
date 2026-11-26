#!/usr/bin/env python3
"""latex/lectures/lecNN-*.tex файлуудыг beamer frame бүтэцтэй болгож
latex/beamer/lectures/lecNN.tex болгон хөрвүүлнэ.

Гарсан файл нэг эх сурвалжаас хоёр хувилбар өгнө:
  * slides.tex  (beamer)             -> хичээл дээр үзүүлэх слайд
  * print.tex   (book + beamerarticle) -> хэвлэх хувилбар

Энэ скриптийг зөвхөн анхны хөрвүүлэлтэд ашигласан. Цаашид
latex/beamer/lectures/ доторх файлуудыг шууд засна. Дахин ажиллуулбал
тэдгээр засвар дарагдана:

    python3 scripts/latex_to_beamer.py
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "latex" / "lectures"
DST = ROOT / "latex" / "beamer" / "lectures"

# Файл \chapter-ээр эхлэхгүй лекцүүдийн гарчиг (latex/build.sh-ээс)
FALLBACK_TITLES = {
    3: "Тоон олонлогууд",
    4: "Функцийн ойлголт, олон гишүүнт ба рационал функц",
    5: "Тригонометр, илтгэгч ба логарифм функц",
    7: "Дарааллын хязгаар",
}

# Шинэ frame эхлүүлэх теорем маягийн орчнууд
THM_ENVS = {
    "definition", "theorem", "proposition", "lemma", "example", "remark",
    "note", "cor", "problem",
}
# Эх файлын жижиг алдааны засвар: {лекц: [(хуучин, шинэ), ...]}
FIXES = {
    1: [  # tabular нүдэнд $...$ дутуу байсан (display math дотор tabular)
        (r"""$$\begin{tabular}{|c|c|c|c|c|c|}
\hline
A&B&$\lnot$ A&A\lor B&A\land B&$A\Rightarrow B$\\""",
         r"""\begin{center}\begin{tabular}{|c|c|c|c|c|c|}
\hline
$A$&$B$&$\lnot A$&$A\lor B$&$A\land B$&$A\Rightarrow B$\\"""),
        ("0&0&1&0&0&1\\\\\n\\hline\n\\end{tabular}$$",
         "0&0&1&0&0&1\\\\\n\\hline\n\\end{tabular}\\end{center}"),
    ],
    2: [  # сурьектив/иньектив солигдсон байсан
        (r"ёсоор } f(x)=\cos x \text{ иньектив}$$", r"ёсоор } f(x)=\cos x \text{ сурьектив}$$"),
        (r"g(x)=\sin x \text{ иньектив биш байна.}$$", r"g(x)=\sin x \text{ сурьектив биш байна.}$$"),
        (r"\neq 0$ тул $f(x)=\cos x$ сурьектив байна.", r"\neq 0$ тул $f(x)=\cos x$ иньектив байна."),
        (r"учир $g(x)=\sin x$ сурьектив биш байна.", r"учир $g(x)=\sin x$ иньектив биш байна."),
    ],
    11: [
        (r"\subsection{[Шүргэгч", r"\subsection{Шүргэгч"),  # илүү "[" тэмдэгт
        # слайдын өргөнд багтахгүй нэг мөр томьёог хоёр мөр болгов
        ("(\\text{тэгээс их тул шийд болно}),\\qquad\n",
         "(\\text{тэгээс их тул шийд болно}),\\]\n\\[\n"),
    ],
}

HEADING_RE = re.compile(r"^\s*\\(chapter|section|subsection|subsubsection)(\*?)\s*(\[[^\]]*\])?\s*\{")
BEGIN_RE = re.compile(r"\\begin\{([A-Za-z*]+)\}")
END_RE = re.compile(r"\\end\{([A-Za-z*]+)\}")


def strip_comment(line: str) -> str:
    out = []
    i = 0
    while i < len(line):
        c = line[i]
        if c == "\\" and i + 1 < len(line):
            out.append(line[i:i + 2])
            i += 2
            continue
        if c == "%":
            break
        out.append(c)
        i += 1
    return "".join(out)


def brace_arg(text: str, start: int):
    """text[start] == '{' байх үед тохирох '}' хүртэлх агуулга ба төгсгөлийг буцаана."""
    depth = 0
    for i in range(start, len(text)):
        if text[i] == "\\":
            continue
        if text[i] == "{" and (i == 0 or text[i - 1] != "\\"):
            depth += 1
        elif text[i] == "}" and text[i - 1] != "\\":
            depth -= 1
            if depth == 0:
                return text[start + 1:i], i + 1
    raise ValueError("тохирох хаалт олдсонгүй: " + text[start:start + 60])


def fix_graphics(line: str) -> str:
    # pictures/ угтварыг авч, слайдад багтахаар хамгийн их хэмжээ тавина
    line = re.sub(r"\{pictures/", "{", line)

    def repl(m):
        opts = m.group(1)
        extra = r"max width=\linewidth,max height=.72\textheight"
        opts = f"[{opts[1:-1]},{extra}]" if opts else f"[{extra}]"
        return r"\includegraphics" + opts
    return re.sub(r"\\includegraphics(\[[^\]]*\])?", repl, line)


def convert(num: int, path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    for old, new in FIXES.get(num, []):
        if old not in text:
            sys.exit(f"{path.name}: засвар олдсонгүй: {old[:50]}")
        text = text.replace(old, new)
    # Зураг, хүснэгтийг слайдад багтахаар (шаардлагатай үед л) жижигрүүлнэ
    text = re.sub(r"(\\begin\{(tikzpicture|tabular)\}.*?\\end\{\2\})",
                  r"\\begin{fitbox}\1\\end{fitbox}", text, flags=re.S)
    lines = text.splitlines()
    title = FALLBACK_TITLES.get(num, "")
    body = []  # (kind, payload): kind in {"line", "heading", "thm"}
    depth = 0
    for raw in lines:
        code = strip_comment(raw)
        if depth == 0 and not code.strip() and raw.strip().startswith("%"):
            continue  # зөвхөн тайлбар мөр
        if re.match(r"^\s*\\(newpage|clearpage)\s*$", code):
            continue
        if depth == 0:
            m = HEADING_RE.match(code)
            if m:
                arg, end = brace_arg(code, m.end() - 1)
                rest = code[end:].strip()
                if m.group(1) == "chapter":
                    title = arg.strip()
                else:
                    body.append(("heading", (m.group(1), m.group(2), arg.strip())))
                if rest:
                    body.append(("line", fix_graphics(rest)))
                continue
            if re.match(r"^\s*\\(providecommand|newcommand|renewcommand|DeclareMathOperator)\b", code) \
                    and code.count("{") == code.count("}"):
                body.append(("global", raw))
                continue
            mb = re.match(r"^\s*\\begin\{([A-Za-z*]+)\}", code)
            if mb and mb.group(1) in THM_ENVS:
                body.append(("thm", None))
        body.append(("line", fix_graphics(raw.replace("\\newpage", ""))))
        depth += len(BEGIN_RE.findall(code)) - len(END_RE.findall(code))
        depth = max(depth, 0)
    if not title:
        sys.exit(f"{path.name}: гарчиг олдсонгүй")

    out = [
        f"% Лекц {num}. {title}",
        f"% Эх: latex/lectures/{path.name} (scripts/latex_to_beamer.py-ээр хөрвүүлсэн)",
        "% Frame бүр слайдад нэг (эсвэл allowframebreaks-аар хэд хэдэн) хуудас болно;",
        "% хэвлэх хувилбарт frame-ийн хил харагдахгүй, текст үргэлжилсэн байна.",
        "",
        f"\\MathLecture{{{num}}}{{{title}}}",
        "",
    ]
    sec = sub = ""
    frame = []

    def flush():
        while frame and not frame[-1].strip():
            frame.pop()
        while frame and not frame[0].strip():
            frame.pop(0)
        if frame:
            ftitle = sub or sec or title
            out.append(f"\\begin{{frame}}[allowframebreaks]{{{ftitle}}}")
            out.extend(frame)
            out.append("\\end{frame}")
            out.append("")
        frame.clear()

    for kind, payload in body:
        if kind == "heading":
            flush()
            level, star, arg = payload
            if level == "section":
                sec, sub = arg, ""
            elif level == "subsection":
                sub = arg
            else:
                sub = arg
            out.append(f"\\{level}{star}{{{arg}}}")
        elif kind == "global":
            # Тодорхойлолт frame-ийн гадна (frame нь бүлэг тул дотор нь орвол алга болно)
            if any(l.strip() for l in frame):
                frame.append(payload)
            else:
                out.append(payload)
        elif kind == "thm":
            if any(l.strip() for l in frame):
                flush()
        else:
            frame.append(payload)
    flush()
    return "\n".join(out).rstrip() + "\n"


def main():
    DST.mkdir(parents=True, exist_ok=True)
    for path in sorted(SRC.glob("lec[0-9][0-9]-*.tex")):
        num = int(path.name[3:5])
        (DST / f"lec{num:02d}.tex").write_text(convert(num, path), encoding="utf-8")
        print(f"lec{num:02d}.tex  <-  {path.name}")


if __name__ == "__main__":
    main()
