from openai import OpenAI
from decouple import config

# Load keys from environment variables
openai_api_key = config('OPENAI_API_KEY')

# Initialize the OpenAI client
client = OpenAI(api_key=openai_api_key)

def get_standalone_question(chat_history, user_input):
    """
    Function to get a standalone question from chat history and user input using OpenAI.

    Args:
        chat_history (list): List of dictionaries containing chat history.
        user_input (str): User's current question.

    Returns:
        str: Reformulated standalone question.
    """
    # Format chat history into a prompt
    chat_history_formatted = "\n".join([f"{msg['role']}: {msg['content']}" for msg in chat_history])

    # Define the prompt
    prompt = f"""
    Given the following chat history and the latest user question, reformulate the question into a standalone question that can be understood without the context of the chat history. 
    Do not answer the question, just reformulate it and return only the reformulated question.

    Chat History:
    {chat_history_formatted}

    User Question:
    {user_input}
    """

    # Make the API call
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an assistant specializing in creating standalone questions."},
            {"role": "user", "content": prompt}
        ],
        temperature=0,
        max_tokens=150
    )

    # Extract and return the reformulated question
    standalone_question = response.choices[0].message.content.strip()
    return standalone_question

# Main function for testing
if __name__ == "__main__":
    chat_history = [
        {"role": "user", "content": "Tell me about Vodafone vs Union of India case."},
        {"role": "assistant", "content": "Vodafone is an amazing company"},
    ]

    user_input = "How is it similar to ASTRAZENECA AB & ANR. VS. INTAS PHARMACEUTICALS LIMITED"
    standalone_question = get_standalone_question(chat_history, user_input)
    print("Standalone Question:", standalone_question)
