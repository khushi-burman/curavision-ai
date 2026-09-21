from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.llms import Ollama
from langchain_core.prompts import PromptTemplate

# 1. Initialize local embeddings and LLM
embeddings = OllamaEmbeddings(model="nomic-embed-text")
llm = Ollama(model="llama3.2:3b", temperature=0.0)

# 2. Connect to the existing ChromaDB
persist_directory = "./chroma_db"
vector_db = Chroma(
    persist_directory=persist_directory,
    embedding_function=embeddings
)

# 3. Define the clinical query and retrieve context
user_query = "What medications should be monitored when skin lesions appear?"
results = vector_db.similarity_search(user_query, k=2)
context_text = "\n\n".join([doc.page_content.strip() for doc in results])

# 4. Strict medical guardrail prompt
template = """
You are the CuraVision AI medical assistant. 
Answer the user's question STRICTLY based on the provided clinical context below.
Do not speculate or extrapolate beyond the context. If the answer cannot be found in the context, state that you do not have enough information.

Context:
{context}

Question:
{question}

Grounded Clinical Answer:
"""

prompt = PromptTemplate(template=template, input_variables=["context", "question"])
formatted_prompt = prompt.format(context=context_text, question=user_query)

# 5. Run inference with Llama 3.2
print("⚡ Generating grounded answer via Llama 3.2...\n")
response = llm.invoke(formatted_prompt)
print(response)