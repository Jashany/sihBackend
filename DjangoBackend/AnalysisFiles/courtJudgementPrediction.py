import os
from langchain_groq import ChatGroq
from langchain_pinecone import PineconeVectorStore
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from langchain_core.prompts import ChatPromptTemplate
from decouple import config

from langchain_huggingface import HuggingFaceEmbeddings
from .Summary import summarize_input_text

pinecone_api_key = config('PINECONE_API_KEY')
groq_api_key = config('GROQ_API_KEY')

# Initialize Pinecone
# Initialize components
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")

kaam_ki_baat = summarize_input_text(input_text=file_contents)



# Replace placeholders with actual values if necessary
R2_BASE_URL = "https://pub-d58fae2843f34cfcbf2cfb0606b5efaf.r2.dev/judgmenttxts/"


vectorstore = PineconeVectorStore(index_name="search-engine", embedding=embeddings, pinecone_api_key=pinecone_api_key)


retriever = vectorstore.as_retriever(
    search_type="similarity_score_threshold",
    search_kwargs={"k": 5, "score_threshold": 0.5},
)

docs = retriever.invoke(kaam_ki_baat)
case_file_paths = []

for doc in docs:
    case_file_paths.append(R2_BASE_URL + doc.metadata["source"])


def read_case_files(case_file_paths):
    """
    Read all case files from the provided list of file paths.
    """
    if not isinstance(case_file_paths, list):
        raise ValueError("Expected a list of file paths, got: {}".format(type(case_file_paths)))

    case_files = []
    for file_path in case_file_paths:
        if not isinstance(file_path, str):
            raise ValueError(f"Invalid file path: {file_path}. Each entry should be a string.")
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                case_files.append(file.read())
        except:
            print("problem")
    return case_files


try:
    case_contents = read_case_files(case_file_paths)
    print("Successfully read case files.")
except ValueError as ve:
    print(f"ValueError: {ve}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")


def extract_facts_and_outcome(case_file_content):
    prompt = f"""
    The following is a legal case file. Extract the following:
    1. Key facts of the case (in 5-7 sentences).
    2. The outcome of the case (the judgment or decision or conclusion).

    Case File: {case_file_content}

    Response format:
    Facts: <Extracted facts>
    Outcome: <Extracted outcome>
    """
    response = llm.invoke(prompt)
    # print(response.content.split("\n"))
    # Parse the response
    facts, outcome = "", ""
    for line in response.content.split("\n"):
        if line.startswith("*Facts:*"):
            # print("fax bhai")
            facts = line.replace("*Facts:*", "")
        else:
            facts += line + "\n"

        if line.startswith("*Outcome:*"):
            # print("result aagya")
            outcome = line.replace("*Outcome:*", "")
        else:
            outcome += line + "\n"
    return {"facts": facts, "outcome": outcome}


def process_retrieved_cases(retrieved_cases_content):
    """
    Process all retrieved case file contents to extract facts and outcomes.
    """
    processed_cases = []
    for case_file_content in retrieved_cases_content:
        extracted_data = extract_facts_and_outcome(case_file_content)
        processed_cases.append(extracted_data)
    return processed_cases


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


def predict_case_outcome(input_case, case_file_paths):
    """
    Predict the outcome of the input case based on retrieved case files from the given paths.
    """
    # Step 1: Read case files from the provided list of paths
    retrieved_cases_content = read_case_files(case_file_paths)

    # Step 2: Process retrieved cases to extract facts and outcomes
    processed_cases = process_retrieved_cases(retrieved_cases_content)

    # Step 3: Construct the prediction prompt
    prediction_prompt = construct_prediction_prompt(input_case, processed_cases)

    # Step 4: Get prediction from the LLM
    response = llm.invoke(prediction_prompt)
    return response.content

predicted_outcome = predict_case_outcome(input_case, path)
print("Predicted Outcome:", predicted_outcome)