# Skills / Rules / Instructions 的专业工作流（SkillOps）与中心化资料入口

本 Playbook 目标：把“写 Skill 很复杂”拆成可执行、可迭代、可评测的工程流程（SkillOps），并给出可直接参考的中心化资料入口（Centralized hubs）。

> 你可以把 Skills 理解为“某个领域专家的浓缩知识 + 可执行 SOP + 可控工具链”。专业团队通常不会把它当一次性提示词，而是当作**版本化、可回归的产品接口**来维护。

---

## 1) 专业人士的 Working Pattern（SkillOps：从 0 到可持续迭代）

### 1.1 入口：从真实任务日志出发（不是从灵感出发）

1. **收集真实样本**：把你一段时间的真实任务记录成可复现样本（输入、上下文、你实际做的步骤、产物）。  
2. **定义“成功/失败”**：写清验收标准（输出格式/字段、必须跑的命令、必须引用的来源、允许的拒答与降级）。  
3. **先定边界再写流程**：in-scope / out-of-scope / 需要人工确认的点（避免范围膨胀）。

### 1.2 产物化：把 Skill 写成“可执行手册 + 可复用工件”

专业团队常把“指令/模板”固定成结构化片段，便于维护与复用：

- **Description**：这是什么、什么时候用、输入是什么（负责“唤醒/路由”）
- **Examples**：正例/反例/边界例（负责“对齐输出”）
- **Dialog / Memory policy**：多轮如何推进、何时收集缺失信息（负责“稳定执行”）

并把“重复且易错”的部分固化为脚本（scripts）与模板（assets），把“长尾细节/规范”下沉到 references（按需加载）。

#### 1.2.1 官方 Skill Creator Guide 的关键原则（建议直接内化到写法里）

- **Concise is key**：上下文窗口是公共资源；`description` 负责唤醒/路由，正文只写“非显而易见”的流程性信息
- **设置合适的自由度**：可变任务用文本说明；可参数化步骤用脚本/伪代码；高风险/易错流程用“低自由度脚本”锁定一致性
- **渐进式披露**：把长内容下沉到 `references/`；把确定性流程下沉到 `scripts/`；把模板/样板下沉到 `assets/`

### 1.3 评测驱动：把 Skill 当作“可回归的产品接口”

典型闭环（强烈建议你照搬）：

1. **Dataset（用例集）**：golden set（核心）/ regression（历史失败）/ adversarial（红队对抗）  
2. **Target（被测目标）**：真实的 Skill 执行链路（含工具调用/脚本）  
3. **Evaluators（评分器）**：确定性断言（结构/格式/合规）+ LLM-as-judge（语义/正确性）  
4. **对比版本**：同一数据集上对比“改动前 vs 改动后”（模型/提示词/检索/工具任一变化都可能导致回归）
5. **CI 门禁**：阈值不达标直接 fail build（质量门）
6. **线上观测**：把真实失败样本回流为新的回归用例（离线评测 + 线上 trace 的闭环）

### 1.4 发布与维护：像软件一样版本化

- **SemVer**：把对外行为当 public API；发布后不可变更；弃用与破坏性变更要可追踪。  
- **Keep a Changelog**：每次变化写清 Added/Changed/Deprecated/Removed/Fixed/Security，并绑定“评测对比证据 + 影响面”。

---

## 2) 你要找的“中心化（Centralized）网站”是什么（按优先级）

### P0（第一优先级：官方/标准/可复用工件仓库）

- OpenAI Skills（技能仓库/分发/安装范式）：`https://github.com/openai/skills`
- OpenAI Cookbook（示例与可复用 recipes）：`https://github.com/openai/openai-cookbook`
- OpenAI Evals（评测框架/基准注册表）：`https://github.com/openai/evals`
- OWASP GenAI / LLM Top 10（威胁模型与安全检查点）：`https://genai.owasp.org/llm-top-10/`
- llms.txt 规范提案（面向 LLM 的文档入口格式）：`https://llmstxt.org/llms.txt`

### P0（厂商官方“写作规范/最佳实践”）

- Google（Gemini Prompting guides）：`https://ai.google.dev/gemini-api/docs/prompting-intro`
- Microsoft Learn（Prompt engineering）：`https://learn.microsoft.com/en-us/azure/ai-services/openai/concepts/prompt-engineering`

### P1（社区型“系统化教程/模式库”）

- Prompt Engineering Guide（聚合/技巧/模式）：`https://github.com/dair-ai/Prompt-Engineering-Guide`
- Learn Prompting（教材/课程型）：`https://github.com/trigaten/Learn_Prompting`

### P1（框架生态的“可复用 Prompt/模板 Hub”）

- LangChain Hub：`https://github.com/hwchase17/langchain-hub`
- LlamaIndex prompts：`https://docs.llamaindex.ai/en/stable/module_guides/models/prompts/`

### P1（文档与信息架构：把 Skill 写清楚、写可维护）

- Diátaxis（Tutorial/How-to/Reference/Explanation 的信息架构框架）：`https://diataxis.fr/`
- Write the Docs（Docs as Code）：`https://www.writethedocs.org/guide/docs-as-code/`
- Google developer documentation style guide：`https://developers.google.com/style`
- Nielsen Norman Group（信息气味/信息觅食/搜索日志分析等）：`https://www.nngroup.com/`
- Microsoft “Guidelines for Human-AI Interaction”（可发现性/可唤醒性）：`https://www.microsoft.com/en-us/research/publication/guidelines-for-human-ai-interaction/`

