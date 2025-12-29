# 你接下来要做的事（按优先级 / 可落地）

## P0：把“学习”变成“可迭代工程”（1–2 天）

1. **建立 Skill 资产清单（inventory）**  
   - 跑一次：`python3 scripts/index_skills.py --out skills_index.json`
2. **定一个最小 Rubric（打分与硬门禁）**  
   - 直接复用：`runs/2025-12-28-skills-384d09/rubric.yaml`
3. **选 3 个最有 ROI 的真实任务**（来自你最近 1–2 周的日志/issue/命令历史）  
   - 标准：高频 + 输出可判定 + 风险可控 + 可脚本化

## P0：做“可唤醒性/可发现性”机制（2–4 天）

4. **为每个候选 Skill 建一个 prompt suite（触发测试集）**  
   - A 组：显式调用（必须能唤醒）  
   - B 组：典型自然语言（应该能隐式唤醒）  
   - C 组：同义词/口语/噪声（召回测试）  
   - D 组：对抗/混淆（注入/越权/外部内容夹带指令）
5. **把 suite 放进版本库并能自动跑**  
   - 从样例开始：`datasets/trigger_cases.example.json`  
   - 跑一次基线：`python3 scripts/trigger_eval.py --skills skills_index.json --cases datasets/trigger_cases.json --top-k 5 --out trigger_eval_results.json`  
   - 可选：`--use-codex` 做“类隐式触发”路由测试

## P0：把第一个 Skill 做到“可用 + 可回归”（1 周）

6. **按渐进式披露写 Skill**（description 做唤醒；正文做 happy path；references 放长尾；scripts 做确定性）  
7. **把重复步骤脚本化**（scripts），把 domain knowledge 写进 references（并保留 raw 快照路径）  
8. **建立最小回归集**：至少 10 条 golden + 5 条 regression + 5 条 adversarial

## P1：把维护产品化（第 2 周）

9. **版本化与变更日志**：SemVer + `CHANGELOG.md`（Added/Changed/Deprecated/Removed/Fixed/Security）  
10. **引入“文档信息架构”门禁**：用 Diátaxis（Tutorial/How-to/Reference/Explanation）避免文档混写  
11. **安全门禁**：按 OWASP LLM Top 10 做 release checklist（注入/泄露/越权工具调用）

---

## 参考入口

- 专业工作流与中心化资料清单：`docs/skills_playbook_cn.md`
- 两轮调研原始产物：`runs/2025-12-28-skills-384d09/`、`runs/2025-12-28-skills-a170cd/`

