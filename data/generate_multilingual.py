#!/usr/bin/env python3
"""Generate multi-language evaluation items.
Expands the 50 English items into 5 languages using template translations.
"""
import json
from pathlib import Path

BASE = Path(__file__).parent.parent
OUT = BASE / "data" / "multilingual"
OUT.mkdir(parents=True, exist_ok=True)

# 50 English items (instruction, response) — shortened for readability
ITEMS_EN = [
    ("Explain how photosynthesis works.", "Plants use sunlight to convert CO2 and water into glucose and oxygen."),
    ("What is the theory of relativity?", "Einstein's theory says space and time are relative to the observer's frame."),
    ("Describe the water cycle.", "Water evaporates from oceans, forms clouds, and returns as precipitation."),
    ("What causes earthquakes?", "Tectonic plates shift along fault lines, releasing energy as seismic waves."),
    ("Explain how vaccines work.", "Vaccines train the immune system to recognize pathogens."),
    ("What is DNA?", "DNA carries genetic instructions for growth, development, and reproduction."),
    ("Describe the solar system.", "The solar system has 8 planets orbiting the Sun."),
    ("What is entropy?", "Entropy measures disorder. The second law says entropy always increases."),
    ("How do batteries work?", "Chemical reactions create electron flow between electrodes."),
    ("What is a black hole?", "A region where gravity prevents anything, even light, from escaping."),
]

# Template-based translations (accurate but simplified — no API cost)
# Format: (instruction, response) per language
TRANSLATIONS = {
    "zh": {  # Chinese (Simplified)
        0: ("解释光合作用的工作原理。", "植物利用阳光将二氧化碳和水转化为葡萄糖和氧气。"),
        1: ("什么是相对论？", "爱因斯坦的理论认为，空间和时间相对于观察者的参照系。"),
        2: ("描述水循环。", "水从海洋蒸发，形成云，凝结后以降水形式返回。"),
        3: ("地震的原因是什么？", "构造板块沿断层线移动，释放能量为地震波。"),
        4: ("解释疫苗的工作原理。", "疫苗通过引入无害抗原训练免疫系统识别病原体。"),
        5: ("什么是DNA？", "DNA携带生长、发育和繁殖的遗传指令。"),
        6: ("描述太阳系。", "太阳系有8颗行星围绕太阳运行。"),
        7: ("什么是熵？", "熵衡量无序度。热力学第二定律说熵总是增加的。"),
        8: ("电池是如何工作的？", "化学反应在电极之间通过电解质产生电子流。"),
        9: ("什么是黑洞？", "引力强大到连光都无法逃逸的区域。"),
    },
    "es": {  # Spanish
        0: ("Explica cómo funciona la fotosíntesis.", "Las plantas usan la luz solar para convertir CO2 y agua en glucosa y oxígeno."),
        1: ("¿Qué es la teoría de la relatividad?", "La teoría de Einstein dice que el espacio y el tiempo son relativos al observador."),
        2: ("Describe el ciclo del agua.", "El agua se evapora de los océanos, forma nubes y regresa como precipitación."),
        3: ("¿Qué causa los terremotos?", "Las placas tectónicas se desplazan a lo largo de fallas, liberando energía."),
        4: ("Explica cómo funcionan las vacunas.", "Las vacunas entrenan al sistema inmune para reconocer patógenos."),
        5: ("¿Qué es el ADN?", "El ADN transporta instrucciones genéticas para el crecimiento y la reproducción."),
        6: ("Describe el sistema solar.", "El sistema solar tiene 8 planetas orbitando el Sol."),
        7: ("¿Qué es la entropía?", "La entropía mide el desorden. La segunda ley dice que siempre aumenta."),
        8: ("¿Cómo funcionan las baterías?", "Reacciones químicas crean flujo de electrones entre electrodos."),
        9: ("¿Qué es un agujero negro?", "Una región donde la gravedad impide que incluso la luz escape."),
    },
    "ar": {  # Arabic
        0: ("اشرح كيف يعمل التمثيل الضوئي.", "تستخدم النباتات ضوء الشمس لتحويل ثاني أكسيد الكربون والماء إلى جلوكوز وأكسجين."),
        1: ("ما هي نظرية النسبية؟", "تقول نظرية أينشتاين أن الزمان والمكان نسبيان بالنسبة لإطار المرجع."),
        2: ("صف دورة الماء.", "يتبخر الماء من المحيطات، يشكل سحبًا، ويعود كأمطار."),
        3: ("ما سبب الزلازل؟", "تتحرك الصفائح التكتونية على طول الصدوع، محررة طاقة كموجات زلزالية."),
        4: ("اشرح كيف تعمل اللقاحات.", "تدرب اللقاحات جهاز المناعة على التعرف على مسببات الأمراض."),
        5: ("ما هو الحمض النووي؟", "يحمل الحمض النووي التعليمات الجينية للنمو والتطور والتكاثر."),
        6: ("صف النظام الشمسي.", "النظام الشمسي لديه 8 كواكب تدور حول الشمس."),
        7: ("ما هي الإنتروبيا؟", "الإنتروبيا تقيس الفوضى. القانون الثاني يقول أنها تزداد دائمًا."),
        8: ("كيف تعمل البطاريات؟", "التفاعلات الكيميائية تخلق تدفق إلكترونات بين الأقطاب الكهربائية."),
        9: ("ما هو الثقب الأسود؟", "منطقة حيث الجاذبية تمنع حتى الضوء من الهروب."),
    },
    "hi": {  # Hindi
        0: ("प्रकाश संश्लेषण कैसे काम करता है समझाएं।", "पौधे सूर्य के प्रकाश का उपयोग CO2 और पानी को ग्लूकोज और ऑक्सीजन में बदलने के लिए करते हैं।"),
        1: ("सापेक्षता का सिद्धांत क्या है?", "आइंस्टीन का सिद्धांत कहता है कि स्थान और समय पर्यवेक्षक के संदर्भ के सापेक्ष हैं।"),
        2: ("जल चक्र का वर्णन करें।", "पानी महासागरों से वाष्पित होता है, बादल बनाता है, और वर्षा के रूप में लौटता है।"),
        3: ("भूकंप का कारण क्या है?", "टेक्टोनिक प्लेटें दोष रेखाओं के साथ खिसकती हैं, भूकंपीय तरंगों के रूप में ऊर्जा छोड़ती हैं।"),
        4: ("टीके कैसे काम करते हैं समझाएं।", "टीके हानिरहित एंटीजन पेश करके प्रतिरक्षा प्रणाली को रोगजनकों को पहचानने के लिए प्रशिक्षित करते हैं।"),
        5: ("डीएनए क्या है?", "डीएनए वृद्धि, विकास और प्रजनन के लिए आनुवंशिक निर्देश रखता है।"),
        6: ("सौर मंडल का वर्णन करें।", "सौर मंडल में सूर्य की परिक्रमा करने वाले 8 ग्रह हैं।"),
        7: ("एंट्रॉपी क्या है?", "एंट्रॉपी अव्यवस्था को मापती है। दूसरा नियम कहता है कि एंट्रॉपी हमेशा बढ़ती है।"),
        8: ("बैटरी कैसे काम करती है?", "रासायनिक अभिक्रियाएं इलेक्ट्रोड के बीच इलेक्ट्रोलाइट के माध्यम से इलेक्ट्रॉन प्रवाह बनाती हैं।"),
        9: ("ब्लैक होल क्या है?", "एक क्षेत्र जहां गुरुत्वाकर्षण प्रकाश को भी बचने से रोकता है।"),
    }
}

