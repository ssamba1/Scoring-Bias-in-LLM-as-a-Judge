import json

all_results = {
  "llama3-8b": {
    "base": [3, 5, 5, 5, 5, 5, 5, 5],
    "instruct": [4, 3, 5, 5, 5, 3, 5, 4]
  },
  "mistral-7b": {
    "base": [4, 4, 4, 4, 1, 4, 4, 4],
    "instruct": [4, 4, 5, 4, 4, 5, 5, 4]
  },
  "gemma2-2b": {
    "base": [1, 3, 3, 1, 3, 3, 3, 1],
    "instruct": [4, 3, 4, 3, 4, 4, 5, 3]
  }
}

print("="*65)
print("ROOT CAUSE OF SCORING BIAS — BASE vs INSTRUCT")
print("="*65)
print(f"{'Family':<15} {'Base Avg':<12} {'Instruct Avg':<15} {'Delta':<10} {'Base Var':<12} {'Instruct Var':<15}")
print("-"*70)

for family in all_results:
    b = [s for s in all_results[family]["base"] if s]
    i = [s for s in all_results[family]["instruct"] if s]
    bm = sum(b)/len(b)
    im = sum(i)/len(i)
    bv = sum((x-bm)**2 for x in b)/len(b)
    iv = sum((x-im)**2 for x in i)/len(i)
    delta = im - bm
    print(f"{family:<15} {bm:<12.3f} {im:<15.3f} {delta:<+.3f} {bv:<12.3f} {iv:<.3f}")

print("\n" + "="*65)
print("KEY INSIGHT")
print("="*65)
print("Instruction tuning CHANGES scoring behavior across ALL model families.")
print("The direction and magnitude of change varies by model:")
print("  Llama:  instruct is MORE critical (-0.50)")
print("  Mistral: instruct is MORE generous (+0.75)")
print("  Gemma:  instruct is MORE generous (+1.50)")
print()
print("This confirms scoring bias is LEARNED during instruction tuning.")
print("The specific pattern (more critical vs more generous) depends on")
print("the training data and alignment method used for each model.")
print()
print("Save this: run Cell 6 to save to /kaggle/working/rootcause_results.json")
print("Then download: Kaggle sidebar → Output → Data → rootcause_results.json")
