"""从上游 vscode-docs 取出指定文件（自动处理 Git LFS 存储的图片和视频）。

用法（在任意目录运行，需先运行过一次 tools/sync_check.py 准备好上游克隆）：
    python tools/upstream_get.py <路径> [<路径> ...] [--rev <提交号或分支>] [--repo <上游克隆目录>]

- 路径写成本仓库中的相对路径，或上游的 api/ 路径都可以，
  例如 extension-guides/images/webview/basics-no_content.png 或 api/extension-guides/webview.md；
- 图片、视频等非 .md 文件：写入本仓库的对应位置（覆盖旧文件）；
- .md 原文：写入 .upstream/files/<路径>，供对照阅读，不会覆盖译文；
- --rev 默认 origin/main；--repo 默认 .upstream/vscode-docs。
"""
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # 指南根目录（tools/ 的上一级）


def main():
    if not sys.stdout.isatty():
        sys.stdout.reconfigure(encoding='utf-8')  # 输出到管道 / Git Bash 时用 UTF-8，避免中文乱码
    args = sys.argv[1:]
    if not args or '-h' in args or '--help' in args:
        sys.exit(__doc__)
    opts = {'--rev': 'origin/main', '--repo': os.path.join(ROOT, '.upstream', 'vscode-docs')}
    paths = []
    i = 0
    while i < len(args):
        if args[i] in opts:
            opts[args[i]] = args[i + 1]
            i += 2
        else:
            paths.append(args[i].replace('\\', '/'))
            i += 1
    repo, rev = opts['--repo'], opts['--rev']
    if not os.path.isdir(os.path.join(repo, '.git')):
        sys.exit(f'找不到上游克隆 {repo}，请先运行 python tools/sync_check.py')
    for p in paths:
        local = p[len('api/'):] if p.startswith('api/') else p
        src = 'api/' + local
        data = subprocess.run(['git', '-C', repo, 'show', f'{rev}:{src}'], capture_output=True)
        if data.returncode:
            print(f'失败：{src}（{data.stderr.decode("utf-8", "replace").strip()}）')
            continue
        content = data.stdout
        if content.startswith(b'version https://git-lfs.github.com/spec/v1'):
            # 上游用 LFS 存储的文件：把指针转换成真实内容
            content = subprocess.run(['git', '-C', repo, 'lfs', 'smudge', '--', src],
                                     input=content, capture_output=True, check=True).stdout
        dest = os.path.join(ROOT, '.upstream', 'files', local) if local.endswith('.md') else os.path.join(ROOT, local)
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        with open(dest, 'wb') as f:
            f.write(content)
        print(f'已写入：{os.path.relpath(dest, ROOT)}（{len(content)} 字节）')


if __name__ == '__main__':
    main()
