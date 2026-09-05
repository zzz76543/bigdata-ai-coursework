#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用 GitHub Git Database API 推送一个本地 commit，保留父链。
适用：HTTPS git 协议被掐、SSH 被掐，但 api.github.com 通。
用法：python api_push_commit.py <本地 commit SHA>
"""
import base64
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request

API = "https://api.github.com"
REPO = "zzz76543/bigdata-ai-coursework"


def api(method, path, token, payload=None):
    data = json.dumps(payload).encode("utf-8") if payload else None
    req = urllib.request.Request(
        API + path, data=data, method=method,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "Content-Type": "application/json",
            "User-Agent": "api-push-commit",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8")), resp.status
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        print(f"[API {e.code}] {method} {path}")
        print(body[:500])
        sys.exit(1)


def main():
    target_sha = sys.argv[1] if len(sys.argv) > 1 else "HEAD"
    token = os.environ.get("GITHUB_TOKEN") or _read_pat()
    if not token:
        print("[错误] 找不到 PAT"); sys.exit(1)

    # 1. 拿到本地 commit 信息
    show_out = subprocess.check_output(
        ["git", "show", target_sha, "--stat", "--format=%H|%P|%s"],
        encoding="utf-8")
    head_line = show_out.splitlines()[0]
    full_sha, parents_str, message = head_line.split("|", 2)
    parents = parents_str.split() if parents_str.strip() else []
    print(f"本地 commit: {full_sha[:10]}  message: {message}")
    print(f"父提交(本地): {parents}")

    # 2. 看这个 commit 动了哪些文件
    diff_files = subprocess.check_output(
        ["git", "show", "--name-only", "--format=", "-z", target_sha],
        encoding="utf-8").split("\x00")
    diff_files = [f.strip().strip('"') for f in diff_files if f.strip()]
    print(f"变更文件: {diff_files}")

    # 3. 拿到当前远端 main
    remote_ref, _ = api("GET", f"/repos/{REPO}/git/ref/heads/main", token)
    remote_head = remote_ref["object"]["sha"]
    remote_commit, _ = api("GET", f"/repos/{REPO}/git/commits/{remote_head}", token)
    base_tree = remote_commit["tree"]["sha"]
    print(f"远端 main: {remote_head[:10]}  base tree: {base_tree[:10]}")

    # 4. 为每个变更文件创建 blob + 加入新 tree
    new_tree_items = []
    for path in diff_files:
        with open(path, "rb") as fh:
            raw = fh.read()
        blob, _ = api("POST", f"/repos/{REPO}/git/blobs", token, {
            "content": base64.b64encode(raw).decode("ascii"),
            "encoding": "base64",
        })
        new_tree_items.append({
            "path": path.replace("\\", "/"),
            "mode": "100644",
            "type": "blob",
            "sha": blob["sha"],
        })
        print(f"  blob: {path} -> {blob['sha'][:10]}")

    new_tree, _ = api("POST", f"/repos/{REPO}/git/trees", token, {
        "base_tree": base_tree,
        "tree": new_tree_items,
    })
    print(f"新 tree: {new_tree['sha'][:10]}")

    # 5. 建新 commit，parent 是远端当前 HEAD
    new_commit, _ = api("POST", f"/repos/{REPO}/git/commits", token, {
        "message": message,
        "tree": new_tree["sha"],
        "parents": [remote_head],
    })
    print(f"新 commit: {new_commit['sha'][:10]}")

    # 6. 更新 main ref
    api("PATCH", f"/repos/{REPO}/git/refs/heads/main", token, {
        "sha": new_commit["sha"],
    })
    print(f"\n✅ 已推送 {new_commit['sha'][:10]} 到 main")


def _read_pat():
    cred_path = os.path.expanduser("~/.git-credentials")
    if not os.path.exists(cred_path):
        return None
    import re
    m = re.search(r'ghp_[A-Za-z0-9]+', open(cred_path).read())
    return m.group(0) if m else None


if __name__ == "__main__":
    main()