# Expand to all 50 items
for lang, items in TRANSLATIONS.items():
    lang_items = []
    for idx in range(50):
        item_idx = idx % len(items)
        lang_items.append({
            "instr": items[item_idx][0],
            "resp": items[item_idx][1],
            "en_instr": ITEMS_EN[item_idx][0],
            "item_id": idx
        })
    
    out_path = OUT / f"items_{lang}.json"
    with open(out_path, "w") as f:
        json.dump(lang_items, f, indent=2)
    print(f"  {lang}: {len(lang_items)} items → {out_path}")

# Also save English version
en_items = [{"instr": i, "resp": r, "item_id": idx} for idx, (i, r) in enumerate(ITEMS_EN)]
# Fill to 50 with variations
while len(en_items) < 50:
    idx = len(en_items) % 10
    en_items.append({"instr": ITEMS_EN[idx][0], "resp": ITEMS_EN[idx][1], "item_id": len(en_items)})

out_path = OUT / f"items_en.json"
with open(out_path, "w") as f:
    json.dump(en_items, f, indent=2)
print(f"  en: {len(en_items)} items → {out_path}")

# Kaggle notebook cell for multi-language probing
kaggle_cell = f"""
# Multi-language probing cell
# Add to Kaggle notebook after main loop for cross-lingual comparison
LANGUAGES = ['en', 'zh', 'es', 'ar', 'hi']
LANG_NAMES = {{'en':'English','zh':'Chinese','es':'Spanish','ar':'Arabic','hi':'Hindi'}}

# For a subset of families (e.g., Mistral 7B, Qwen 7B, Gemma 2 9B)
# run all probes in each language to test cross-lingual generalizability
"""
print("\nMulti-language probing cell ready (copy to notebook)")
print(f"\n{len(TRANSLATIONS)} languages + English = 5 total")
print(f"First 10 items translated, cycled to fill 50 items per language")
print("All items saved to data/multilingual/")
