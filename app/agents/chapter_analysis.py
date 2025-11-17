from os import getenv
from typing import List

from agno.agent import Agent
from agno.models.openai import OpenAILike
from pydantic import BaseModel, Field

prompt = {
    "description": "You are a professional bilingual (Chinese-English) literary editor with expertise in extracting critical information from Chinese novel chapters and converting it into a standardized data format. You possess strong analytical skills in literary interpretation and exceptional translation accuracy, enabling you to identify all essential narrative elements and express them clearly in both languages.",
    "instructions": [
        "Read the entire chapter thoroughly to ensure no critical information is missed.",
        "Character Extraction: Identify all named characters, including those who appear only once. Classify them based on their frequency and narrative importance into: Protagonists (central characters throughout the story), Major Characters (recurring with significant plot influence), and Minor Characters (named but appear briefly or only once).",
        "Alias Collection: Only include name variants, nicknames, or abbreviations that are explicitly mentioned in the text. Do NOT include relational titles (e.g., father, teacher), occupational roles, identity-based labels, or emotional descriptors.",
        "Terminology Extraction: Prioritize terms related to the story’s worldbuilding (e.g., place names, organizations, unique artifacts), magic or skill systems, and domain-specific vocabulary. Exclude character names, common words, and basic adjectives.",
        "Translation Standards: Use American English conventions. Translate names using phonetic transliteration; translate terms (e.g., locations, artifacts, skills) using a hybrid approach combining transliteration and contextual interpretation to suit native English-speaking readers.",
        "Plot Summary: Provide an objective third-person summary in 80–120 words, highlighting pivotal events and turning points. Avoid meta-narrative phrases such as 'In this chapter' or 'The author describes'.",
        "Quality Control: If any term is ambiguous or difficult to translate, mark the English field with [TBD] instead of leaving it blank or omitting it."
    ],
    "expected_output": "Return the final result in a valid JSON format only, without any Markdown code blocks, annotations, or extra symbols. The output must be clean and directly parseable by a program."
}


class Character(BaseModel):
    name: str = Field(..., description="Name of the character")
    translation: str = Field(..., description="Translation standard")
    aliases: List[str] = Field(..., description="the character aliases")

class Terminology(BaseModel):
    term: str = Field(..., description="The terminology")
    translation: str = Field(..., description="Translation standard")

class ChapterAnalysisResult(BaseModel):
    summary: str = Field(..., description="chapter summary")
    characters: List[Character] = Field(..., description="List of characters in this chapter")
    terminologies: List[Terminology] = Field(..., description="List of terminologies in this chapter")

ChapterAnalysisAgent = Agent(
    model=OpenAILike(id="gpt-5-mini",
                     temperature=getenv("TEMPERATURE", 0.9),
                     api_key=getenv("API_KEY", ""),
                     base_url=getenv("BASE_URL", "")),
    instructions=prompt["instructions"],
    description=prompt["description"],
    expected_output=prompt["expected_output"],
    output_schema=ChapterAnalysisResult,
    telemetry=False,
)


from agno.run.agent import RunOutput
from dotenv import load_dotenv
load_dotenv()
response: RunOutput = ChapterAnalysisAgent.run("chapter content ...")