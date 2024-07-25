from pydantic import BaseModel

class DocsQueryInput(BaseModel):
    text: str

class DocsQueryOutput(BaseModel):
    input: str
    output: str
    intermediate_steps: list[str]