# NL2CNL

Translates natural language (NL) queries into a Controlled Natural Language (CNL) using an LLM,
guided by a YAML grammar specification, and benchmarks how accurate the translations are.

The included specification is [BioQueryCNL](https://github.com/seven-stars-0/BioQueryCNL), for biomedical queries:

```text
diabetes meds?  ->  Which drugs treat the disease Diabetes?
```

## Installation

Requires [uv](https://docs.astral.sh/uv/) and Python 3.14.

```bash
uv sync
cp .env.example .env   # then add the API keys of the providers you use
```

PyTorch is installed in its CPU-only build (see `pyproject.toml`).

## Usage

Any [LiteLLM](https://docs.litellm.ai/docs/providers) model identifier works, e.g. `ollama_chat/qwen3.5:4b` or `groq/qwen/qwen3-32b`.

```bash
# Single query
uv run nl2cnl -m ollama_chat/qwen3.5:4b -y data/specifications/bioquery.yaml -t "drugs related to asthma"

# One query per line from a file
uv run nl2cnl -m ollama_chat/qwen3.5:4b -y data/specifications/bioquery.yaml -i data/inputs/input.txt

# Benchmark: results saved to data/results/test-<timestamp>.csv
uv run nl2cnl -m ollama_chat/qwen3.5:4b -y data/specifications/bioquery.yaml -b data/tests/test_cases.json

# All settings from a file (CLI flags override it)
uv run nl2cnl -c data/config/config_example.yaml
```

Run `uv run nl2cnl --help` for every option.

### Strategies (`-s`)

| Name | What goes in the system prompt |
|---|---|
| `inctx` (default) | The whole grammar specification and, if given with `-e`, all the examples |
| `example` | The whole grammar specification and the `-k` examples (default 10) most similar to the query, retrieved with sentence embeddings. Requires `-e` |

### Benchmark output

One row per test case, with columns:
`id, model, strategy, top_k, syntax_valid, match, prompt_tokens, completion_tokens, total_tokens, latency_ms, cost_usd, error`.

- `syntax_valid`: 1 if the output is parsed by the Lark grammar (`-g`, default `grammar.lark`).
- `match`: 1 if the output is exactly one of the `expected_cnl` of the case.
- `error`: message of a temporary API error (rate limit, timeout...); the output is empty in that case.

## Data

```text
data/
├── config/          # example configuration file
├── examples/        # NL -> CNL example pairs (-e)
├── inputs/          # plain query files (-i)
├── specifications/  # YAML grammar specifications (-y)
├── tests/           # benchmark suites with expected CNL (-b)
└── results/         # benchmark CSVs (not versioned)
grammar.lark         # Lark version of the BioQueryCNL grammar, used by the benchmark
```

## Project structure

```text
src/nl2cnl/
├── main.py         # entry point: runs the pipeline
├── cli.py          # command line arguments
├── config.py       # merges config file and flags, validates them into AppConfig
├── loaders.py      # reads every input file
├── formatter.py    # converts the input source into PromptItem
├── model.py        # PromptItem, PromptResult, FatalLLMError
├── llm.py          # model calls through LiteLLM
├── prompts.py      # system prompt templates
├── ui.py           # terminal output (Rich)
├── strategies/     # how the system prompt is built (one file per strategy)
└── evaluation/     # syntax validator and benchmark CSV
```

## Tests

```bash
uv run pytest
```

They don't call any LLM.
