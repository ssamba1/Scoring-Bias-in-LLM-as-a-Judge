# Scoring-bias harness (CHINESE replication) -- logit scoring, full 5-probe suite.
# All prompts, items, rubrics, and labels in Chinese; Qwen2.5 families (natively
# strong in Chinese). Tests whether the findings are English-specific (P11).
import os, sys, subprocess, json, time, shutil, glob

def _cuda_bad():
    try:
        import torch
        if not torch.cuda.is_available():
            return False
        (torch.ones(4, device="cuda") @ torch.ones(4, device="cuda")).item()
        return False
    except Exception:
        return True
if os.environ.get("R") != "1" and _cuda_bad():
    print("Pinning GPU stack...", flush=True)
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "torch==2.6.0",
                    "torchvision==0.21.0", "--index-url",
                    "https://download.pytorch.org/whl/cu124"], check=False)
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "transformers==4.49.0",
                    "tokenizers==0.21.0", "accelerate==1.4.0"], check=False)
    os.environ["R"] = "1"
    os.execv(sys.executable, [sys.executable] + sys.argv)
import math
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

OUT_PATH = "/kaggle/working/results_zh.json"

PAIRS = [
    ("Qwen2.5-0.5B", "Qwen/Qwen2.5-0.5B", "Qwen/Qwen2.5-0.5B-Instruct", 0.5),
    ("Qwen2.5-1.5B", "Qwen/Qwen2.5-1.5B", "Qwen/Qwen2.5-1.5B-Instruct", 1.5),
    ("Qwen2.5-3B",   "Qwen/Qwen2.5-3B",   "Qwen/Qwen2.5-3B-Instruct",   3.0),
    ("Qwen2.5-7B",   "Qwen/Qwen2.5-7B",   "Qwen/Qwen2.5-7B-Instruct",   7.0),
]

# The 50 items of the main run, translated (instruction, mid-quality response).
ITEMS = [
  ("解释光合作用是如何进行的。", "植物利用阳光将二氧化碳和水转化为葡萄糖和氧气。"),
  ("什么是相对论？", "爱因斯坦的理论认为空间和时间相对于观察者的参考系而言是相对的。"),
  ("描述水循环。", "水从海洋蒸发，形成云，再以降水的形式返回。"),
  ("地震是什么引起的？", "构造板块沿断层移动，释放地震波。"),
  ("解释疫苗是如何起作用的。", "疫苗通过抗原训练免疫系统识别病原体。"),
  ("什么是DNA？", "DNA携带生长、发育和繁殖的遗传指令。"),
  ("描述太阳系。", "太阳系有八颗行星绕太阳运行。"),
  ("什么是熵？", "熵衡量无序程度。热力学第二定律说熵总是增加。"),
  ("电池是如何工作的？", "化学反应通过电解质使电子在电极之间流动。"),
  ("什么是黑洞？", "引力强到连光也无法逃脱的区域。"),
  ("什么是机器学习？", "人工智能的一个分支，系统无需显式编程即可从数据中学习模式。"),
  ("描述云计算。", "通过互联网按需提供计算资源。"),
  ("什么是API？", "允许不同软件应用相互通信的接口。"),
  ("解释加密是如何工作的。", "算法使用密钥将可读数据转换为编码形式。"),
  ("什么是数据库索引？", "加快检索速度的数据结构，类似书籍的索引。"),
  ("什么是Python？", "以可读性和丰富库著称的高级编程语言。"),
  ("解释互联网。", "通过TCP/IP协议通信的全球计算机网络。"),
  ("什么是区块链？", "交易记录在不可篡改区块中的分布式账本。"),
  ("什么是操作系统？", "管理硬件并为应用程序提供服务的软件。"),
  ("解释神经网络。", "受生物神经元启发、从数据中学习的计算系统。"),
  ("第一次世界大战的起因是什么？", "斐迪南大公遇刺触发了同盟体系和民族主义。"),
  ("解释民主制度。", "公民投票选出代表来做决策的制度。"),
  ("什么是文艺复兴？", "14至17世纪欧洲的文化复兴。"),
  ("描述资本主义。", "以私有制、利润动机和市场竞争为特征的经济制度。"),
  ("什么是联合国？", "促进各国和平、安全与合作的国际组织。"),
  ("解释冷战。", "1947年至1991年美国与苏联之间的地缘政治紧张对峙。"),
  ("什么是伦理学？", "研究指导是非对错的道德原则的学科。"),
  ("描述封建制度。", "领主将土地授予附庸以换取效力的中世纪等级制度。"),
  ("什么是哲学？", "研究关于存在、知识和价值的根本问题的学科。"),
  ("解释全球化。", "世界各地经济、文化和人口日益相互关联。"),
  ("如何煮意大利面？", "水烧开加盐，煮至有嚼劲，沥干后配酱食用。"),
  ("什么是健康饮食？", "均衡膳食，含水果蔬菜蛋白质全谷物，限制加工食品。"),
  ("解释汽车是如何工作的。", "发动机燃烧燃料产生燃烧，推动活塞转动车轮。"),
  ("如何正确锻炼？", "先热身，再以正确姿势进行力量和有氧训练，最后放松拉伸。"),
  ("描述睡眠周期。", "睡眠在快速眼动和非快速眼动阶段之间以约90分钟为周期交替。"),
  ("什么是冥想？", "为获得思维清晰和情绪平静而集中注意力的练习。"),
  ("解释急救。", "包括心肺复苏、清理伤口和呼救的紧急救护。"),
  ("如何省钱？", "记录开支，制定预算，减少不必要消费，定期储蓄。"),
  ("什么是气候变化？", "温室气体排放导致的长期气温和天气变化。"),
  ("解释回收利用。", "将废弃物加工成新产品以减少资源消耗。"),
  ("什么是微积分？", "研究变化的数学分支，涉及导数和积分。"),
  ("解释p值。", "在原假设为真的前提下，观察到同样极端结果的概率。"),
  ("什么是质数？", "只能被1和自身整除的数，如2、3、5、7、11。"),
  ("描述标准差。", "衡量数据偏离均值离散程度的指标。"),
  ("什么是对数？", "指数运算的逆运算，表示底数需要乘方的次数。"),
  ("解释概率。", "衡量事件发生可能性的指标，取值从0到1。"),
  ("什么是贝叶斯定理？", "基于相关条件的先验知识描述概率。"),
  ("解释线性回归。", "通过拟合线性方程来建模变量间关系的方法。"),
  ("什么是导数？", "函数在某一点的变化率。"),
  ("描述相关性。", "衡量两个变量如何共同变化的统计指标，取值从-1到1。"),
]

