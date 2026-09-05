# Git 速查卡

## 一、首次配置（只需做一次）

```bash
git config --global user.name  "你的名字"
git config --global user.email "你的邮箱@example.com"
git config --global init.defaultBranch main
git config --global core.autocrlf input      # Windows 建议，避免换行符告警
```

查看配置：

```bash
git config --global --list
```

## 二、日常提交三部曲

```bash
git status                      # 看改了什么
git add .                       # 暂存全部改动
git add 文件名                   # 只暂存指定文件
git commit -m "hw01: 完成数据清洗"
git push                        # 推送到远端
```

## 三、查看与回退

```bash
git log --oneline --graph       # 图形化查看提交历史
git diff                        # 查看未暂存的改动
git diff --staged               # 查看已暂存的改动

git restore 文件名               # 丢弃工作区改动（未 add）
git restore --staged 文件名      # 取消暂存（已 add，未 commit）
git reset --soft HEAD~1         # 撤销上一次提交，改动保留在暂存区
git reset --hard HEAD~1         # 撤销上一次提交，改动全部丢弃（危险）
```

## 四、分支协作

```bash
git branch                      # 查看本地分支
git checkout -b feature/hw02    # 新建并切换分支
git checkout main               # 切回主分支
git merge feature/hw02          # 合并分支到当前分支
git branch -d feature/hw02      # 删除已合并的分支
```

## 五、同步远端

```bash
git pull                        # 拉取并合并
git pull --rebase               # 拉取并变基（历史更干净）
git fetch origin                # 只拉取不合并
git remote -v                   # 查看远端地址
```

**推送前先拉取是好习惯**：`git pull --rebase && git push`

## 六、本仓库的双通道配置

本机到 GitHub 配了两条通道，**彼此独立**——一条断了另一条可能照常用：

| remote | 地址 | 用途 | 特点 |
| --- | --- | --- | --- |
| `origin` | `git@github.com:zzz76543/bigdata-ai-coursework.git` | 日常主用 | SSH 密钥，**永久有效**，不用管令牌 |
| `https-origin` | `https://github.com/zzz76543/bigdata-ai-coursework.git` | SSH 不通时备用 | 令牌已存本机，不用再输密码 |

```bash
git push origin main        # 主：走 SSH
git push https-origin main  # 备：走 HTTPS
```

**关于网络**：本机访问 `github.com` 是**间歇性阻断**，不是永久封锁——同一天内可能通断翻转好几次，等一会儿往往自己恢复。SSH 与 HTTPS 独立阻断，实测过 SSH 全通而 HTTPS 全断的情况，反之也有。

**卡住时先探测再动手**，别急着改配置：

```bash
# 测 HTTPS（200 = 通，000 = 断）
curl -s -o /dev/null -w "%{http_code}\n" --max-time 10 https://github.com/

# 测 SSH（看到 successfully authenticated = 通）
ssh -T git@github.com
```

SSH 返回 `Permission denied (publickey)` 说明**通道是通的**，只是公钥没配好；返回 `Connection reset` 或超时才是通道被掐。两者处理方式完全不同，别搞混。

## 七、生成访问令牌（PAT）

**PAT = Personal Access Token，个人访问令牌。** 2021 年 8 月起 GitHub 不再接受账号密码推代码，令牌就是密码的替代品——一串 `ghp_` 开头的字符，推送时代替密码使用。

**为什么不用密码**：密码泄露 = 整个账号失守；令牌可以随时单独吊销，也能限制它只能干某几件事。

**两种类型的取舍**：

| | fine-grained（细粒度） | classic（经典） |
| --- | --- | --- |
| 权限粒度 | 精确到单个仓库、单项操作 | 粗粒度，勾 `repo` 即全仓库 |
| 过期时间 | 1～366 天 | 可选不过期 |
| 能否建仓库 | 需**额外**勾 Administration: 读写 | 勾 `repo` 即可 |
| GitHub 态度 | 官方推荐 | 仍支持 |

**本仓库推荐 classic + `repo`**：一条勾选搞定、能自动建仓库、一学期不用换。代价是权限较宽（可访问你名下所有仓库）——新账号本来也只有这一个作业仓库，这点代价可以忽略。

生成步骤：头像 → **Settings** → **Developer settings** → **Personal access tokens** → **Tokens (classic)** → **Generate new token (classic)**

1. Note 填 `bdai-coursework`
2. 勾选 **`repo`**（不勾推不上去）
3. Expiration 选 90 days，或图省事选 No expiration
4. Generate —— **立刻复制保存**，关掉页面后就再也看不到了

若坚持用 fine-grained：Repository access 选 **All repositories**，权限里 **Contents: 读写** 和 **Administration: 读写** 两个都要勾。少了 Administration，`github-sync.sh` 调 API 建仓库会被 403 拒绝。

## 八、凭据管理

凭据保存在 `~/.git-credentials`（权限 600）。若 Token 更换：

```bash
# Windows PowerShell
notepad "$env:USERPROFILE\.git-credentials"
```

删除对应行后重新推送，会再次提示输入。

## 九、常见问题

**`failed to push some refs`**
远端有新提交，先执行 `git pull --rebase origin main` 再推送。

**`Permission denied (publickey)`**
用了 SSH 地址但没配密钥。改用 HTTPS 地址即可。

**`SSL certificate problem`**
公司/校园网证书拦截，可临时关闭校验（不推荐长期使用）：
`git config --global http.sslVerify false`

**中文文件名显示为转义序列**
执行：`git config --global core.quotepath false`

**提交了不该提交的文件（如数据、密钥）**
```bash
git rm --cached 文件名
echo "文件名" >> .gitignore
git commit -m "chore: 移除误提交文件"
```
若已推送到远端且含密钥，**立即去 GitHub 吊销该 Token**。
