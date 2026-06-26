from pydantic_ai import Agent, RunContext
from app.llm.factory import llm_factory
from app.config import settings
from app.assistant.deps import AgentDeps
from app.assistant.outputs import GroundedAnswer

# Create model dynamically from settings
model = llm_factory.create(settings.llm_provider, settings.model_name)

# Define the PydanticAI Agent
agent = Agent(
    model,
    deps_type=AgentDeps,
    output_type=GroundedAnswer,
    system_prompt=(
        "You are a professional financial analyst assistant researching company filings. "
        "Your goal is to provide accurate, truthful, and grounded answers using the provided context."
    )
)

@agent.system_prompt
def generate_dynamic_prompt(ctx: RunContext[AgentDeps]) -> str:
    """
    Format the dynamic context to include the retrieved chunks and prompt guidelines.
    """
    chunks_str = ""
    for idx, chunk in enumerate(ctx.deps.retrieved_chunks, start=1):
        ticker = "Unknown"
        form = "Unknown"
        if getattr(chunk, "document", None):
            ticker = getattr(chunk.document, "ticker", "Unknown")
            form = getattr(chunk.document, "filing_type", "Unknown")
            
        chunks_str += (
            f"--- Source Chunk [{idx}] ---\n"
            f"Chunk UUID: {chunk.id}\n"
            f"Document UUID: {chunk.document_id}\n"
            f"Filing Info: {ticker} {form}\n"
            f"Text:\n{chunk.chunk_text}\n\n"
        )
        
    return (
        "You are an expert financial analyst. Your task is to answer the user's question using ONLY the provided Source Chunks.\n"
        "Grounding Rules:\n"
        "1. Your answer must be strictly derived from the provided Source Chunks. Do not introduce outside knowledge or extrapolate.\n"
        "2. If the chunks do not contain sufficient information to answer, you must state that you cannot answer based on the provided documents.\n"
        "3. Every claim or statement of fact you make must cite the specific Source Chunk it is based on. "
        "For each citation, you must map it to the exact Chunk UUID and Document UUID, and provide the exact quote (excerpt) from the chunk's text.\n"
        "4. Include all cited excerpts in the 'supporting_passages' list.\n"
        "5. Never reference or cite a Source Chunk that was not explicitly provided in the list below.\n\n"
        f"Retrieved Source Chunks:\n{chunks_str}"
    )
