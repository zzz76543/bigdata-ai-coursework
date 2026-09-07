# Big Data & AI Coursework

「大数据与人工智能」课程作业仓库 —— 涵盖数据处理、分布式计算与机器学习/深度学习的完整作业归档，以及「Agent / Skill 概念学习」专题作业。

## 目录结构

```
bigdata-ai-coursework/
├── .workbuddy/
│   └── skills/
│       └── concept-learning/
│           └── SKILL.md          # 项目级 Skill：概念学习资料生成器
├── learning-materials/           # Agent / Skill 概念学习作业交付物
│   ├── agent.html                # 概念一：Agent
│   ├── llm-context.html          # 概念二：大模型的上下文
│   ├── skill.html                # 概念三：Skill
│   └── concept-relationship.html # 三概念关系说明（含流程图）
├── data/
│   ├── raw/            原始数据（不入 Git，见 .gitignore）
│   └── processed/      清洗后的中间数据
├── notebooks/          Jupyter 探索性分析与实验记录
├── src/
│   ├── bigdata/        分布式计算脚本（Spark / Hadoop / Flink）
│   └── ai/             机器学习与深度学习代码
├── assignments/        按作业编号归档（hw01, hw02, ...）
├── docs/               课程笔记、环境配置说明
└── reports/            实验报告与结果分析
```

---

## Agent / Skill 概念学习作业

本仓库包含一份专题作业：围绕 **Agent、大模型的上下文、Skill** 三个概念，产出一个可复用的项目级 Skill 和四份学习资料。

### Skill 存放路径

```
.workbuddy/skills/concept-learning/SKILL.md
```

这个 Skill 名为 `concept-learning`（概念学习资料生成器），是一个**泛化**的技能：它接收任意一个新概念作为学习主题，按固定的「五段式」结构生成学习资料，而不是只为本次三个概念写死的一次性提示词。SKILL.md 顶部含 YAML 元数据（`name` 与 `description`），正文明确了适用场景、输入信息、生成步骤、输出结构、资料来源要求与自检要求。

### 如何在 WorkBuddy 中调用

**方式一（项目级，推荐）**：把本仓库作为项目在 WorkBuddy 中打开，Skill 位于项目根目录的 `.workbuddy/skills/` 下，WorkBuddy 会自动发现并按需加载。当你在对话里说"帮我学懂某个新概念"时，WorkBuddy 会匹配该 Skill 并按其流程生成资料。

**方式二（用户级，全局可用）**：把 `concept-learning` 目录复制到用户级技能目录：

```
~/.workbuddy/skills/concept-learning/
```

复制后，在任意项目的对话中都能调用该 Skill。

> 两种方式下，调用都无需手动指定路径——只需用自然语言描述"学懂一个概念"的意图，WorkBuddy 会依据 Skill 的 `description` 自动触发。

### 已生成的学习资料

| 文件 | 概念 | 要点 |
| --- | --- | --- |
| `learning-materials/agent.html` | Agent | 个人解释、四大组成、GitHub 建仓场景、与聊天机器人的区别 |
| `learning-materials/llm-context.html` | 上下文 | 上下文窗口、工作记忆 vs 训练数据、context rot |
| `learning-materials/skill.html` | Skill | SKILL.md 结构、渐进披露、与一次性提示词的分界 |
| `learning-materials/concept-relationship.html` | 三概念关系 | 能力闭环流程图、上下文如何影响 Agent、Skill 如何沉淀能力 |

每份资料均包含：概念的个人解释、核心机制或组成、一个具体应用场景、易混淆问题或使用边界、可核查的资料来源链接。

### AI 使用说明与人工核查

本作业的部分内容由 AI 辅助生成。以下是 AI 完成的工作，以及我（Jack）所做的人工核查：

**AI 完成的工作**
- 起草 `concept-learning` Skill 的 SKILL.md；
- 生成四份学习资料的初稿（含个人解释、机制、场景、来源链接）；
- 设计资料的 HTML 排版与流程图。

**人工核查清单（逐条核对后才算定稿）**

| 核查项 | 状态 |
| --- | --- |
| 三份资料中"个人解释"是否确实是我自己的理解，而非照搬定义 | 待核查 |
| 资料来源链接是否真实可点开、且确实支撑文中说法 | 待核查 |
| SKILL.md 是否真的能套用到任意新概念（而非只适用于本次三个概念） | 待核查 |
| 全仓库是否无 API Key、密码、个人隐私等敏感信息 | 待核查 |

> 核查完成后请把上表状态更新为「已核查」，并在对应文件里修订任何与个人理解不符的表述。

---

## 环境依赖

```bash
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## 使用约定

- 每次作业在 `assignments/` 下新建独立子目录，互不干扰
- 数据集一律放 `data/raw/`，不要直接提交大文件到仓库
- 实验结论同步更新到 `reports/`，方便期末复盘
- 提交信息统一格式：`hw01: 完成数据清洗与特征工程`

## 仓库地址

<https://github.com/zzz76543/bigdata-ai-coursework>

## 克隆到新机器

```bash
# 方式一：SSH（推荐，配置一次永久有效）
git clone git@github.com:zzz76543/bigdata-ai-coursework.git

# 方式二：HTTPS（SSH 连不上时用这个）
git clone https://github.com/zzz76543/bigdata-ai-coursework.git
```

## 日常推送

```bash
git add .                            # 暂存改动
git commit -m "hw01: 完成数据清洗"    # 提交
git push origin main                 # 推送（走 SSH）
```

若 SSH 通道被网络阻断，改走备用通道：

```bash
git push https-origin main           # 走 HTTPS（凭据已存本机，不需再输密码）
```

推送前先 `git pull --rebase origin main`，避免与他人改动冲突。

## 工具链

| 类别 | 主要工具 |
| --- | --- |
| 数据处理 | pandas, NumPy, Polars |
| 分布式计算 | PySpark, Hadoop (HDFS/MapReduce) |
| 机器学习 | scikit-learn, XGBoost |
| 深度学习 | PyTorch |
| 可视化 | Matplotlib, Seaborn |
