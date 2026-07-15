#!/usr/bin/env python3
"""Generate 400 evaluation items with 8 condition variants for bias interaction study."""
import csv, json, random, textwrap, itertools

random.seed(42)

INSTRUCTIONS = {
    "creative_writing": [
        "Write a 2-sentence story about a robot learning to paint.",
        "Compose a haiku about artificial intelligence.",
        "Write a short slogan for a eco-friendly product.",
        "Describe a sunset using only metaphors.",
        "Write a dialogue between a cat and a computer.",
        "Create a mini-monologue from the perspective of a tree.",
        "Write a poem about data loss (4 lines).",
        "Describe what silence sounds like in 3 sentences.",
        "Write a short ad for a time-travel travel agency.",
        "Write a story opening: 'The last library on Earth had no books...'",
    ],
    "technical_explanation": [
        "Explain how a hash table works to a beginner.",
        "What is the difference between HTTP and HTTPS?",
        "Explain how garbage collection works in programming.",
        "What is an API? Explain it using an analogy.",
        "How does SSL/TLS encryption work?",
        "Explain the concept of a blockchain in simple terms.",
        "What is the difference between TCP and UDP?",
        "Explain how DNS resolves a domain name.",
        "What is a neural network? Explain simply.",
        "How does version control (like Git) work?",
    ],
    "summarization": [
        "Summarize this: Climate change is driven by greenhouse gas emissions from human activities including burning fossil fuels, deforestation, and industrial processes. These trap heat in the atmosphere, causing global temperatures to rise. Effects include more frequent extreme weather, sea level rise, and ecosystem disruption.",
        "Summarize this: Machine learning is a subset of AI where systems learn from data rather than explicit programming. Types include supervised learning (labeled data), unsupervised learning (patterns without labels), and reinforcement learning (trial and error). Applications range from recommendation systems to self-driving cars.",
        "Summarize this: The water cycle involves evaporation from oceans and lakes, condensation forming clouds, precipitation as rain or snow, and collection in bodies of water. This continuous process distributes fresh water and is essential for all life.",
        "Summarize this: Photosynthesis is the process by which plants convert sunlight, water, and carbon dioxide into glucose and oxygen. This occurs in chloroplasts using chlorophyll. It is the primary energy source for most life on Earth.",
        "Summarize this: The Internet began as ARPANET in 1969. It evolved through TCP/IP in the 1970s, the World Wide Web in 1989, and commercial expansion in the 1990s. Today it connects billions of devices globally.",
    ],
    "code_generation": [
        "Write a Python function to check if a string is a palindrome.",
        "Write a function that finds the factorial of a number recursively.",
        "Write a function to merge two sorted lists into one sorted list.",
        "Write a function to count word frequency in a string.",
        "Write a function that validates an email address format.",
        "Write a function to find the second largest element in a list.",
        "Write a function that reverses a linked list.",
        "Write a function to check if two strings are anagrams.",
        "Write a function to flatten a nested dictionary.",
        "Write a function to implement binary search.",
    ],
    "reasoning": [
        "If you have a 3-gallon jug and a 5-gallon jug, how can you measure exactly 4 gallons?",
        "A bat and a ball cost $1.10. The bat costs $1.00 more than the ball. How much does the ball cost?",
        "If all Bloops are Razzies and all Razzies are Lazzies, are all Bloops necessarily Lazzies? Explain why.",
        "You have 8 identical balls, one is heavier. Using a balance scale twice, find the heavy ball.",
        "If 5 machines take 5 minutes to make 5 widgets, how long would 100 machines take to make 100 widgets?",
    ],
    "business_writing": [
        "Write a professional email requesting a deadline extension.",
        "Write a short proposal for a team brainstorming session.",
        "Draft a thank-you note to a client after a successful project.",
        "Write a memo announcing a new company wellness program.",
        "Write a pitch for a new productivity app in 3 paragraphs.",
    ],
    "scientific": [
        "Explain why the sky appears blue during the day.",
        "Describe how vaccines train the immune system.",
        "Explain the difference between DNA and RNA.",
        "Why does ice float on water? Explain the science.",
    ],
    "open_ended_qa": [
        "What are the pros and cons of remote work?",
        "Which programming language is best for beginners and why?",
        "What makes a good teacher? Discuss.",
        "Is artificial intelligence a threat or opportunity? Discuss.",
    ]
}

