"""在 Theresa 上编译开卷手册：python build.py <tex目录> [章文件名...]
把 \\ix{词} 改写成 \\index{拼音@词}，然后循环 xelatex → makeindex，页码和引用不再变化就停。
给了章文件名（如 ch08-photometry）是快速模式：只排这几章、只跑一轮，页码和引用沿用上次整本的结果，
输出 build\\fast.pdf，不动 main.pdf。交付前要编整本。"""
import hashlib, os, re, shutil, subprocess, sys
from pypinyin import lazy_pinyin

src = sys.argv[1]
only = sys.argv[2:]
out = os.path.join(src, 'build')
os.makedirs(out, exist_ok=True)
TEX = r'E:\texlive\2023\bin\windows'
MAX_PASS = 6


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


def snapshot():
    """下一轮要读进来的文件（aux、目录、各种一览、索引）的指纹；一轮前后相同就说明已经稳定。"""
    h = {}
    for f in os.listdir(out):
        if f.startswith('fast.') or f.rsplit('.', 1)[-1] in ('tex', 'pdf', 'log', 'ilg', 'idx', 'xdv'):
            continue
        h[f] = hashlib.md5(open(os.path.join(out, f), 'rb').read()).hexdigest()
    return h


def xe(name):
    return [os.path.join(TEX, 'xelatex.exe'), '-interaction=nonstopmode', '-file-line-error', name + '.tex']


if only:
    job = 'fast'
    if not os.path.exists(os.path.join(out, 'main.aux')):
        sys.exit('还没有整本编译的结果，先不带章文件名编一次整本')
    shutil.copy(os.path.join(out, 'main.aux'), os.path.join(out, 'fast.aux'))
    s = open(os.path.join(out, 'main.tex'), encoding='utf-8').read()
    s = s.replace(r'\begin{document}', r'\includeonly{' + ','.join(only) + '}\n' + r'\begin{document}', 1)
    s = s.replace(r'\printindex', '')
    open(os.path.join(out, 'fast.tex'), 'w', encoding='utf-8').write(s)
    print('xelatex fast', run(xe(job)))
else:
    job = 'main'
    for i in range(MAX_PASS):
        before = snapshot()
        rc = run(xe(job))
        print('xelatex', i, rc)
        if rc:
            break
        run([os.path.join(TEX, 'makeindex.exe'), 'main.idx'])
        if snapshot() == before:
            break
    else:
        print('跑满', MAX_PASS, '轮仍未稳定')
log = open(os.path.join(out, job + '.log'), encoding='utf-8', errors='replace').read()
for l in log.splitlines():
    if re.match(r'^(\./)?[\w.-]+\.tex:\d+:', l) or l.startswith('!') or 'Missing character' in l or ('undefined' in l.lower() and 'Reference' not in l):
        print(l[:200])
print('undefined refs', len(re.findall(r"Reference `[^']*' on page \d+ undefined", log)))
m = re.search(r'Output written on %s.pdf \((\d+) pages' % job, log)
print('pages', m.group(1) if m else None)
