from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_groq import ChatGroq
from langchain_pinecone import PineconeVectorStore
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from langchain_core.prompts import ChatPromptTemplate
from decouple import config


groq_api_key = config('GROQ_API_KEY')


llm = ChatGroq(
    temperature=0,
    model_name="llama3-8b-8192",
    groq_api_key=groq_api_key
)




def legal_st(file_contents):
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    contents = splitter.split_text(file_contents)

    ans = ""
    for chunks in contents:
        prompt = f"""
        You are an AI trained in legal analysis. Extract the key legal statutes, laws, and concepts referenced in the following case text:

        Case File : {chunks}

        Response format:
        Key Statutes: <List of key statutes and laws>
        Summary: <summary of the statues and laws involved in the case file not the company involved in the case>
        """
        response = llm.invoke(prompt)
        ans += response.content

    words = ans.split()
    chunks = []
    start = 0
    while start < len(words):
        end = min(start + 1000, len(words))
        chunks.append(" ".join(words[start:end]))
        start += 1000 - 200

    outputs = []
    for chunk in chunks:
        prompt = f"Analyze the following text and provide all the legal statues and laws you came across:\n\n{chunk}. you have to reply such that the law name and its description is separated by a colon. description should be 2-3 lines long"
        response = llm.invoke(prompt)  # Assuming response.content contains the LLM output
        outputs.append(response.content)  # Collect the output for each chunk

    # Step 3: Combine all outputs into a single result
    combined_output = "\n".join(outputs)

    lines = combined_output.strip().split("\n")
    statutes_dict = {}

    for line in lines:
        if line.strip():
            parts = line.split(": ", 1)
            if len(parts) == 2:
                key = parts[0].replace("", "")
                value = parts[1].strip()
                statutes_dict[key] = value
    return statutes_dict



def main():
    file_contents = """
    DocumentBgs Sgs Soma Jv vs Nhpc Ltd on 10 December 2019Equivalent citations AIRONLINE 2019 SC 1720  2019 17 SCALE 369 2019 6 ARBILR 393  2019 6 ARBILR 393Author R.F. NarimanBench V. Ramasubramanian Aniruddha Bose R.F. Nariman REPORTABLE IN THE SUPREME COURT OF INDIA CIVIL APPELLATE JURISDICTION CIVIL APPEAL NO 9307 OF 2019 ARISING OUT OF SLP CIVIL NO25618 OF 2018 BGS SGS SOMA JV u2026Petitioner Versus NHPC LTD u2026Respondent WITH CIVIL APPEAL NO 9308 OF 2019 ARISING OUT OF SLP CIVIL NO 25848 OF 2018 WITH CIVIL APPEAL NO 9309 OF 2019 ARISING OUT OF SLP CIVIL NO 28062 OF 2018
    """

    statutes_dict = legal_st(file_contents)

    # Print the extracted statutes and their summaries
    print(statutes_dict)

if __name__ == "__main__":
    main()