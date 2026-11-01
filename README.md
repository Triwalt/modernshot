![MODERNSHOT](assets/banner.jpg)

# 现代光学 · 开卷手册

《现代光学》（傅里叶光学 + 视光学）期中考试用的开卷手册，153 页，适合黑白打印。

- **PDF**：[现代光学开卷手册.pdf](现代光学开卷手册.pdf)
- **源文件**：`tex/`（ctexbook，XeLaTeX 编译）

## 内容

- 第零章「零基础入门」：用信号与系统的语言讲傅里叶光学的四个核心概念（元件 = 乘法、传播 = 卷积、成像 = LTI 系统、像差 = 光瞳相位误差）
- 第 1–8 章：数学工具、平面波与空间频率、衍射、透镜与 4f 系统、成像系统（PSF / CTF / OTF / MTF）、像差与 Strehl 比、视光学、光度与色度
- 第 9 章：往年题详解与答题模板
- 解题决策树、题型索引、题干信号词表、术语表、公式框一览、关键词索引

书里的框分五类：【公式】【套路】【易错】【直觉】【例】，靠图标、文字标签和边框样式区分（黑白打印也能分清），使用说明里有图例。

首批校订的 [PPT 页码依据](docs/errata-first-batch.md) 使用课件右下角数字，正文以 `s` 标注；原有 `p` 标注表示 PDF 文件页序。

## 编译

需要 TeX Live（XeLaTeX、makeindex）、Noto Serif SC / Noto Sans SC 字体，以及 Python 包 `pypinyin`（索引按拼音排序）。

```
python build.py tex
```

`build.py` 把 `\ix{词}` 转成带拼音排序键的 `\index`，然后运行 xelatex ×2 → makeindex → xelatex ×2，输出在 `tex/build/main.pdf`。脚本开头的 `TEX` 变量是 TeX Live 可执行文件所在目录，请按自己的安装位置修改。
