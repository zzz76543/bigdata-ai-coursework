#!/usr/bin/env bash
# ============================================================
# GitHub 同步助手 —— 针对国内网络 git push 被拦截的情况
# 功能：创建远端仓库 -> 配置镜像通道 -> 推送代码
# 用法：bash github-sync.sh
# ============================================================
set -uo pipefail

REPO_NAME="bigdata-ai-coursework"
REPO_DESC="大数据与人工智能课程作业仓库"
DIRECT_URL="https://github.com"
# 通道按实测可用性排序（2026-09-03 校验）
# gh.idayer.com 同时支持网页代理与 git 协议，实测最稳
MIRRORS=(
  "https://gh.idayer.com"
  "https://ghproxy.net"
  "https://gh-proxy.com"
  "https://ghproxy.cc"
  "https://gh-proxy.net"
)

echo "=============================================="
echo "  GitHub 同步助手"
echo "=============================================="
echo ""

# ---------- 步骤 1：收集凭据 ----------
if [ -n "${GITHUB_USER:-}" ]; then GH_USER="$GITHUB_USER"; else read -r -p "GitHub 用户名: " GH_USER; fi
if [ -n "${GITHUB_TOKEN:-}" ]; then GH_TOKEN="$GITHUB_TOKEN"; else read -r -s -p "Personal Access Token: " GH_TOKEN; echo; fi

if [ -z "$GH_USER" ] || [ -z "$GH_TOKEN" ]; then
  echo "[错误] 用户名和 Token 都不能为空"; exit 1
fi

# ---------- 步骤 2：校验 Token 并创建仓库 ----------
echo ""
echo ">> [1/5] 校验 Token 有效性..."
AUTH_HEADER="Authorization: Bearer ${GH_TOKEN}"
USER_JSON=$(curl -s --max-time 25 -H "$AUTH_HEADER" https://api.github.com/user)
GH_LOGIN=$(echo "$USER_JSON" | grep -o '"login": *"[^"]*"' | head -1 | sed 's/.*"login": *"//;s/"//')

if [ -z "$GH_LOGIN" ]; then
  echo "[失败] Token 无效或网络不可达。返回内容："
  echo "$USER_JSON" | head -5
  exit 1
fi
echo "    认证成功，账号：$GH_LOGIN"

echo ">> [2/5] 检查远端仓库是否存在..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" --max-time 25 -H "$AUTH_HEADER" \
  "https://api.github.com/repos/${GH_LOGIN}/${REPO_NAME}")

if [ "$HTTP_CODE" = "200" ]; then
  echo "    仓库已存在，跳过创建"
else
  echo "    仓库不存在，正在创建..."
  CREATE_RESULT=$(curl -s --max-time 30 -X POST \
    -H "$AUTH_HEADER" \
    -H "Accept: application/vnd.github+json" \
    https://api.github.com/user/repos \
    -d "{\"name\":\"${REPO_NAME}\",\"description\":\"${REPO_DESC}\",\"private\":false,\"auto_init\":false}")
  if echo "$CREATE_RESULT" | grep -q '"full_name"'; then
    echo "    仓库创建成功"
  else
    echo "[警告] 自动创建未成功，请手动到网页创建。返回："
    echo "$CREATE_RESULT" | head -5
  fi
fi

# ---------- 步骤 3：配置本地身份 ----------
echo ">> [3/5] 配置 Git 身份..."
CURRENT_NAME=$(git config user.name 2>/dev/null || echo "")
if [ -z "$CURRENT_NAME" ]; then
  git config user.name "$GH_LOGIN"
  git config user.email "${GH_LOGIN}@users.noreply.github.com"
  echo "    已设置为：${GH_LOGIN} <${GH_LOGIN}@users.noreply.github.com>"
else
  echo "    保持现有身份：$CURRENT_NAME"
fi

# ---------- 步骤 4：探测可用推送通道 ----------
echo ">> [4/5] 探测可用通道（这步会尝试实际握手）..."
WORKING_URL=""

# 先试直连
if timeout 20 git ls-remote "https://${GH_USER}:${GH_TOKEN}@github.com/${GH_LOGIN}/${REPO_NAME}.git" HEAD >/dev/null 2>&1; then
  WORKING_URL="https://github.com/${GH_LOGIN}/${REPO_NAME}.git"
  echo "    [直连] 可用"
else
  echo "    [直连] 不可用"
  for M in "${MIRRORS[@]}"; do
    if timeout 25 git ls-remote "${M}/https://github.com/${GH_LOGIN}/${REPO_NAME}.git" HEAD >/dev/null 2>&1; then
      WORKING_URL="${M}/https://github.com/${GH_LOGIN}/${REPO_NAME}.git"
      echo "    [镜像] ${M} 可用"
      break
    else
      echo "    [镜像] ${M} 不可用"
    fi
  done
fi

if [ -z "$WORKING_URL" ]; then
  echo ""
  echo "[失败] 所有通道均不可用。请检查网络或稍后重试。"
  exit 1
fi

# ---------- 步骤 5：写入凭据并推送 ----------
echo ">> [5/5] 配置远端并推送..."

# 提取 host 用于凭据存储
CRED_HOST=$(echo "$WORKING_URL" | sed -E 's#https://([^/]+)/.*#\1#')

# 保存凭据到 ~/.git-credentials（避免明文出现在 .git/config）
mkdir -p "$HOME"
grep -v "https://${GH_LOGIN}@${CRED_HOST}" "$HOME/.git-credentials" 2>/dev/null > "$HOME/.git-credentials.tmp" || true
echo "https://${GH_LOGIN}:${GH_TOKEN}@${CRED_HOST}" >> "$HOME/.git-credentials.tmp"
mv "$HOME/.git-credentials.tmp" "$HOME/.git-credentials"
chmod 600 "$HOME/.git-credentials" 2>/dev/null || true
git config --global credential.helper store

git remote remove origin 2>/dev/null
git remote add origin "$WORKING_URL"
git branch -M main

# 确保有提交
if ! git rev-parse HEAD >/dev/null 2>&1; then
  git add -A
  git commit -q -m "init: 初始化课程作业仓库结构"
fi

echo ""
echo "    远端地址：$WORKING_URL"
echo "    正在推送..."
echo ""

if git push -u origin main; then
  echo ""
  echo "=============================================="
  echo "  推送成功！"
  echo "  仓库地址：https://github.com/${GH_LOGIN}/${REPO_NAME}"
  echo "=============================================="
  echo ""
  echo "提示：本机通过镜像推送，网页访问同样可能需要加速。"
else
  echo ""
  echo "[推送失败] 常见原因："
  echo "  1. Token 未勾选 repo 权限 -> 重新生成并勾选 repo"
  echo "  2. 镜像站临时故障 -> 重跑本脚本换一个镜像"
  echo "  3. 远端已有内容冲突 -> 先执行 git pull --rebase origin main"
fi
