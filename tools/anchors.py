import os, re, sys, collections
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # 指南根目录（tools/ 的上一级）
DRY = '--dry' in sys.argv

def md_files():
    for d, _, fs in os.walk(ROOT):
        for f in fs:
            if f.endswith('.md'):
                yield os.path.normpath(os.path.join(d, f))

def norm(s):
    return re.sub(r'[^a-z0-9]', '', s.lower())

def english_of(h):
    m = re.search(r'（([^（）]*)）\s*$', h)
    return m.group(1) if m else h

def canonical(t):
    if ' ' not in t.strip():
        w = t.strip()
        # 普通单词（如 Overview）按官网的规则转小写；标识符（如 onCommand、contributes.commands）保持原样
        return w.lower() if re.fullmatch(r'[A-Z][a-z]+', w) else w
    s = t.strip().lower()
    s = re.sub(r'[^a-z0-9 \-]', '', s)
    return re.sub(r' ', '-', s)

LINK = re.compile(r'\]\(([^)\s]+)\)')

def parse(path):
    lines = open(path, encoding='utf-8').read().split('\n')
    heads = []  # (line index, text)
    infence = False
    for i, l in enumerate(lines):
        if re.match(r'^\s*(```|~~~)', l):
            infence = not infence; continue
        if infence: continue
        m = re.match(r'^(#{1,6})\s+(.*?)\s*$', l)
        if m: heads.append((i, m.group(2)))
    return lines, heads

# 1. collect referenced anchors per target file
refs = collections.defaultdict(set)
for f in md_files():
    text = open(f, encoding='utf-8').read()
    text_nf = re.sub(r'```.*?```', '', text, flags=re.S)
    for u in LINK.findall(text_nf):
        if u.startswith('http') or u.startswith('mailto:'): continue
        if '#' not in u: continue
        p, a = u.split('#', 1)
        tgt = f if p == '' else os.path.normpath(os.path.join(os.path.dirname(f), p))
        refs[tgt].add(a)

# 2. insert anchors
unmatched = []
for f in md_files():
    lines, heads = parse(f)
    existing = set(re.findall(r'<a id="([^"]+)"></a>', '\n'.join(lines)))
    want = {}
    for idx, h in heads:
        if idx == 0 and h.startswith('#'): pass
        eng = english_of(h)
        ids = []
        c = canonical(eng)
        if c: ids.append(c)
        for a in refs.get(f, ()):
            if norm(a) == norm(eng) and a not in ids: ids.append(a)
        want[idx] = [i for i in ids if i not in existing]
    for a in refs.get(f, ()):
        ok = a in existing or any(a in v for v in want.values())
        if not ok: unmatched.append((f, a))
    if DRY: continue
    out = []
    for i, l in enumerate(lines):
        if i in want and want[i] and i != 0:
            # skip the H1 title (line 0)
            # remove trailing blank-line duplication: put anchors directly above heading
            for a in want[i]:
                out.append(f'<a id="{a}"></a>')
        out.append(l)
    open(f, 'w', encoding='utf-8').write('\n'.join(out))

print('UNMATCHED anchors:', len(unmatched))
for f, a in unmatched:
    print(' ', os.path.relpath(f, ROOT), '#' + a)