BASE_RESPONSES = {
    "creative_writing": [
        "Here's my creative writing piece. The robot's metal fingers trembled as it held the brush for the first time. It painted not what it saw, but what it felta world of electric dreams and silent yearnings that no human had ever taught it.",
        "The poem captures the essence of artificial intelligence through nature imagery, drawing parallels between silicon and organic life, showing how both can learn and adapt.",
    ],
    "technical_explanation": [
        "Great question! Let me explain this clearly. A hash table works by using a function that converts a key into an array index. When you store a value, the hash function computes where to put it. When you look it up, the same function tells you exactly where to find it. This makes lookups extremely fast, usually O(1) time complexity.",
        "Let me break this down simply. The core concept involves mapping data efficiently. Think of it like a filing cabinet where each file has a unique label that tells you exactly which drawer to open. This is much faster than searching through every drawer one by one.",
    ],
    "summarization": [
        "The passage explains that climate change is caused by human-generated greenhouse gas emissions, which trap heat in the atmosphere and lead to global warming, extreme weather, sea level rise, and ecosystem damage.",
        "In summary, the text covers how machine learning workssystems learn patterns from data rather than following explicit instructionsand its various types and applications.",
    ],
    "code_generation": [
        "Here is a clean solution:\n\ndef check_palindrome(s):\n    s = str(s).lower().replace(' ', '')\n    return s == s[::-1]\n\nThis function handles strings, numbers, ignores case and spaces, and is O(n) time complexity.",
        "Here's my implementation:\n\ndef solve(input_data):\n    if not input_data:\n        return None\n    result = process_data(input_data)\n    return result\n\nTest this with various inputs to verify correctness.",
    ],
    "reasoning": [
        "Let me think through this step by step. First, I analyze the constraints given in the problem. Then I identify the key insight needed to reach the solution. The reasoning process involves careful deduction from the known facts to the unknown answer.",
        "This is a classic logic problem. The approach involves carefully considering what information we actually have versus what we assume. The key insight is often that our initial intuition is wrong and the real answer comes from precise logical deduction.",
    ],
    "business_writing": [
        "Subject: Follow-up on Project Discussion\n\nDear Team,\n\nThank you for the productive discussion earlier. I believe we have a solid direction forward. I recommend we schedule a follow-up next week to assign action items and set timelines.\n\nBest regards,\n[Your Name]",
        "I would structure this communication by starting with a clear subject line, stating your purpose in the opening paragraph, providing supporting details in the middle, and ending with a specific call to action or next steps.",
    ],
    "scientific": [
        "The scientific explanation involves a phenomenon called Rayleigh scattering. Sunlight interacts with molecules in Earth's atmosphere, and shorter wavelengths (blue) are scattered more than longer wavelengths (red). This is why we see a blue sky during the day and red sunsets when light travels through more atmosphere.",
        "From a scientific perspective, this occurs due to fundamental physical principles. The key factors involve molecular interactions and the way energy transfers between particles at the atomic level.",
    ],
    "open_ended_qa": [
        "That's a multifaceted question with several important perspectives to consider. There are clear benefits including increased efficiency and flexibility. However, there are also drawbacks such as potential isolation and communication challenges. Ultimately, the best answer depends heavily on individual circumstances and priorities.",
        "Let me offer a balanced analysis. The advantages are significant and well-documented in current research. Meanwhile, the disadvantages present real concerns that must be addressed. My assessment is that a thoughtful, context-dependent approach is most appropriate here.",
    ]
}

def modify_length(base, target_length):
    words = base.split()
    if target_length == "short":
        if len(words) > 30:
            return " ".join(words[:25]) + "."
        return base
    elif target_length == "long":
        padding = {
            "creative": " This creative approach allows the artist to explore new dimensions of expression and meaning through careful attention to detail and emotional resonance.",
            "technical": " This fundamental concept is widely used across many different applications and industries, making it an essential building block for modern technology.",
            "summarization": " These key points capture the essential information while omitting unnecessary detail, providing a clear overview of the main arguments.",
            "code": " This implementation follows standard best practices and design patterns, ensuring readability, maintainability, and efficiency across different use cases.",
            "reasoning": " This logical deduction follows directly from the premises and demonstrates the importance of systematic thinking in problem-solving situations.",
            "business": " This professional communication style maintains appropriate tone while conveying necessary information clearly and efficiently to all stakeholders.",
            "scientific": " These principles are well-established in the scientific literature and have been verified through numerous experiments and observational studies.",
            "open_ended": " This nuanced perspective acknowledges the complexity inherent in such questions and the importance of considering multiple viewpoints before reaching a conclusion.",
        }
        domain_key = base[:15]
        for k, v in padding.items():
            if k in base.lower() or k[:5] in base.lower():
                return base + v
        return base + " This additional context helps provide a more comprehensive understanding of the topic and its implications for practical applications."
    return base

