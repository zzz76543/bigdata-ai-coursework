#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
兜底推送方案：通过 GitHub API 直接提交文件（一次 commit）
适用：git push 被网络彻底拦截时使用
用法：
    set GITHUB_TOKEN=ghp_xxxxxx        (Windows CMD)
    $env:GITHUB_TOKEN="ghp_xxxxxx"     (PowerShell)
    python push_via_api.py [提交信息]
"""
import base64
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request

API = "https://api.github.com"
REPO_NAME = "bigdata-ai-coursework"
MAX_FILE_BYTES = 25 * 1024 * 1024  # GitHub API 单文件上限约 25MB


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True,
                          encoding="utf-8", errors="replace")


def api(method, path, token, payload=None):
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8") if payload else None
    req = urllib.request.Request(
        API + path, data=data, method=method,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "Content-Type": "application/json",
            "User-Agent": "bdai-coursework-uploader",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        print(f"[API 错误] {method} {path} -> {e.code}")
        print(body[:500])
        sys.exit(1)


def main():
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        print("[错误] 请先设置环境变量 GITHUB_TOKEN")
        sys.exit(1)

    message = sys.argv[1] if len(sys.argv) > 1 else "feat: 通过 API 提交课程作业"

    # 1. 确认身份
    me = api("GET", "/user", token)
    owner = me["login"]
    print(f"账号：{owner}")

    # 2. 确保仓库存在
    try:
        api("GET", f"/repos/{owner}/{REPO_NAME}", token)
        print(f"仓库已存在：{owner}/{REPO_NAME}")
    except SystemExit:
        print("正在创建仓库...")
        api("POST", "/user/repos", token, {
            "name": REPO_NAME,
            "description": "大数据与人工智能课程作业仓库",
            "private": False,
            "auto_init": False,
        })
        print("仓库已创建")

    # 3. 收集待提交文件
    files = [f for f in run(["git", "ls-files"]).stdout.split("\n") if f.strip()]
    if not files:
        print("[错误] 没有已跟踪的文件，请先 git add")
        sys.exit(1)
    print(f"待提交文件：{len(files)} 个")

    # 4. 创建 blob
    tree = []
    for path in files:
        try:
            with open(path, "rb") as fh:
                raw = fh.read()
        except OSError as e:
            print(f"  跳过（读取失败）：{path} - {e}")
            continue
        if len(raw) > MAX_FILE_BYTES:
            print(f"  跳过（超过 25MB）：{path}")
            continue
        content = base64.b64encode(raw).decode("ascii")
        blob = api("POST", f"/repos/{owner}/{REPO_NAME}/git/blobs", token,
                   {"content": content, "encoding": "base64"})
        tree.append({"path": path.replace("\\", "/"), "mode": "100644",
                     "type": "blob", "sha": blob["sha"]})
        print(f"  + {path}")

    if not tree:
        print("[错误] 没有可提交的文件")
        sys.exit(1)

    # 5. 建 tree -> commit -> 更新 ref
    new_tree = api("POST", f"/repos/{owner}/{REPO_NAME}/git/trees", token, {"tree": tree})
    commit = api("POST", f"/repos/{owner}/{REPO_NAME}/git/commits", token, {
        "message": message,
        "tree": new_tree["sha"],
        "parents": [],
    })
    print(f"Commit 已创建：{commit['sha'][:8]}")

    # 6. 创建或更新 main 分支
    try:
        api("POST", f"/repos/{owner}/{REPO_NAME}/git/refs", token,
            {"ref": "refs/heads/main", "sha": commit["sha"]})
        print("已创建 main 分支")
    except SystemExit:
        api("PATCH", f"/repos/{owner}/{REPO_NAME}/git/refs/heads/main", token,
            {"sha": commit["sha"], "force": True})
        print("已更新 main 分支")

    print("\n" + "=" * 46)
    print(f"  完成！https://github.com/{owner}/{REPO_NAME}")
    print("=" * 46)


if __name__ == "__main__":
    main()
