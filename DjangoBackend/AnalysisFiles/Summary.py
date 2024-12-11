from AnalysisFiles.utils.preprocessfortfdf import clean_document
from AnalysisFiles.utils.Tf_idf import summarize_text
from groq import Groq
from decouple import config

groq_api_key = config('GROQ_API_KEY')
client = Groq(api_key=groq_api_key)

def summarize_input_text(input_text, dict_path="AnalysisFiles/utils/dictionary.txt", word_limit=600, sentence_limit=40):
    preprocessed_text = clean_document(input_text)
    top_lines = summarize_text(preprocessed_text, dict_path, word_limit, sentence_limit)
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": f'''You are an expert legal assistant specializing in summarizing legal documents.

I will provide you with a set of key sentences extracted from a legal document. Using these sentences, create a concise and coherent summary that accurately reflects the primary purpose, arguments, and conclusions of the document. Ensure that your summary is formal, well-structured, and does not include information outside the provided sentences.

Here are the key sentences:
{top_lines}'''
            }
        ],
        model="llama3-8b-8192"
    )
    groqsummary = chat_completion.choices[0].message.content
    return groqsummary

