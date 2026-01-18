from langchain_openai import ChatOpenAI
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate

from app.config import get_settings

settings = get_settings()


def create_summarizer():
    """Create and return a GPT-4 language model instance."""
    return ChatOpenAI(
        model="gpt-4",
        temperature=0.3,
        openai_api_key=settings.openai_api_key,
    )


def split_text_into_chunks(text: str, chunk_size: int = 4000, chunk_overlap: int = 500) -> list[Document]:
    """
    Split text into chunks for processing.

    Args:
        text: The text to split
        chunk_size: Maximum size of each chunk
        chunk_overlap: Overlap between chunks

    Returns:
        List of Document objects
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    chunks = text_splitter.split_text(text)
    return [Document(page_content=chunk) for chunk in chunks]


def summarize_text(text: str) -> str:
    """
    Summarize text using GPT-4.

    Args:
        text: The text to summarize

    Returns:
        Summary string
    """
    llm = create_summarizer()

    # Split text into chunks
    docs = split_text_into_chunks(text)

    # If text is short enough, use simple summarization
    if len(docs) == 1:
        return simple_summarize(docs[0].page_content, llm)

    # Use map-reduce for longer documents
    return map_reduce_summarize(docs, llm)


def simple_summarize(text: str, llm: ChatOpenAI) -> str:
    """
    Simple summarization for short documents.

    Args:
        text: Text to summarize
        llm: Language model instance

    Returns:
        Summary string
    """
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant that creates clear, concise summaries."),
        ("human", """Please provide a comprehensive summary of the following document.
Include the main points, key findings, and important conclusions.
Make the summary clear, concise, and well-organized.

Document:
{text}

Summary:"""),
    ])

    chain = prompt | llm
    result = chain.invoke({"text": text})
    return result.content


def map_reduce_summarize(docs: list[Document], llm: ChatOpenAI) -> str:
    """
    Map-reduce summarization for longer documents.

    Args:
        docs: List of document chunks
        llm: Language model instance

    Returns:
        Summary string
    """
    # Map phase - summarize each chunk
    map_prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant that creates clear, concise summaries."),
        ("human", """Summarize the following section of a document, capturing the key points and important details:

{text}

Section Summary:"""),
    ])

    map_chain = map_prompt | llm
    summaries = []

    for doc in docs:
        result = map_chain.invoke({"text": doc.page_content})
        summaries.append(result.content)

    # Reduce phase - combine summaries
    combined_summaries = "\n\n".join(summaries)

    reduce_prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant that creates clear, concise summaries."),
        ("human", """You are given summaries of different sections of a document.
Please combine these into a comprehensive, well-organized final summary.
Include the main points, key findings, and important conclusions.
Make sure the summary flows naturally and is easy to read.

Section Summaries:
{text}

Final Summary:"""),
    ])

    reduce_chain = reduce_prompt | llm
    result = reduce_chain.invoke({"text": combined_summaries})
    return result.content


def count_words(text: str) -> int:
    """Count words in text."""
    return len(text.split())
