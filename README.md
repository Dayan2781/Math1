# Математик I В

Сайт: <https://dayan2781.github.io/Math1/>

`main` салбар руу push хийх бүрт GitHub Actions дараах хоёр алхмыг хийгээд сайтыг шинэчилнэ:

1. `latex/build.sh` нь `latex/lectures/` доторх лекцүүдээс PDF үүсгэнэ.
2. `pretext build html` нь `source/` доторх PreTeXt номыг HTML болгоно.
   PDF-үүд сайтын **Лекцийн материал** хуудаснаас татагдана.

## Хавтаснууд

| Хавтас | Агуулга |
| --- | --- |
| `source/` | PreTeXt ном (`main.ptx`, `chapters/`) |
| `source/lecture-materials.ptx` | Лекцийн PDF-үүдийн жагсаалт |
| `source/syllabus.ptx` | Хичээлийн хөтөлбөр ба үнэлгээ |
| `latex/preamble.tex` | Бүх лекцийн PDF-д хуваалцах преамбл |
| `latex/lectures/` | Лекц, семинар, гэрийн даалгаврын LaTeX эх файлууд |
| `latex/pictures/` | LaTeX-д ашиглах зургууд |

## Шинэ лекц нэмэх

1. `latex/lectures/lec17-....tex` файлыг нэмнэ (`\chapter{...}`-ээр эхэлбэл сайн).
2. `latex/build.sh` доторх `LECTURES` жагсаалтад `"17|lec17-...|"` мөр нэмнэ.
3. `source/lecture-materials.ptx` доторх хүснэгтэд мөр нэмнэ.
4. Push хийнэ.

## Өөрийн компьютер дээр шалгах

```sh
./latex/build.sh          # бүх PDF (xelatex хэрэгтэй)
./latex/build.sh lec06    # зөвхөн нэг лекц
pretext build html        # сайт → output/html/
pretext view html
```
