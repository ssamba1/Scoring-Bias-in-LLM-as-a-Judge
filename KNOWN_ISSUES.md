# Known Issues

## 4-bit Loading: `config=config` blocks `load_in_4bit`

When loading quantized 4-bit models, passing `config=config` in `from_pretrained()`
can conflict with `load_in_4bit=True`. The `config` object overwrites the
quantization config. Workaround: omit `config=` when using `load_in_4bit`, or
set quantization parameters via `BitsAndBytesConfig` directly.

## StableLM `pad_token_id` Workaround

StableLM-2-1.6B does not set `pad_token_id` by default. This causes issues in
batched generation. Workaround: manually set `tokenizer.pad_token_id = tokenizer.eos_token_id`
and `model.config.pad_token_id = tokenizer.eos_token_id` after loading.

## OpenRouter Stop-Token Truncation

OpenRouter truncates responses that exceed the stop-token limit for 5 excluded
models: `gpt-4-turbo`, `gpt-3.5-turbo`, `claude-3-opus`, `claude-3-sonnet`,
and `claude-3-haiku`. These models may drop the final score number when the
response is truncated mid-token. Workaround: for these models, use a longer
`max_tokens` or switch to a model without stop-token truncation.

## Descriptive Parser Issue (1/9 Comparisons)

The descriptive score parser (`extract_descriptive`) only matches 1 of 9
comparisons correctly when the scoring rubric uses descriptive labels
("excellent", "good", "fair", "poor", "terrible") instead of numeric scores.
The parser uses substring matching which is fragile for nuanced descriptive
outputs. See `tests/test_all.py:TestScoringFunctions.test_extract_descriptive`
for current behavior.

## Windows Patch Tool Double-Escapes LaTeX Backslashes

The Hermes `patch` tool, when used on Windows, double-escapes backslashes in
LaTeX files. Writing `\section{Introduction}` via `new_string` results in
`\\section{Introduction}` in the file. Workaround: for LaTeX edits, write the
entire file with `write_file()` instead of using `patch()`, or run the
replacements via `sed` in the terminal.