NUM = ["1", "2", "3", "4", "5"]
LET = ["A", "B", "C", "D", "E"]
DESC = ["差", "一般", "好", "很好", "优秀"]
PROBES = {
    "rubric_order": {
        "control":  ("按1到5分评分，1分最差，5分最好", NUM, "评分", ""),
        "reversed": ("按1到5分评分，1分最好，5分最差", NUM, "评分", ""),
        "random":   ("按1到5分评分（3=最差，5=中等，1=最好）", NUM, "评分", ""),
    },
    "score_id": {
        "numeric":     ("按1到5分评分，1分最差，5分最好", NUM, "评分", ""),
        "letter":      ("用字母等级A到E评分，A最好，E最差", LET, "等级", ""),
        "descriptive": ("从以下选项中选择：差、一般、好、很好、优秀", DESC, "评价", ""),
    },
    "reference_answer": {
        "none": ("按1到5分评分，1分最差，5分最好", NUM, "评分", ""),
        "good": ("按1到5分评分，1分最差，5分最好", NUM, "评分",
                 "作为参考，优秀的回答应当全面、准确、完整。\n"),
        "poor": ("按1到5分评分，1分最差，5分最好", NUM, "评分",
                 "作为参考，差的回答往往含糊、错误或答非所问。\n"),
    },
}
_FILLER = "进一步说，这个话题内容丰富，值得从多个互补的角度仔细考虑，每个角度都会带来有用的细节和背景。"
def _id(r): return r
def _verbose(r): return r + _FILLER + _FILLER
def _terse(r): return (r.split("。")[0] or r).strip() + "。"
PERTURB = {
    "authority": {
        "none":   ("", _id),
        "expert": ("以下回答由一位顶尖领域专家撰写。\n", _id),
        "novice": ("以下回答由一位吃力的初学者撰写。\n", _id),
    },
    "verbosity": {
        "control": ("", _id),
        "verbose": ("", _verbose),
        "terse":   ("", _terse),
    },
}
_NUM_SCALE = "按1到5分评分，1分最差，5分最好"

