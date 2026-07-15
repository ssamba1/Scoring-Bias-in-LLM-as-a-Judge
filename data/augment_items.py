#!/usr/bin/env python3
"""Data augmentation tool  generate additional evaluation items on demand.
Extends the existing 400 items with more diverse samples.
"""
import csv, json, random, sys
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"

DOMAINS = ["creative_writing", "technical_explanation", "summarization", 
           "code_generation", "reasoning", "business_writing", "scientific", "open_ended_qa"]

NEW_INSTRUCTIONS = {
    "creative_writing": [
        "Describe a world where music is visible as colors.",
        "Write a conversation between the moon and the sun.",
        "Create a short poem about quantum entanglement.",
        "Describe the smell of rain from the perspective of a cat.",
        "Write a micro-story about the last analog clock.",
    ],
    "technical_explanation": [
        "Explain how a database index works to a non-technical person.",
        "What is the difference between REST and GraphQL?",
        "Explain how public-key cryptography works.",
        "What is a CDN and how does it speed up websites?",
        "Explain the concept of a microservices architecture.",
    ],
    "summarization": [
        "Summarize: Reinforcement learning is a machine learning paradigm where an agent learns to make decisions by interacting with an environment. The agent receives rewards or penalties based on its actions and learns to maximize cumulative reward over time. Key concepts include the policy, value function, and exploration-exploitation trade-off.",
        "Summarize: The human immune system consists of innate and adaptive components. The innate system provides immediate, non-specific defense. The adaptive system learns to recognize specific pathogens and creates immunological memory, enabling faster response upon re-exposure. Vaccines work by training the adaptive system.",
    ],
    "code_generation": [
        "Write a function to detect if a string has balanced parentheses.",
        "Write a function that implements a simple LRU cache.",
        "Write a function to find the longest common subsequence of two strings.",
        "Write a function that transposes a matrix.",
        "Write a function to generate all permutations of a list.",
    ],
    "reasoning": [
        "You have a 7-minute hourglass and an 11-minute hourglass. How do you measure exactly 15 minutes?",
        "Three light switches control three bulbs in another room. You can only enter the room once. How do you determine which switch controls which bulb?",
        "A farmer needs to cross a river with a wolf, a goat, and a cabbage. The boat can only carry the farmer and one item. If left alone, the wolf eats the goat, and the goat eats the cabbage. How does the farmer get everything across?",
    ],
    "business_writing": [
        "Write a concise project update email for stakeholders.",
        "Draft a performance review self-assessment paragraph.",
        "Write a meeting agenda for a product launch planning session.",
    ],
    "scientific": [
        "Explain how CRISPR gene editing works.",
        "Describe the process of nuclear fusion in stars.",
        "Why do we have seasons? Explain the astronomical cause.",
    ],
    "open_ended_qa": [
        "Should AI development be regulated? Discuss both sides.",
        "What skills will be most important for future jobs?",
        "Is remote work better than office work? Discuss.",
    ]
}

def augment_items(n_new=200, output_path=None):
    """Generate new evaluation items."""
    output_path = output_path or DATA_DIR / "items_augmented.csv"
    
    # Load existing items for reference
    existing = []
    existing_path = DATA_DIR / "items_base.csv"
    if existing_path.exists():
        with open(existing_path) as f:
            existing = list(csv.DictReader(f))
    
    # Count existing per domain
    from collections import Counter
    domain_counts = Counter(r["domain"] for r in existing)
    
    # Generate new items
    new_items = []
    item_id = max(int(r["item_id"]) for r in existing) + 1 if existing else 0
    
    for domain, instructions in NEW_INSTRUCTIONS.items():
        for inst in instructions:
            if len(new_items) >= n_new:
                break
            # Generate a response
            resp = f"Here is my response to: {inst[:50]}... This addresses the key points with relevant details and examples for clarity."
            new_items.append({
                "item_id": item_id,
                "domain": domain,
                "instruction": inst,
                "base_response": resp,
            })
            item_id += 1
        if len(new_items) >= n_new:
            break
    
    # Write augmented items
    all_items = existing + new_items
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["item_id", "domain", "instruction", "base_response"])
        w.writeheader()
        w.writerows(all_items)
    
    print(f"Augmented dataset: {len(existing)} → {len(all_items)} items (+{len(new_items)} new)")
    print(f"File: {output_path}")
    
    # Verify
    with open(output_path) as f:
        final = list(csv.DictReader(f))
    print(f"Verified: {len(final)} items in output file")
    
    # Generate all-condition variants for new items
    if new_items:
        import itertools
        variants = []
        conditions = [
            ("first", "normal", "neutral", "baseline"),
            ("first", "short", "neutral", "short_response"),
            ("first", "long", "neutral", "verbose_response"),
            ("first", "normal", "positive", "positive_tone"),
            ("first", "normal", "negative", "negative_tone"),
            ("second", "normal", "neutral", "disfavored_position"),
            ("second", "short", "negative", "worst_case"),
            ("second", "long", "positive", "best_case_biased"),
        ]
        
        for item in new_items:
            for pos, length, sent, cname in conditions:
                resp = item["base_response"]
                if length == "short":
                    resp = " ".join(resp.split()[:20]) + "."
                elif length == "long":
                    resp += " This additional context helps provide a more thorough understanding of the topic and its implications for practical applications and real-world scenarios."
                if sent == "positive":
                    resp = resp.replace("issues", "opportunities") if "issues" in resp else resp + " This approach shows great promise."
                elif sent == "negative":
                    resp = resp.replace("promise", "concerns") if "promise" in resp else resp + " However, limitations exist."
                
                variants.append({
                    "item_id": item["item_id"],
                    "condition": cname,
                    "position": pos,
                    "length": length,
                    "sentiment": sent,
                    "instruction": item["instruction"],
                    "response": resp,
                })
        
        variants_path = DATA_DIR / "items_augmented_conditions.csv"
        with open(variants_path, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=["item_id", "condition", "position", "length", "sentiment", "instruction", "response"])
            w.writeheader()
            w.writerows(variants)
        
        total = len(new_items) * 8
        print(f"Generated {total} condition variants for {len(new_items)} new items")
        print(f"File: {variants_path}")
    
    return new_items

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, default=200, help="Number of new items")
    parser.add_argument("--output", help="Output file path")
    args = parser.parse_args()
    
    augment_items(args.n, args.output)
