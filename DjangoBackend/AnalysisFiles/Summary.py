from AnalysisFiles.utils.preprocessfortfdf import clean_document
from AnalysisFiles.utils.Tf_idf import summarize_text
from groq import Groq
from decouple import config
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore
groq_api_key = config('GROQ_API_KEY')
pinecone_api_key = config('PINECONE_API_KEY')

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
vectorstore = PineconeVectorStore(index_name="search-engine", embedding=embeddings, pinecone_api_key=pinecone_api_key)


client = Groq(api_key=groq_api_key)
retriever = vectorstore.as_retriever(
    search_type="similarity_score_threshold",
    search_kwargs={"k": 5, "score_threshold": 0.5},
)

def summarize_input_text(input_text, dict_path="AnalysisFiles/utils/dictionary.txt", word_limit=600, sentence_limit=40):
    preprocessed_text = clean_document(input_text)
    top_lines = summarize_text(preprocessed_text, dict_path, word_limit, sentence_limit)
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": f'''You are an expert legal assistant specializing in summarizing legal documents.
                Just give the summary, and don't write statements like "Here is a concise and coherent summary of the key sentences:" or "The summary is as follows:".

I will provide you with a set of key sentences extracted from a legal document. Using these sentences, create a concise and coherent summary that accurately reflects the primary purpose, arguments, and conclusions of the document. Ensure that your summary is formal, well-structured, and does not include information outside the provided sentences.

Here are the key sentences:
{top_lines}'''
            }
        ],
        model="llama3-8b-8192"
    )
    groqsummary = chat_completion.choices[0].message.content
    path =[]
    docs = retriever.invoke(groqsummary)

    path = [doc.metadata["source"] for doc in docs if doc and doc.metadata.get("source")]

    print(groqsummary)
    print(path)
    return groqsummary, path


if __name__ == "__main__":
    input_text = """
    Your sample input text goes here. This text will be preprocessed and summarized using the clean_document function and the summarize_text function.
    """
    summary, paths = summarize_input_text(input_text)
    print("Summary:")
    print(summary)
    print("Paths:")
    print(paths)