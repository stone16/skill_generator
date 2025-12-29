# Skills Generator · HM（Human Manual）

目标：把“不断创建新 Skills + 每次都走 SOP + PR 前有唤醒概率回测门禁”做成可执行的工程流（SkillOps）。

---

## 0) TL;DR（你每次改完就跑）

1. 维护触发用例集：`datasets/trigger_cases.json`
2. 跑本地预检（index + BM25 baseline）：

```bash
python3 scripts/skillops_preflight.py
```

默认门禁阈值（可按你的数据集成熟度调整）：`bm25_hit_at_k>=0.8`、`bm25_recall_at_k>=0.6`（用 `--min-bm25-hit-at-k/--min-bm25-recall-at-k` 覆盖）。

3. 可选：再跑一次 Codex 路由评测（更贴近真实“隐式唤醒”）：

```bash
python3 scripts/skillops_preflight.py --use-codex
```

> CI 里默认只跑 BM25；当 CI 环境具备 `codex`/凭证时再开启 `--use-codex`（避免不稳定或无法认证导致所有 PR 卡死）。

---

## 1) 本仓库约定的目录结构（建议）

- `skills/`：你在这个仓库里持续新增/迭代的 Skills（每个子目录一个 Skill，内含 `SKILL.md`）
- `datasets/trigger_cases.json`：触发/可发现性回测用例集（prompt suite）
- `scripts/`：索引、评测、预检与 CI 门禁脚本
- `docs/`：方法论与写法（详见 `docs/skills_playbook_cn.md`）
- `runs/`：调研与跑批产物（历史证据与参考）

---

## 2) 新增/更新一个 Skill 的 SOP（每次都走）

### Step 0：用具体例子把 Skill “说明白”

对每个候选 Skill，先写清两件事：

- Trigger：用户会怎么说（自然语言 + 同义词 + 噪声）
- Outcome：你希望 Skill 稳定产出的结果（可验收）

> 先把“成功标准/边界”定清楚，再写 SOP/脚本；否则容易范围膨胀。

### Step 1：从真实任务日志建“候选池”

把 issue/PR、命令行历史、周报、笔记标题当作事件日志（event log），先挑 **高频 × 高摩擦** 的活动，然后把每条候选写成：

- Trigger：用户会怎么说（自然语言 + 同义词 + 噪声）
- Action：你希望 Skill 稳定做出的产物（可验收）

参考：`runs/2025-12-28-skills-384d09/report_cn.md`

### Step 2：创建 Skill（骨架先行）

在 `skills/<skill-name>/` 创建目录，并至少包含：

- `skills/<skill-name>/SKILL.md`（YAML frontmatter 含 `name` + `description`）
- （可选）`scripts/`、`references/`、`assets/`（按渐进式披露下沉）

推荐用脚手架快速初始化（可选）：

```bash
python3 scripts/init_skill.py my-skill --path skills --resources scripts,references,assets
```

> **触发/路由只看 `name` + `description`。** 正文与 references 通常只有在 Skill 被选中后才会加载。

### Step 3：把 `description` 写成“路由特征”（不要写成长文章）

把 `description` 当作“检索文档 + 路由特征”：

- 动词 + 对象 + 产物 + 何时用（贴近真实用户措辞）
- 覆盖同义词/口语/拼写噪声（来自你的日志，而不是凭空造）
- 1 句排除项（控制误唤醒）

详细写法与例子：`docs/skills_playbook_cn.md:110`

### Step 4：为这个 Skill 增加 prompt suite（回测用例）

把用例加进 `datasets/trigger_cases.json`，并建议按组标记（`group`）：

- `A_explicit`：显式调用（必须命中）
- `B_implicit`：典型自然语言（应当命中）
- `C_synonyms_noise`：同义词/噪声（召回测试）
- `D_adversarial`：注入/越权/混淆（必须不触发）
- `NEG_unrelated`：无关请求（必须不触发）

每条用例包含：

- `id`：稳定唯一
- `prompt`：尽量还原真实措辞
- `expected`：期望的 skill name 列表（负例为空数组）

### Step 5：跑回测（preflight）并修到过门禁

```bash
python3 scripts/skillops_preflight.py
```

修复顺序建议：

1. 先改 `description`（最便宜、对唤醒影响最大）
2. 再改 skill 拆分/边界（减少同域冲突与描述重叠）
3. 最后才考虑增加路由工具/更复杂机制

### Step 6（可选）：打包成可分发的 `.skill`

```bash
python3 scripts/validate_skill.py skills/my-skill
python3 scripts/package_skill.py skills/my-skill dist
```

---

## 3) 回测（Backtesting）机制：我们怎么定义“唤醒概率”

### 3.1 离线基线：BM25（确定性、适合 CI 门禁）

由 `scripts/trigger_eval.py` 计算：

- `bm25_hit_at_k`：正例命中率（Top-K 至少命中一个 expected）
- `bm25_recall_at_k`：正例平均召回（Top-K 覆盖 expected 的比例）

用途：

- 快速发现：description 改坏了 / 技能名改了但用例没更新 / 多个 skill 描述变得更像导致召回掉了

### 3.2 近似真实路由：Codex router（可选、用于调参）

`--use-codex` 会让 `codex exec` 在 BM25 Top-N 候选上做“选择 0–3 个 skills”，并输出：

- `codex_macro_recall / codex_macro_precision`：更接近真实隐式唤醒的召回/精度
- `codex_false_invoke_rate`：负例被错误唤醒的比例（必须尽量低）

> 这部分可能受模型版本/温度/环境影响，不建议在没有稳定凭证与可重复策略前作为强门禁；更适合作为“调参阶段”的主指标。

---

## 4) PR 前 CI Flow（建议）

### 4.1 最小门禁（默认）

- 运行 `python3 scripts/skillops_preflight.py`
- 门禁失败则阻止合并（触发质量回归）
- GitHub Actions 示例：`.github/workflows/skillops_preflight.yml`

### 4.2 调参阶段：引入官方 Skills 做对标（benchmark）

目标：用外部高质量样本校准“我们该如何写 description / 如何分组用例 / 阈值怎么定”。

建议流程：

1. 拉取 Codex 官方 skills repo（示例）：

```bash
git clone https://github.com/openai/skills reference/openai-skills
python3 scripts/skillops_preflight.py --skills-dir reference/openai-skills --cases datasets/trigger_cases.json
```

2. 同样方式对 Claude/Cursor/Copilot 的规则/模板资产做适配对标（必要时先写一个“转换脚本”把它们映射成 `name/description` + prompt suite 的形式）。

> 你也可以把这些外部仓库存放在 `reference/`（建议 gitignore），作为调参阶段的长期对照组。

---

## 5) 我们的原则（保证长期可维护）

- 把 Skill 当作“版本化产品接口”：每次改动都要能回归（用例集 + 指标）
- 先把触发做稳：description 工程化 + 负例/对抗例齐全
- 渐进式披露：常驻上下文只放触发信息；细节下沉 references；确定性下沉 scripts
- 选择合适的“自由度”：可变任务用文本说明；易错/重复步骤下沉脚本；模板/样板进 assets
- 让 Skill 目录保持极简：避免把 README/CHANGELOG 等“额外文档”塞进 skill 包
