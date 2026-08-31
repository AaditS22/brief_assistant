import os

from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import BaseModel

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")

if not API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY is not set. Copy .env.example to .env and fill in your key."
    )

client = genai.Client(api_key=API_KEY)

class OutputSchema(BaseModel):
    summary: str
    open_questions: list[str]
    requirements: list[str]

PLACEHOLDER_PROMPT_TEMPLATE = """
You are helping a project team quickly understand a new client briefing.

Client briefing:
\"\"\"
{briefing}
\"\"\"

Analyse it and return:
- summary: what does the client want, in a few sentences.
- open_questions: important information that is still missing.
- requirements: a rough list of inferred requirements / user stories / features that the team can use
 to start working on a solution

Double check your work to make sure information is accurate.

Citations:
Citations exist so a reviewer can check if the AI hallucinated or based its claim on direct 
information from the briefing. Only add it where it is actually useful for a reviewer.

- You do not need to add a citation after every sentence. Do not add so many citations
  that it overwhelms the reviewer. 
- Do not cite trivial facts that are obviously and literally stated, cite more
  when an inference is made from information from the text.
- Never cite the same quote more than once across your entire response
- Follow this format exactly, adding the inline citation immediately after the statement that needs it: 
  (Citation: "exact quote copied from the briefing")
- Only use exact substrings from the briefing text, do not paraphrase.
- Keep quotes short (a phrase or short sentence).
"""

class QCSchema(BaseModel):
    verified_claims: list[str]
    flagged_claims: list[str]
    polish_notes: list[str]


PLACEHOLDER_QC_PROMPT_TEMPLATE = """
You are a quality control reviewer checking another AI's analysis of a client briefing,
before a human project team sees it.

Original client briefing:
\"\"\"
{briefing}
\"\"\"

AI-generated analysis to check:

Summary:
{summary}

Open questions:
{open_questions}

Requirements:
{requirements}

Your job is not to rewrite or improve the wording. Only check the analysis and report on it.

Return:
- verified_claims: statements from the analysis that are directly and clearly supported
  by the briefing. This does not mean include every statement that is not false (as there will be many).
  Only the statements that reviewers would be most skeptic about, things like inferences the AI made.
- flagged_claims: statements from the analysis that are not supported by the briefing,
  are an assumption presented as fact, or seem inaccurate / made up. Explain briefly why
  each one is flagged.
- polish_notes: things that are missing or could be added to make the analysis more
  thorough (not grammar/wording fixes). e.g. an important angle the summary skipped,
  or a requirement category that wasn't considered.

Only include an item if it is genuinely useful for a human reviewer. Do not pad the lists.
"""

def ask_gemini(briefing: str) -> OutputSchema:
    prompt = PLACEHOLDER_PROMPT_TEMPLATE.format(briefing=briefing)

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=OutputSchema,
        ),
    )

    if response.parsed is not None:
        return response.parsed
    return OutputSchema.model_validate_json(response.text)

def verify_output(briefing: str, result: OutputSchema) -> QCSchema:
    prompt = PLACEHOLDER_QC_PROMPT_TEMPLATE.format(
        briefing=briefing,
        summary=result.summary,
        open_questions="\n".join(f"- {q}" for q in result.open_questions),
        requirements="\n".join(f"- {r}" for r in result.requirements),
    )

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=QCSchema,
        ),
    )

    if response.parsed is not None:
        return response.parsed
    return QCSchema.model_validate_json(response.text)