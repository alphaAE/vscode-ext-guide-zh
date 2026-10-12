import os, re
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # 指南根目录（tools/ 的上一级）
bad=[]; leftovers=[]
files=[os.path.join(d,f) for d,_,fs in os.walk(ROOT) for f in fs if f.endswith('.md')]
LINK = re.compile(r'!?\[[^\]]*\]\(([^)\s]+)(?:\s+"[^"]*")?\)')
SRC = re.compile(r'(?:src|href)="([^"]+)"')
for f in files:
    t=open(f,encoding='utf-8').read()
    nf=re.sub(r'```.*?```','',t,flags=re.S)
    ids=set(re.findall(r'<a id="([^"]+)"',t))
    for u in LINK.findall(nf)+SRC.findall(nf):
        if re.match(r'^(https?:|mailto:|command:|vscode:)',u): continue
        if u.startswith('/'): leftovers.append((f,u)); continue
        p,_,a=u.partition('#')
        tgt=os.path.normpath(os.path.join(os.path.dirname(f),p)) if p else f
        if not os.path.exists(tgt): bad.append((f,u,'missing file')); continue
        if a and tgt.endswith('.md'):
            tt=open(tgt,encoding='utf-8').read()
            if a not in set(re.findall(r'<a id="([^"]+)"',tt)): bad.append((f,u,'missing anchor'))
    for pat in ['kb(','kbstyle(','{% data','/assets/api']:
        if pat in nf: leftovers.append((f,pat))
for x in bad: print('BAD',os.path.relpath(x[0],ROOT),x[1],x[2])
for x in leftovers: print('LEFT',os.path.relpath(x[0],ROOT),x[1])
print(len(files),'files',len(bad),'bad',len(leftovers),'leftovers')