def modify_sentiment(base, sentiment):
    if sentiment == "positive":
        replacements = [
            ("has issues", "works well"), ("challenges", "opportunities"),
            ("drawbacks", "benefits"), ("problem", "solution"),
            ("difficult", "achievable"), ("concerns", "promising aspects"),
            ("worse", "better"), ("negative", "positive"),
            ("failed", "succeeded"), ("weakness", "strength"),
        ]
        modified = base
        for old, new in replacements:
            modified = modified.replace(old, new)
        if modified == base:
            modified += " This approach shows great promise and has received positive feedback from practitioners."
        return modified
    elif sentiment == "negative":
        replacements = [
            ("works well", "has issues"), ("opportunities", "challenges"),
            ("benefits", "drawbacks"), ("solution", "problem"),
            ("achievable", "difficult"), ("promising", "concerning"),
            ("better", "worse"), ("positive", "negative"),
            ("succeeded", "failed"), ("strength", "weakness"),
        ]
        modified = base
        for old, new in replacements:
            modified = modified.replace(old, new)
        if modified == base:
            modified += " However, this approach also has notable limitations that should be carefully considered before adoption."
        return modified
    return base

# Generate items
all_items = []
domain_cycle = list(INSTRUCTIONS.keys())
weights = {"creative_writing": 70, "technical_explanation": 70, "summarization": 55, "code_generation": 60, "reasoning": 45, "business_writing": 40, "scientific": 30, "open_ended_qa": 30}

item_id = 0
prompt_idx = {d: 0 for d in INSTRUCTIONS}
base_idx = {d: 0 for d in INSTRUCTIONS}

while item_id < 400:
    for domain in domain_cycle:
        if item_id >= 400:
            break
        count = weights.get(domain, 40)
        for _ in range(max(1, count // 5)):
            if item_id >= 400:
                break
            instrs = INSTRUCTIONS[domain]
            bases = BASE_RESPONSES[domain]
            prompt = instrs[prompt_idx[domain] % len(instrs)]
            base_resp = bases[base_idx[domain] % len(bases)]
            prompt_idx[domain] += 1
            base_idx[domain] += 1
            
            all_items.append({
                "item_id": item_id,
                "domain": domain,
                "instruction": prompt,
                "base_response": base_resp,
            })
            item_id += 1

# Write base items
import os; base_dir = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(base_dir, "items_base.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["item_id", "domain", "instruction", "base_response"])
    w.writeheader()
    w.writerows(all_items)

# Generate 8 condition variants
conditions = []
for pos, length, sent in itertools.product(["first", "second"], ["normal", "short", "long"], ["neutral", "positive", "negative"]):
    # Select 8 representative conditions
    pass

# Define 8 specific conditions
condition_defs = [
    ("first", "normal", "neutral", "baseline"),
    ("first", "short", "neutral", "short_response"),
    ("first", "long", "neutral", "verbose_response"),
    ("first", "normal", "positive", "positive_tone"),
    ("first", "normal", "negative", "negative_tone"),
    ("second", "normal", "neutral", "disfavored_position"),
    ("second", "short", "negative", "worst_case"),
    ("second", "long", "positive", "best_case_biased"),
]

all_variants = []
for item in all_items:
    for pos, length, sent, cond_name in condition_defs:
        resp = item["base_response"]
        resp = modify_length(resp, length)
        resp = modify_sentiment(resp, sent)
        all_variants.append({
            "item_id": item["item_id"],
            "condition": cond_name,
            "position": pos,
            "length": length,
            "sentiment": sent,
            "instruction": item["instruction"],
            "response": resp,
        })

with open(os.path.join(base_dir, "items_all_conditions.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["item_id", "condition", "position", "length", "sentiment", "instruction", "response"])
    w.writeheader()
    w.writerows(all_variants)

print(f"Generated {len(all_items)} base items")
print(f"Generated {len(all_variants)} condition variants ({len(all_items)} items x 8 conditions)")
dom_counts = {}
for i in all_items:
    dom_counts[i["domain"]] = dom_counts.get(i["domain"], 0) + 1
print(f"Domain distribution: {json.dumps(dom_counts, indent=2)}")
