"""列出上游 vscode-docs 的 api/ 目录自上次同步以来的变化，并对应到本仓库的译文文件。

用法（在本仓库根目录运行）：
    python tools/sync_check.py <vscode-docs 克隆目录> [--fetch] [--to <提交号或分支>]

- 上次同步的基准提交号从 MAINTAINING.md 中“上游基准提交”一行读取；
- --fetch：先在 vscode-docs 克隆中执行 git fetch origin main；
- --to：比较的目标版本，默认 origin/main。
"""
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # 指南根目录（tools/ 的上一级）


def read_baseline():
    text = open(os.path.join(ROOT, 'MAINTAINING.md'), encoding='utf-8').read()
    m = re.search(r'上游基准提交[^`]*`([0-9a-f]{7,40})`', text)
    if not m:
        sys.exit('在 MAINTAINING.md 中找不到“上游基准提交”')
    return m.group(1)


def git(repo, *args):
    r = subprocess.run(['git', '-C', repo, *args], capture_output=True)
    if r.returncode:
        sys.exit(r.stderr.decode('utf-8', 'replace'))
    return r.stdout.decode('utf-8', 'replace')


META_KEYS = ('DateApproved:', 'ContentId:', 'MetaDescription:', 'MetaSocialImage:')


def only_metadata(repo, base, head, path):
    """判断一个文件的改动是否只发生在文件头的元数据行（官方常批量更新 DateApproved）。"""
    diff = git(repo, 'diff', '-U0', base, head, '--', path)
    changed = [l[1:].strip() for l in diff.splitlines()
               if l[:1] in '+-' and not l.startswith(('+++', '---'))]
    return bool(changed) and all(l.startswith(META_KEYS) or l == '' for l in changed)


def main():
    if not sys.stdout.isatty():
        sys.stdout.reconfigure(encoding='utf-8')  # 输出到管道 / Git Bash 时用 UTF-8，避免中文乱码
    args = sys.argv[1:]
    if not args or args[0].startswith('-'):
        sys.exit(__doc__)
    repo = args[0]
    target = args[args.index('--to') + 1] if '--to' in args else 'origin/main'
    if '--fetch' in args:
        git(repo, 'fetch', 'origin', 'main')
    base = read_baseline()
    head = git(repo, 'rev-parse', target).strip()
    print(f'基准提交：{base}')
    print(f'目标提交：{head}  {git(repo, "log", "-1", "--format=%ci %s", head).strip()}')
    out = git(repo, 'diff', '--name-status', '-M', base, head, '--', 'api/')
    if not out.strip():
        print('\napi/ 目录没有变化，无需同步。')
        return
    names = {'M': '修改', 'A': '新增', 'D': '删除', 'R': '重命名', 'C': '复制', 'T': '类型变化'}
    docs, assets = [], []
    for line in out.strip().splitlines():
        parts = line.split('\t')
        st = parts[0][0]
        src = parts[-1]
        local = src[len('api/'):]
        old = parts[1][len('api/'):] if st == 'R' else None
        exists = os.path.exists(os.path.join(ROOT, local))
        item = (names.get(st, st), local, old, exists)
        (docs if src.endswith('.md') else assets).append(item)
    print(f'\n文档变化（{len(docs)}）：')
    meta_only = 0
    for st, local, old, exists in docs:
        extra = f'（原路径 {old}）' if old else ''
        mark = '' if exists or st == '删除' else '  ← 本仓库尚无此文件'
        if st == '修改' and only_metadata(repo, base, head, 'api/' + local):
            mark = '  （仅文件头元数据变化，如 DateApproved，只需更新译文文件头）'
            meta_only += 1
        print(f'  [{st}] {local}{extra}{mark}')
    if meta_only:
        print(f'  其中 {meta_only} 篇只有文件头元数据变化')
    print(f'\n图片 / 其他资源变化（{len(assets)}）：')
    for st, local, old, _ in assets:
        extra = f'（原路径 {old}）' if old else ''
        print(f'  [{st}] {local}{extra}')
    print(f'\n查看某一篇的具体改动：git -C {repo} diff {base[:7]} {head[:7]} -- api/<路径>')
    print(f'同步完成后，把 MAINTAINING.md 中的基准提交改为：{head}')


if __name__ == '__main__':
    main()