---

## 3) 把你的三大阶段拆成“你需要做的事情”（可执行清单）

下面直接对应你提出的 3 大块步骤。

### 3.1 深入研究与探索（Wide Research → Processing）

**你要做：**

1. 先定研究问题（你要解决的“唤醒/执行/维护”的哪一块）。  
2. 用 Wide Research 扇出子问题：每个子问题只回答一个维度（触发、结构、评测、安全、知识源等）。  
3. 统一 raw 归档：每个事实都能追溯到 URL + 本地快照路径。  
4. Processing（把资料变成可复用资产）：输出“Pattern Library”（模式库）与“Checklist”（检查表），不要只输出长文章。

**建议产物：**

- `pattern_library/`：按主题分类的模式卡片（Trigger / SOP / Evals / Guardrails / Knowledge sources）
- `source_registry.json`：来源注册表（url、raw_path、last_fetched、hash、更新频率）

### 3.2 筛选与机制建立（Checkpoints + Trigger test）

**你要做：**

1. 用 Rubric 把“好坏”量化：至少覆盖 Trigger / SOP 可执行性 / 评测回归 / 安全 / 可维护性。  
2. 为每个 Skill 建最小触发测试集（Prompt suite）：  
   - A 组：显式调用（强制唤醒）  
   - B 组：典型自然语言（应当隐式唤醒）  
   - C 组：同义词/口语/拼写噪声（召回测试）  
   - D 组：对抗/混淆（注入/越权/外部内容夹带指令）
3. 设“通过/失败”的硬门禁：例如 Invoke@1/2、False-invoke、Turns-to-invoke、安全对抗用例必须 0 泄露。

#### 3.2.1 让“唤醒概率”不靠运气：把它当成可评测的路由问题

你遇到的 “flip coins（50% / 50%）” 本质上是：路由特征不够清晰 / 多个 Skill 描述高度重叠 / 缺少回归用例导致改一次坏一次。

**关键机制：**在 Codex Skills 里，*负责唤醒/路由的是 `SKILL.md` 的 YAML frontmatter 里的 `name` + `description`*；正文内容通常只有在 Skill 被选中后才会加载。因此提升唤醒概率，优先投入在 `description` 的工程化写法与评测闭环上。

**把 `description` 当成“检索文档 + 路由特征”来写：**

- 写清 **要做什么（动词）+ 对什么做（对象/产物）+ 何时用（触发语境）**：例如“并行调研链接并聚合报告”“对一组 issue 做归因与分流”“生成可执行脚本并跑通验证”。
- 覆盖 **真实用户措辞的同义词**（来自你自己的任务日志）：例如“并行/批量/拆分子任务/汇总/带引用/覆盖率”。
- 提供 **区分度特征**：关键文件类型（`.pdf/.docx/.sql`）、关键工具/平台名（`git`、`gh`、`linear`）、关键约束（“必须带引用”“必须能回归评测”）。
- 写 1 句 **边界/不适用**（控制误唤醒）：例如“不要用于一般写作/闲聊/非该领域问题”。
- 句子尽量短，避免把 SOP 细节塞进 `description`（它会常驻上下文）；长尾细节下沉到 `references/`，确定性步骤下沉到 `scripts/`。

**做成可回归的评测闭环（建议直接照搬）：**

- 先索引本地已安装 Skills：`python3 scripts/index_skills.py --out skills_index.json`
- 写/维护触发用例集：从 `datasets/trigger_cases.example.json` 复制成你的 `datasets/trigger_cases.json`
- 跑基线（BM25 召回）：`python3 scripts/trigger_eval.py --skills skills_index.json --cases datasets/trigger_cases.json --top-k 5 --out trigger_eval_results.json`
- 可选：再跑一次 “类隐式触发路由”（需要 `--use-codex`；用于评估 False-invoke、误路由、稳定性）
- 初始化/打包技能（可选）：`python3 scripts/init_skill.py ...`、`python3 scripts/package_skill.py ...`

### 3.3 抽象与知识溯源（Skill=领域专家知识）

**你要做：**

1. 把知识源分层：标准/官方规则（骨架）→ 权威机构共识（补充）→ 平台实践（高变动）。  
2. 每个角色只维护 3–6 个“中心化入口”，避免维护爆炸。  
3. 落到 references 的方式要“可维护”：sources 清单 + 蒸馏 playbook + glossary + 刷新策略（hash/更新时间/差异记录）。  
4. 对高变动领域（SEO/平台政策）设置“刷新与差异记录”机制，并把变化当作版本发布。

---

## 4) 本仓库已有材料（可直接复用）

- 第一轮调研与方法论/评估维度：`runs/2025-12-28-skills-384d09/report_cn.md`
- 第一轮 Rubric（可直接用作评分/门禁草案）：`runs/2025-12-28-skills-384d09/rubric.yaml`
- 第二轮补充调研（中心化入口/Diataxis/llms.txt/安全/可发现性）：`runs/2025-12-28-skills-a170cd/child_outputs/`
- 原始汇总：`runs/2025-12-28-skills-a170cd/aggregated_raw.md`
- 可唤醒性/可发现性工具：`scripts/index_skills.py`、`scripts/trigger_eval.py`、`datasets/trigger_cases.example.json`
