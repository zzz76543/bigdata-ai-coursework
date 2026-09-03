# Big Data & AI Coursework

「大数据与人工智能」课程作业仓库 —— 涵盖数据处理、分布式计算与机器学习/深度学习的完整作业归档。

## 目录结构

```
bigdata-ai-coursework/
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

## 工具链

| 类别 | 主要工具 |
| --- | --- |
| 数据处理 | pandas, NumPy, Polars |
| 分布式计算 | PySpark, Hadoop (HDFS/MapReduce) |
| 机器学习 | scikit-learn, XGBoost |
| 深度学习 | PyTorch |
| 可视化 | Matplotlib, Seaborn |
