from arg.arg_checker import check_args
from arg.arg_parser import parse_args
from arg.arg_processer import process_args
from dotenv import load_dotenv
from prompt.prompt_model import prompt_model

from nl2cnl.file_opener import open_file

load_dotenv()

# ARG PHASE
args = parse_args()
check_args(args)
processed = process_args(args)

specification = open_file(processed.yaml)

model = processed.model

system_prompt = f"""You are a formal translator that converts natural language input into a Controlled Natural Language (CNL) strictly conforming to the provided YAML grammar specification.

How to read and apply the grammar specification:
1. Root rule: Always start expanding from the `start` rule down to terminal tokens.
2. Literal tokens: Strings enclosed in double quotes (e.g., `"the"`, `"of the"`, `"?."`) are mandatory keywords or punctuation and MUST appear verbatim in the exact positions specified.
3. Alternatives: YAML lists (`- ...`) and pipes (`|`) represent mutually exclusive production branches; select the branch that best matches the semantic intent of the input.
4. Lexical terminals: Placeholders such as `string` or `number` must be instantiated with the corresponding words or values extracted from the user input.
5. Implicit slot resolution: If a production rule requires multiple adjacent slots (e.g., a classifier/type followed by an identifier/instance) and the user input omits one of them, infer the minimal missing grammatical slot from general linguistic context so that every required token of the rule is satisfied.

Output constraints:
- Output ONLY the final valid CNL sentence.
- Do NOT include explanations, parse trees, markdown formatting, or surrounding quotes.

Grammar specification:
{specification}
"""

messages = [
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": f"{processed.text}"}
]

text = prompt_model(model, messages)

print(text)
