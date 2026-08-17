"""
按 PIE Issue Type 分组，对高频类（工单数 >= MIN_COUNT）用 DeepSeek 提炼共性，
生成标准解决流程 SOP，并写回该类下所有工单的 SOP 字段。
带断点：SOP 生成结果缓存在 sop_generated.json，写入进度记录在 sop_write_progress.json。
"""
import sys, io, json, os, time, requests
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
except Exception:
    pass
import feishu_api
import config

MIN_COUNT = 5
DATA = r"C:\Users\Admin\AppData\Local\Temp\claude\E--Claude\fb587855-2309-4e41-b779-1c9ad610140b\scratchpad\sop_data.json"
GEN_CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sop_generated.json")
PROGRESS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sop_write_progress.json")

SOP_PROMPT = """你是Mammotion（割草机器人）售后技术支持的SOP编写专家。
下面给你同一问题类型「{issue}」的多个真实工单，每条含：问题概述、故障现象、已采取的解决方案。
请你归纳这些工单的【共性处理路径】，提炼出一份标准化解决流程SOP。

要求：
- 用简洁的中文编号步骤（1. 2. 3. ...），一般 3-6 步
- 步骤要精准、可执行，体现"先查什么→再做什么→仍不行怎么处理"的排查逻辑
- 只保留这类问题的通用流程，去掉个别工单的特例细节
- 面向售后工程师，措辞专业简练
- 只输出SOP步骤本身，不要任何前言、解释或标题
"""


def distill(issue, items):
    samples = []
    for r in items[:25]:
        block = ""
        if r["pie"]:
            block += "问题: " + r["pie"][:200] + "\n"
        if r["symptom"]:
            block += "现象: " + r["symptom"] + "\n"
        if r["sol"]:
            block += "解决: " + r["sol"][:400] + "\n"
        if block.strip():
            samples.append(block.strip())
    user = "\n---\n".join(samples)
    resp = requests.post(
        config.DEEPSEEK_BASE_URL + "/chat/completions",
        headers={"Authorization": "Bearer " + config.DEEPSEEK_API_KEY, "Content-Type": "application/json"},
        json={"model": "deepseek-chat",
              "messages": [{"role": "system", "content": SOP_PROMPT.replace("{issue}", issue)},
                           {"role": "user", "content": user[:12000]}],
              "temperature": 0.3},
        timeout=120,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"].strip()


def main():
    with open(DATA, encoding="utf-8") as f:
        rows = json.load(f)

    from collections import defaultdict
    groups = defaultdict(list)
    for r in rows:
        if r["issue"]:
            groups[r["issue"]].append(r)

    qualifying = {k: v for k, v in groups.items() if len(v) >= MIN_COUNT}
    print(f"符合条件的问题类型（>= {MIN_COUNT} 条）：{len(qualifying)} 个，"
          f"覆盖 {sum(len(v) for v in qualifying.values())} 条工单\n")

    # ── 生成阶段（带缓存）──
    generated = {}
    if os.path.exists(GEN_CACHE):
        with open(GEN_CACHE, encoding="utf-8") as f:
            generated = json.load(f)

    for issue, items in sorted(qualifying.items(), key=lambda x: -len(x[1])):
        if issue in generated:
            print(f"[缓存] {issue}")
            continue
        print(f"[生成] {issue} ({len(items)} 条) ...")
        try:
            sop = distill(issue, items)
            generated[issue] = sop
            with open(GEN_CACHE, "w", encoding="utf-8") as f:
                json.dump(generated, f, ensure_ascii=False, indent=2)
            print("  " + sop.replace("\n", "\n  ")[:300] + " ...")
        except Exception as e:
            print(f"  生成失败: {e}")
        time.sleep(0.3)

    # ── 写入阶段（带进度）──
    done = set()
    if os.path.exists(PROGRESS):
        with open(PROGRESS, encoding="utf-8") as f:
            done = set(json.load(f))

    print(f"\n开始写入 SOP 字段 ...")
    written = 0
    for issue, items in qualifying.items():
        sop = generated.get(issue)
        if not sop:
            continue
        for r in items:
            rid = r["rid"]
            if rid in done:
                continue
            res = feishu_api.update_record(rid, {"SOP": sop})
            if res.get("code") == 0:
                done.add(rid)
                written += 1
                if written % 20 == 0:
                    with open(PROGRESS, "w", encoding="utf-8") as f:
                        json.dump(sorted(done), f)
                    print(f"  已写入 {written} 条 ...")
            else:
                print(f"  写入失败 {r['ref']}: {res.get('msg')}")
            time.sleep(0.12)

    with open(PROGRESS, "w", encoding="utf-8") as f:
        json.dump(sorted(done), f)

    print(f"\n完成：生成 {len(generated)} 份 SOP，写入 {written} 条工单")


if __name__ == "__main__":
    main()
