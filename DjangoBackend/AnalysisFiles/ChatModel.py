from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain_pinecone import PineconeVectorStore
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from langchain_core.prompts import ChatPromptTemplate
from decouple import config


# Load keys from environment variables
pinecone_api_key = config('PINECONE_API_KEY')
groq_api_key = config('GROQ_API_KEY')

# Initialize Pinecone
# Initialize components
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")

vectorstore = PineconeVectorStore(
    index_name="search-engine",
    embedding=embeddings,
    pinecone_api_key=pinecone_api_key,
)

llm = ChatGroq(model="llama3-8b-8192", groq_api_key=groq_api_key,temperature=0.7)

retriever = vectorstore.as_retriever(
    search_type="similarity_score_threshold",
    search_kwargs={"k": 5, "score_threshold": 0.5},
)

# Define the prompts
retrieval_prompt = ChatPromptTemplate.from_template(
    """
    You are an intelligent legal assistant who is specialised in answering user queries about commercial cases and laws.
    Use the given context and chat history to answer the user's question to the best of your capacity.
    Keep the answer to about 2 paragraphs maximum and no need to mention according to context in the answer.
    Don't answer outside the domain of commercial cases and law.
    No need to mention that you are using any context for every answer. Just converse normally.
    <context>
    {context}
    <context>
    Question : {input}
    """
)

contextualise_q_prompt = ChatPromptTemplate.from_template(
    """
    Given a chat history and the latest user question
    which might reference a context in the chat history
    formulate a standalone question that can be understood without the chat history
    Do not answer the question, just reformulate it and return only the question as it is
    {chats}
    {input}
    """
)

# Define chains
document_chain = create_stuff_documents_chain(llm, retrieval_prompt)
retrieval_chain = create_retrieval_chain(retriever, document_chain)

history_chain = contextualise_q_prompt | llm


# Function definition
def legal_assistant(chat_history, user_input):
    """
    Function to process user input and chat history, retrieve context, and provide an answer.

    Args:
        chat_history (list): List of dictionaries containing chat history.
        user_input (str): User's current question.

    Returns:
        dict: Contains the answer and source document information.
    """
    # Contextualize the question
    ques = history_chain.invoke({"input": user_input, "chats": chat_history}).content

    # Retrieve the answer
    answer = retrieval_chain.invoke({"input": ques})
    print(answer['context'])
    return {
        "answer": answer['answer'],
        "source": [answer['context'][0].metadata["source"].replace("data\\", "")] if answer['context'] else []
    }

# Example usage
if __name__ == "__main__":
    chat_history = [
        {"role": "user", "content": "What is the competition act?"},
        {"role": "assistant", "content": "The Competition Act is a law that promotes or seeks to maintain market competition by regulating anti-competitive conduct by companies."}
    ]

    user_input = "Tell me about ASTRAZENECA AB & ANR. VS. INTAS PHARMACEUTICALS LIMITED"
    response = legal_assistant(chat_history, user_input)
    print("Answer:", response["answer"])
    print("Source:", response["source"])
