"""在 Theresa 上编译开卷手册：python build.py <tex目录>
把 \\ix{词} 改写成 \\index{拼音@词}，然后 xelatex ×2 → makeindex → xelatex ×2。"""
import os, re, shutil, subprocess, sys
from pypinyin import lazy_pinyin

src = sys.argv[1]
out = os.path.join(src, 'build')
os.makedirs(out, exist_ok=True)
TEX = r'E:\texlive\2023\bin\windows'


def key(word):
    plain = re.sub(r'[$\\{}^]', '', word)
    return ''.join(lazy_pinyin(plain)).lower()


def conv(m):
    parts = []
    for p in m.group(1).split('!'):
        parts.append(p if '@' in p else f'{key(p)}@{p}')
    return r'\index{' + '!'.join(parts) + '}'


for f in os.listdir(src):
    if f.endswith('.tex'):
        s = open(os.path.join(src, f), encoding='utf-8').read()
        if f != 'main.tex':
            s = re.sub(r'\\ix\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}', conv, s)
        open(os.path.join(out, f), 'w', encoding='utf-8').write(s)


def run(cmd):
    r = subprocess.run(cmd, cwd=out, capture_output=True)
    return r.returncode


xe = [os.path.join(TEX, 'xelatex.exe'), '-interaction=nonstopmode', '-file-line-error', 'main.tex']
for i in range(2):
    rc = run(xe)
    print('xelatex', i, rc)
    if rc:
        break
run([os.path.join(TEX, 'makeindex.exe'), 'main.idx'])
for i in range(2):
    print('xelatex', 2 + i, run(xe))
log = open(os.path.join(out, 'main.log'), encoding='utf-8', errors='replace').read()
for l in log.splitlines():
    if re.match(r'^(\./)?[\w.-]+\.tex:\d+:', l) or l.startswith('!') or 'Missing character' in l or ('undefined' in l.lower() and 'Reference' not in l):
        print(l[:200])
m = re.search(r'Output written on main.pdf \((\d+) pages', log)
print('pages', m.group(1) if m else None)
