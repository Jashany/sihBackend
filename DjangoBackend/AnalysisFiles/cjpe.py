import os
import requests
import sys
from decouple import config
from .Summary import summarize_input_text

# Langchain and ML imports
from langchain_groq import ChatGroq
from langchain_pinecone import PineconeVectorStore
from langchain_huggingface import HuggingFaceEmbeddings

# Hardcoded API keys and configurations
pinecone_api_key = config('PINECONE_API_KEY', default='your_pinecone_api_key')
groq_api_key = config('GROQ_API_KEY', default='your_groq_api_key')
R2_BASE_URL = "https://pub-d58fae2843f34cfcbf2cfb0606b5efaf.r2.dev/judgmenttxts/"

# Initialize components
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
llm = ChatGroq(
    temperature=0,
    model_name="llama3-8b-8192",
    groq_api_key=groq_api_key
)



def retrieve_similar_cases(summarized_text):
    """
    Retrieve similar case documents from Pinecone vector store.
    """
    vectorstore = PineconeVectorStore(
        index_name="search-engine",
        embedding=embeddings,
        pinecone_api_key=pinecone_api_key
    )

    retriever = vectorstore.as_retriever(
        search_type="similarity_score_threshold",
        search_kwargs={"k": 5, "score_threshold": 0.5},
    )

    # Retrieve similar documents
    docs = retriever.invoke(summarized_text)
    docs = retriever.invoke(summarized_text)
    return [R2_BASE_URL + doc.metadata["source"] for doc in docs]


def read_case_files(case_file_paths):
    """
    Read case files from the provided list of file paths.
    """
    case_files = []
    for file_path in case_file_paths:
        try:
            response = requests.get(file_path)
            if response.status_code == 200:
                case_files.append(response.text)
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
    return case_files


def extract_facts_and_outcome(case_file_content_full):
    case_file_content = summarize_input_text(case_file_content_full)
    """
    Extract key facts and outcome from a case file using LLM.
    """
    prompt = f"""
    The following is a legal case file. Extract the following:
    1. Key facts of the case (in 5-7 sentences).
    2. The outcome of the case (the judgment or decision or conclusion).

    Case File: {case_file_content}

    Response format:
    Facts: <Extracted facts>
    Outcome: <Extracted outcome>
    """

    response = "hello"
    try:
        response = llm.invoke(prompt)
    except Exception as e:
        print("armaan randi")

    facts, outcome = "", ""
    for line in response.content.split("\n"):
        if line.startswith("*Facts:*"):
            facts = line.replace("*Facts:*", "")
        elif line.startswith("*Outcome:*"):
            outcome = line.replace("*Outcome:*", "")

    return {"facts": facts, "outcome": outcome}

def process_retrieved_cases(retrieved_cases_content):
    """
    Process retrieved case file contents to extract facts and outcomes.
    """
    return [extract_facts_and_outcome(case) for case in retrieved_cases_content]

def construct_prediction_prompt(input_case, processed_cases):
    """
    Construct a structured prompt for the LLM to predict the outcome of the input case.
    """
    prompt = f"Predict the outcome of the following case based on similar past cases:\n\n"
    prompt += f"Input Case:\n{input_case}\n\n"
    prompt += "Similar Cases and Their Extracted Outcomes:\n"

    for i, case in enumerate(processed_cases, start=1):
        prompt += f"Case {i}:\nFacts: {case['facts']}\nOutcome: {case['outcome']}\n\n"

    prompt += "Return only the probable outcome of the input case."
    return prompt

def predict_case_outcome(file_contents):
    """
    Main method to predict the outcome of a legal case.
    """

    # Summarize input text
    summarized_text = summarize_input_text(file_contents)[0]

    # Retrieve similar case file paths
    similar_case_paths = retrieve_similar_cases(summarized_text)

    # Read retrieved case files
    retrieved_cases_content = read_case_files(similar_case_paths)

    # Process retrieved cases
    processed_cases = process_retrieved_cases(retrieved_cases_content)

    # Construct prediction prompt
    prediction_prompt = construct_prediction_prompt(file_contents, processed_cases)

    # Get prediction from the LLM
    response = llm.invoke(prediction_prompt)

    return response.content



def main():
    # Hardcoded file path
    file_contents = '''DocumentBgs Sgs Soma Jv vs Nhpc Ltd on 10 December 2019Equivalent citations AIRONLINE 2019 SC 1720  2019 17 SCALE 369 2019 6 ARBILR 393  2019 6 ARBILR 393Author R.F. NarimanBench V. Ramasubramanian Aniruddha Bose R.F. Nariman REPORTABLE IN THE SUPREME COURT OF INDIA CIVIL APPELLATE JURISDICTION CIVIL APPEAL NO 9307 OF 2019 ARISING OUT OF SLP CIVIL NO25618 OF 2018 BGS SGS SOMA JV u2026Petitioner Versus NHPC LTD u2026Respondent WITH CIVIL APPEAL NO 9308 OF 2019 ARISING OUT OF SLP CIVIL NO 25848 OF 2018 WITH CIVIL APPEAL NO 9309 OF 2019 ARISING OUT OF SLP CIVIL NO 28062 OF 2018 JUDGMENT R.F. NARIMAN J. Leave granted 2.Signature Not Verified Three appeals before us raise questions as to maintainability of ap Digitally signed by RNATARAJANDate 2019.12.10 peals under Section 37 of the Arbitration and Conciliation Act 199617 44 59 ISTReason '''

    # Predict case outcome
    predicted_outcome = predict_case_outcome(file_contents)

    # Print predicted outcome
    print("\n--- Predicted Case Outcome ---")
    print(predicted_outcome)

if __name__ == "__main__":
    main()