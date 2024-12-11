import re

def clean_document(input_string):
    """
    Cleans the given document string by removing paragraph labels, dots from abbreviations,
    and other punctuation marks.

    Args:
        input_string (str): The raw document as a single string.

    Returns:
        str: The cleaned document.
    """
    # Split the input string into lines
    documents = input_string.strip().split("\n")

    # Find the starting line of the main content
    for i in range(len(documents)):
        if documents[i].startswith("1."):
            break
    doc = documents[i:]

    # Process each line
    temp = ""
    for eachDocument in doc[:]:
        # Remove paragraph labels like 1., 2., etc.
        eachDocument = re.sub(r'(\d\d\d|\d\d|\d)\.\s', ' ', eachDocument)
        # Remove dots in cases like File No.1063
        eachDocument = re.sub(r'(?<=[a-zA-Z])\.(?=\d)', '', eachDocument)
        # Remove ending dots of abbreviations
        eachDocument = re.sub(r'(?<=\d|[a-zA-Z])\.(?=\s[\da-z])', ' ', eachDocument)
        # Remove dots after abbreviations
        eachDocument = re.sub(r'(?<=\d|[a-zA-Z])\.(?=\s?[\!\"\#\$\%\&\'\(\)\*\+\,\-\/\:\;\<\=\>\?\@\[\\\]\^\_\`\{\|\}\~])', '', eachDocument)
        # Remove other punctuation marks
        eachDocument = re.sub(r'(?<!\.)[\!\"\#\$\%\&\'\(\)\*\+\,\-\/\:\;\<\=\>\?\@\[\\\]\^\_\`\{\|\}\~]', ' ', eachDocument)

        # Concatenate the cleaned line
        temp += eachDocument

    # Remove extra spaces and process the final document
    temp = temp.replace("  ", " ")  # Replace double spaces with single space
    cleaned_document = temp.lstrip()  # Remove leading space

    return cleaned_document
