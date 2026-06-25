# 一站式智能旅行规划专家\n基于Qwen2.5微调的旅行Agent系统。
# 🌍 一站式智能旅行规划专家 (Multi-Agent Travel System)

[![Model](https://img.shields.io/badge/Model-Qwen2.5--0.5B--Instruct-blue)](https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct)
[![Fine-tuning](https://img.shields.io/badge/Method-LoRA-orange)](#)
[![Framework](https://img.shields.io/badge/Framework-Gradio-green)](#)

本项目是一款基于 **Qwen2.5-0.5B** 轻量化大模型开发的智能旅行 Agent 系统。通过 **多智能体协作 (Multi-Agent System)** 架构，实现了从意图识别、实时气象抓取、路径规划到数字化归档的完整闭环。

---

## 🌟 核心特性

- **🤖 多智能体协同 (MAS)**：
  - **Agent 1 (TravelExpert)**：负责逻辑推理、API 调度与导游风格文案创作。
  - **Agent 2 (FileArchivist)**：基于对话历史回溯，实现攻略的一键本地 Markdown 归档。
- **🎯 领域深度微调**：
  - 基于 200+ 条自主构造的旅行指令数据集进行 **LoRA 微调**。
  - 显著提升了小参数模型（0.5B）的工具调用（Tool Use）准确率与 ReAct 思维链能力。
- **🛠️ 工业级工具集成**：
  - **高德地图 API**：实时天气感知、地理编码转换、步行路径规划。
  - **SerpApi**：抓取全网最新旅行建议与社交媒体热搜攻略。
- **🛡️ 智能意图护栏**：
  - 内置 Python 逻辑过滤层，精准拦截非旅游业务（如数学、编程、考试）的非法请求。
- **📂 RAG 知识库增强**：
  - 结合本地结构化 JSON 知识库，弥补大模型在垂直领域私有信息的不足。

---

## 📂 项目结构

```text
Travel_Agent_Project/
├── Agent1/                  # 规划专家智能体
│   ├── tools/               # 外部工具集成 (Weather, Map, Search)
│   └── main_agent.py        # 意图识别与决策逻辑
├── Agent2/                  # 归档专家智能体
│   └── main_agent.py        # 上下文回溯与持久化存储逻辑
├── data/                    # 微调数据集 (Alpaca format)
├── output/travel_lora       # LoRA 适配器权重文件
├── saved_plans/             # 自动生成的本地 Markdown 档案
├── web_demo_final.py        # Gradio 前端交互主程序
└── requirements.txt         # 依赖环境配置

## 🚀 快速开始
1. 环境准备 (建议 AutoDL 环境)
# 激活虚拟环境
source /root/autodl-tmp/llm_homework/.venv/bin/activate

# 安装依赖
pip install gradio transformers peft accelerate requests chromadb -i https://mirrors.aliyun.com/pypi/simple/

2. 配置 API Key
在运行前，请确保在 Agent1/tools/ 目录下的相关工具脚本中配置以下 Key：
Amap Key: 高德开放平台
SerpApi Key: SerpApi官网

3. 启动系统
python web_demo_final.py
运行成功后，点击终端输出的 https://xxxx.gradio.live 公网链接即可访问。

💡 典型指令示例
意图分类	测试指令	预期行为
攻略规划	"帮我规划一下成都的攻略，要看大熊猫。"	调用搜索+天气，生成 Markdown 行程表
气象建议	"2026年6月成都天气热吗？该穿什么？"	识别远期日期，给出季节性避暑建议
数字化归档	"帮我把刚才生成的攻略保存记录。"	Agent 2 触发，在 saved_plans/ 生成 .md 文件
业务拦截	"帮我解一下这个二元一次方程。"	触发护栏，礼貌拒绝并重申导游身份

📝 鸣谢
本项目作为《大模型微调与优化》课程大作业（模式二：个人提交）。
感谢 AutoDL 提供的算力支持。
