# Математик I В — LaTeX слайд ба хэвлэх хувилбар

Нэг эх файлаас хоёр төрлийн PDF гарна:

| Үндсэн файл | Юу гарах вэ |
| --- | --- |
| `slides.tex` | Хичээл дээр үзүүлэх **слайд** (beamer, 16:9) |
| `print.tex`  | **Хэвлэх** хувилбар (A4, нэг лекц эсвэл бүх 16 лекц нэг ном) |

Хоёулаа `lectures/lecNN.tex` (NN = 01…16) файлуудыг ашигладаг. Тиймээс лекцийн
агуулгыг нэг л газар засахад слайд ба хэвлэх хувилбар хоёулаа шинэчлэгдэнэ.

## Overleaf дээр

1. Overleaf → **New Project → Upload Project** → `math1-latex-overleaf.zip`-г сонгоно.
2. Compiler нь XeLaTeX байх ёстой. `latexmkrc` файл үүнийг автоматаар тохируулдаг;
   хэрэв алдаа гарвал **Menu → Compiler → XeLaTeX** гэж сонгоно.
3. **Menu → Main document** дээр `slides.tex` эсвэл `print.tex`-г сонгоод Recompile.
4. Аль лекцийг гаргахаа файлын эхний мөрөнд бичнэ:
   * `slides.tex`: `\providecommand*{\LECTURE}{05}` → 5-р лекцийн слайд
   * `print.tex`: `\providecommand*{\LECTURE}{05}` → 5-р лекцийн хэвлэх хувилбар,
     `\providecommand*{\LECTURE}{all}` → 16 лекц бүгд нэг ном

## Лекцийн файл бичих дүрэм

```latex
\MathLecture{5}{Тригонометр, илтгэгч ба логарифм функц}  % слайдад гарчгийн хуудас, хэвлэхэд бүлэг

\section{Тригонометр функцүүд}          % frame-ийн гадна
\subsection{Нэгж тойрог}

\begin{frame}[allowframebreaks]{Нэгж тойрог}   % нэг слайд (урт бол автоматаар хуваагдана)
\begin{definition} ... \end{definition}
\end{frame}
```

* `frame`-ийн хил зөвхөн слайдад харагдана; хэвлэх хувилбарт текст үргэлжилсэн байна.
* Зөвхөн слайдад гаргах зүйл: `\mode<presentation>{...}` эсвэл `\only<presentation>{...}`;
  зөвхөн хэвлэхэд: `\mode<article>{...}`.
* Орчнууд: `definition`, `theorem`, `proposition`, `lemma`, `example`, `remark`,
  `note`, `cor`, `prof` (баталгаа), `problem`, `solution`.
* Бодолтыг нуух: `common/preamble.tex` дотор `\showsolutionsfalse`.
* `tikzpicture` ба `tabular`-ыг `fitbox` орчинд хийвэл слайдад багтахгүй үед автоматаар
  жижигрэнэ.
* Слайдад `multicols` нэг багана болдог (урт жагсаалт хэд хэдэн слайдад хуваагдахын тулд).
* Зургууд `pictures/` хавтсанд.

## Өөрийн компьютер дээр

```sh
./build.sh       # 16 слайд + 16 хэвлэх + бүтэн ном → pdf/
./build.sh 07    # зөвхөн 7-р лекц
```

## Эх сурвалж

`lectures/lecNN.tex` нь `latex/lectures/lecNN-*.tex` файлуудаас
`scripts/latex_to_beamer.py`-ээр анх хөрвүүлэгдсэн. Скриптийг дахин ажиллуулбал
энд хийсэн гар засвар дарагдана.
