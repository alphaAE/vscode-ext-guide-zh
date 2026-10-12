import os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # 指南根目录（tools/ 的上一级）
LINK = re.compile(r'\]\(([^)\s]+)\)')
refs = set()
files = [os.path.join(d,f) for d,_,fs in os.walk(ROOT) for f in fs if f.endswith('.md')]
for f in files:
    t = open(f,encoding='utf-8').read()
    for u in LINK.findall(t):
        if '#' in u and not u.startswith('http'):
            p,a = u.split('#',1)
            tgt = os.path.normpath(f if p=='' else os.path.join(os.path.dirname(f),p))
            refs.add((tgt,a))
removed=0
cjk = re.compile(r'[\u4e00-\u9fff]')
for f in files:
    lines = open(f,encoding='utf-8').read().split('\n')
    out=[]
    for i,l in enumerate(lines):
        m = re.match(r'^<a id="([^"]+)"></a>$', l)
        if m:
            a = m.group(1)
            j = i
            while j < len(lines) and lines[j].startswith('<a id='): j += 1
            h = lines[j] if j < len(lines) else ''
            bad = (not a.isascii()) or (cjk.search(h) and '（' not in h and (os.path.normpath(f),a) not in refs) or a.strip('-')=='' 
            if bad: removed+=1; continue
        out.append(l)
    open(f,'w',encoding='utf-8').write('\n'.join(out))
print('removed',removed)
