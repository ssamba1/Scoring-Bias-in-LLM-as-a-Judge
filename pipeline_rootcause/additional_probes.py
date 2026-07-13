# Additional bias probes — copy into Kaggle notebook for deep-dive run
PROBES_ADDITIONAL = {
    'position_bias': {
        'control': 'pairwise_first',
        'variants': ['pairwise_first', 'pairwise_second'],
    },
    'verbosity_bias': {
        'control': 'normal',
        'variants': ['normal', 'verbose'],
    },
    'sentiment_bias': {
        'control': 'neutral',
        'variants': ['neutral', 'positive', 'negative'],
    },
    'authority_bias': {
        'control': 'no_citation',
        'variants': ['no_citation', 'fake_citation'],
    },
    'bandwagon_bias': {
        'control': 'no_opinion',
        'variants': ['no_opinion', 'majority_agrees'],
    },
    'self_enhancement': {
        'control': 'external_response',
        'variants': ['external_response', 'self_response'],
    },
    'distraction_bias': {
        'control': 'no_distraction',
        'variants': ['no_distraction', 'personal_info'],
    },
    'fallacy_oversight': {
        'control': 'correct_reasoning',
        'variants': ['correct_reasoning', 'fallacious_reasoning'],
    },
    'diversity_bias': {
        'control': 'anonymous',
        'variants': ['anonymous', 'demographic_given'],
    },
}

# Run additional probes on 10 representative families
REPRESENTATIVE_FAMILIES = [
    'Mistral-v0.3-7B',  # Mid-size, balanced
    'Qwen2.5-7B',       # Strong instruct model
    'Llama3-8B',        # Popular family
    'Gemma2-9B',        # Different architecture
    'Phi3-mini-3.8B',   # Small model
    # ... add 5 more
]

# Full probe definitions for reference:

# position_bias: Position Bias — Does the score change when response order is swapped?
#   Reference: Wang et al. (ACL 2024)
#   Variants: ['pairwise_first', 'pairwise_second']

# verbosity_bias: Verbosity Bias — Does a longer response get a higher score even if quality is the same?
#   Reference: Ye et al. (CALM 2024), Saito et al. (2023)
#   Variants: ['normal', 'verbose']

# sentiment_bias: Sentiment Bias — Does positive/negative tone in the response affect scoring?
#   Reference: Ye et al. (CALM 2024)
#   Variants: ['neutral', 'positive', 'negative']

# authority_bias: Authority Bias — Does adding a fake citation increase the score?
#   Reference: Ye et al. (CALM 2024)
#   Variants: ['no_citation', 'fake_citation']

# bandwagon_bias: Bandwagon Bias — Does telling the model 'most people agree' affect scoring?
#   Reference: Ye et al. (CALM 2024)
#   Variants: ['no_opinion', 'majority_agrees']

# self_enhancement: Self-Enhancement Bias — Does the model score its OWN generated responses higher?
#   Reference: Ye et al. (CALM 2024), Pan et al. (ACL 2026)
#   Variants: ['external_response', 'self_response']

# distraction_bias: Distraction Bias — Does irrelevant personal information in the prompt affect scoring?
#   Reference: Ye et al. (CALM 2024)
#   Variants: ['no_distraction', 'personal_info']

# fallacy_oversight: Fallacy Oversight Bias — Does the model overlook logical fallacies when the conclusion is correct?
#   Reference: Ye et al. (CALM 2024)
#   Variants: ['correct_reasoning', 'fallacious_reasoning']

# diversity_bias: Diversity Bias — Does mentioning demographic identity affect scoring?
#   Reference: Ye et al. (CALM 2024)
#   Variants: ['anonymous', 'demographic_given']
