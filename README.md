![MODERNSHOT](assets/banner.jpg)

# 现代光学 · 开卷手册

《现代光学》（傅里叶光学 + 视光学）开卷速查手册，205 页，适合黑白打印。

- **在线阅读**：<https://triwalt.github.io/modernshot/>
- **下载最新版 PDF**：<https://github.com/Triwalt/modernshot/releases/latest/download/modernshot.pdf>
- **历史版本**：[Releases](https://github.com/Triwalt/modernshot/releases)
- **源文件**：`tex/`（ctexbook，XeLaTeX 编译）

## 内容

- 第零章「零基础入门」：用信号与系统的语言讲傅里叶光学的四个核心概念（元件 = 乘法、传播 = 卷积、成像 = LTI 系统、像差 = 光瞳相位误差）
- 第 1–8 章：数学工具、平面波与空间频率、衍射、透镜与 4f 系统、成像系统（PSF / CTF / OTF / MTF）、像差与 Strehl 比、视光学、光度与色度
- 第 9 章：综合例题与答题模板
- 解题决策树、题型索引、题干信号词表、术语表、公式框一览、关键词索引

书里的框分五类：【公式】【套路】【易错】【直觉】【例】，靠图标、文字标签和边框样式区分（黑白打印也能分清），使用说明里有图例。

首批校订的 [PPT 页码依据](docs/errata-first-batch.md) 使用课件右下角数字，正文以 `s` 标注；原有 `p` 标注表示 PDF 文件页序。

## 编译

需要 TeX Live（XeLaTeX、makeindex）、Noto Serif SC / Noto Sans SC 字体，以及 Python 包 `pypinyin`（索引按拼音排序）。

```
python build.py tex
```

`build.py` 把 `\ix{词}` 转成带拼音排序键的 `\index`，然后循环运行 xelatex → makeindex，交叉引用和索引不再变化就停，输出在 `tex/build/main.pdf`。

只改了某几章时可以用快速模式 `python build.py tex ch08-photometry`：只排给定的章、只跑一轮，页码沿用上次整本编译的结果，输出 `tex/build/fast.pdf`。发布前仍需整本编译。脚本开头的 `TEX` 变量是 TeX Live 可执行文件所在目录，请按自己的安装位置修改。

## 发布

`main` 及其全部提交历史不保存 PDF。编译好以后新建一个 Release，附件命名为 `modernshot.pdf`，上面的下载链接总是指向最新的 Release。

在线阅读使用 GitHub Pages 的 `gh-pages` 分支。该分支仅有一个根提交，保存当前版本的 `modernshot.pdf` 和入口页；每次发布时重新创建单提交分支并用 `--force-with-lease` 更新，不追加 PDF 历史。历史版本只放在 Releases。发布 Release 后还需同步更新网页分支，二者不是自动联动。

主分支历史已重写。此前克隆过的协作者请另行保存未提交修改后重新克隆，不要把旧历史合回主分支。
