from openai import OpenAI
from decouple import config

# Load keys from environment variables
openai_api_key = config('OPENAI_API_KEY')

# Initialize OpenAI client
client = OpenAI(api_key=openai_api_key)

def extract_search_terms(user_prompt):
    # Define the prompt template
    prompt = '''
    Analyze the input to extract relevant search terms for a query. This system is a database of legal cases that uses string matching. The database will never contain words like 'highlights,' 'summary,' or 'details.' Focus only on the core search terms related to the input. If the input contains a year, generate a date range in the format 'fromdate=1-1-[year] todate=31-12-[year]'. Output the result in JSON format with the key search_query. Examples:
    Input: vodafone vs union of India
    Output: { "search_query": "vodafone vs union of India" }

    Input: vodafone vs union of India (2018)
    Output: { "search_query": "vodafone vs union of India fromdate: 1-1-2018 todate: 31-12-2018" }

    Input: supreme court ruling on privacy (2017)
    Output: { "search_query": "supreme court ruling on privacy fromdate: 1-1-2017 todate: 31-12-2017" }

    Input: give me highlights of all cases of zomato in the year 2015 and tell me the verdicts
    Output: { "search_query": "zomato fromdate: 1-1-2015 todate: 31-12-2015" }

    this is the input:
    '''

    # Make the API call to OpenAI
    chat_completion = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an expert in legal data processing."},
            {"role": "user", "content": prompt + user_prompt}
        ],
        temperature=0,
        max_tokens=150
    )

    # Extract the classification result
    classification_result = chat_completion.choices[0].message.content.strip()
    return classification_result

# Main function for testing
if __name__ == "__main__":
    user_prompt = "Tell me about AstraZenca vs Intas Pharmaceuticals Limited case, what can you tell me about your mom"
    result = extract_search_terms(user_prompt)
    print("Search Query:", result)
