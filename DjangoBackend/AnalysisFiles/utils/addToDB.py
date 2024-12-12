import json
from django.db import IntegrityError
from api.models import CaseInfo  # Replace with your app name and model

def populate_database():
    json_file_path = 'case_data_output.json'  # Update path if needed

    try:
        with open(json_file_path, 'r') as file:
            case_data = json.load(file)

        for case in case_data:
            for case_id, case_title in case.items():
                try:
                    CaseInfo.objects.create(caseId=case_id, caseTitle=case_title)
                    print(f"Added case: {case_id} - {case_title}")
                except IntegrityError:
                    print(f"Case with ID {case_id} already exists. Skipping...")
    except Exception as e:
        print(f"Error populating database: {e}")
