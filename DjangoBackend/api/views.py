from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import *
from AnalysisFiles.ChatModel import legal_assistant
from AnalysisFiles.Summary import summarize_input_text
from AnalysisFiles.cjpe import predict_case_outcome
from AnalysisFiles.lsi import legal_st
from django.conf import settings

class ChatAPIView(APIView):
    def post(self, request):
        # Validate the request data
        serializer = ChatRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Extract data
        user_input = serializer.validated_data.get("user_input")
        chat_history = serializer.validated_data.get("chat_history", [])


        assistant_object = legal_assistant(chat_history, user_input)


        # Prepare response
        response_data = {
            "assistant_output": assistant_object["answer"],
            "doc_id": assistant_object["source"]
        }

        print(response_data)
        response_serializer = ChatResponseSerializer(response_data)

        return Response(response_serializer.data, status=status.HTTP_200_OK)


# views.py


class TextSummaryAPIView(APIView):
    def post(self, request):
        # Validate input
        input_serializer = SummaryInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        # Get the input text
        input_text = input_serializer.validated_data['input_text']

        # Process the input text (replace this with your summarization logic)
        summary_text, path = summarize_input_text(input_text)

        # Prepare the response
        response_data = {
            'summary_text': summary_text,
            'paths': path
        }
        output_serializer = SummaryOutputSerializer(data=response_data)
        output_serializer.is_valid(raise_exception=True)

        return Response(output_serializer.data, status=status.HTTP_200_OK)


class StringProcessingView(APIView):
    def post(self, request):
        serializer = StringProcessingSerializer(data=request.data)

        if serializer.is_valid():
            # Call create method to process the string
            input_text = serializer.validated_data['input_text']

            result = predict_case_outcome(input_text)

            # Serialize the response
            response_serializer = StringProcessingResponseSerializer(data={'result': result})
            response_serializer.is_valid(raise_exception=True)

            return Response(response_serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LSIView(APIView):
    def post(self, request):
        # Validate the request data
        serializer = LSI(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Extract the input text
        input_text = serializer.validated_data['input_text']

        # Process the input text to extract legal statutes
        statutes_dict = legal_st(input_text)

        # Prepare the response
        response_serializer = LSIResponseSerializer(data={'statutes': statutes_dict})
        response_serializer.is_valid(raise_exception=True)

        return Response(response_serializer.data, status=status.HTTP_200_OK)