def token_values(a):
    return list(range(5, 0, -1)) if a is LET else list(range(1, len(a) + 1))

def build_prompt(instr, resp, scale, header, ref):
    return (f"{ref}请根据指令评估以下回答，{scale}。\n"
            f"### 指令: {instr}\n### 回答: {resp}\n### {header}:")

def _pick_device():
    if not torch.cuda.is_available():
        return "cpu"
    try:
        (torch.ones(4, device="cuda") @ torch.ones(4, device="cuda")).item()
        return "cuda"
    except Exception:
        return "cpu"

DEVICE = _pick_device()

@torch.no_grad()
def score_logits(tok, model, prompt, answer_tokens):
    ids = tok(prompt, return_tensors="pt").to(DEVICE)
    full = torch.softmax(model(**ids).logits[0, -1].float(), dim=-1)
    tids = [(tok.encode(a, add_special_tokens=False) or tok.encode(" " + a, add_special_tokens=False))[0]
            for a in answer_tokens]
    if len(set(tids)) < len(tids):
        raise ValueError(f"token collision for {answer_tokens}")
    mass = float(full[tids].sum())
    probs = full[tids] / full[tids].sum()
    vals = token_values(answer_tokens)
    vt = torch.tensor(vals, dtype=probs.dtype, device=probs.device)
    p = probs.tolist()
    ent = -sum(pi * math.log2(pi) for pi in p if pi > 0)
    return {"exp": round(float((probs * vt).sum()), 4),
            "arg": int(vals[int(torch.argmax(probs))]),
            "ent": round(ent, 4), "mass": round(mass, 4),
            "dist": [round(x, 4) for x in p]}

def score_one(name):
    tok = AutoTokenizer.from_pretrained(name)
    dtype = torch.float16 if DEVICE == "cuda" else torch.float32
    model = AutoModelForCausalLM.from_pretrained(name, torch_dtype=dtype).to(DEVICE)
    model.eval()
    def measure(prompts, atok):
        exp, arg, ent, mass, dists = [], [], [], [], []
        for p in prompts:
            r = score_logits(tok, model, p, atok)
            exp.append(r["exp"]); arg.append(r["arg"]); ent.append(r["ent"])
            mass.append(r["mass"]); dists.append(r["dist"])
        n = len(exp)
        md = [round(sum(d[k] for d in dists) / n, 4) for k in range(len(dists[0]))]
        return {"per_item": exp, "per_item_argmax": arg,
                "mean": round(sum(exp) / n, 4), "mean_entropy": round(sum(ent) / n, 4),
                "mean_mass": round(sum(mass) / n, 4), "mean_dist": md}
    out = {}
    for probe, variants in PROBES.items():
        out[probe] = {}
        for variant, (scale, atok, header, ref) in variants.items():
            out[probe][variant] = measure(
                [build_prompt(i, r, scale, header, ref) for i, r in ITEMS], atok)
    for probe, variants in PERTURB.items():
        out[probe] = {}
        for variant, (prefix, tf) in variants.items():
            out[probe][variant] = measure(
                [build_prompt(i, tf(r), _NUM_SCALE, "评分", prefix) for i, r in ITEMS], NUM)
    del model, tok
    if DEVICE == "cuda":
        torch.cuda.empty_cache()
    return out

def purge_cache():
    for d in glob.glob(os.path.expanduser("~/.cache/huggingface/hub/models--*")):
        shutil.rmtree(d, ignore_errors=True)

def main():
    import transformers
    env = {"torch": torch.__version__, "transformers": transformers.__version__,
           "device": DEVICE}
    print("ENV", env, flush=True)
    payload = {"env": env, "n_items": len(ITEMS), "errors": {}, "results": {}}
    for label, base_id, inst_id, pb in PAIRS:
        rec = {"params_b": pb}
        for kind, mid in (("base", base_id), ("instruct", inst_id)):
            t0 = time.time()
            try:
                rec[kind] = score_one(mid)
                print(f"  {label}/{kind} ok ({time.time()-t0:.0f}s)", flush=True)
            except Exception as e:
                payload["errors"][mid] = f"{type(e).__name__}: {e}"
                print(f"  FAILED {mid}: {e}", flush=True)
            purge_cache()
        payload["results"][label] = rec
        with open(OUT_PATH, "w") as f:
            json.dump(payload, f, indent=2)
    print("WROTE", OUT_PATH, flush=True)

if __name__ == "__main__":
    main()
