from rest_framework import serializers

class ChatRequestSerializer(serializers.Serializer):
    user_input = serializers.CharField()  # Validates the user input as a string
    chat_history = serializers.ListField(
        child=serializers.DictField(),  # Each item in the list is a dictionary (object)
        required=False,  # Makes the field optional
        allow_empty=True,  # Allows an empty list
    )

class ChatResponseSerializer(serializers.Serializer):
    assistant_output = serializers.CharField()
    doc_id = serializers.ListField(child=serializers.CharField())


class SummaryInputSerializer(serializers.Serializer):
    input_text = serializers.CharField()

class SummaryOutputSerializer(serializers.Serializer):
    summary_text = serializers.CharField()
    paths = serializers.ListField(child=serializers.CharField())



class LSI(serializers.Serializer):
    input_text = serializers.CharField()


class LSIResponseSerializer(serializers.Serializer):
    statutes = serializers.DictField(
        child=serializers.CharField()
    )


class StringProcessingSerializer(serializers.Serializer):
    input_text = serializers.CharField()

class StringProcessingResponseSerializer(serializers.Serializer):
    result = serializers.CharField()