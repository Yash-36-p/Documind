from rest_framework import serializers
from .models import ExtractedField, FieldCorrectionHistory

class FieldCorrectionHistorySerializer(serializers.ModelSerializer):
    corrected_by_name = serializers.SerializerMethodField()

    class Meta:
        model = FieldCorrectionHistory
        fields = [
            'id', 'field_name', 'field_key', 'previous_value', 'new_value',
            'corrected_by', 'corrected_by_name', 'corrected_at',
            'correction_type', 'notes'
        ]

    def get_corrected_by_name(self, obj):
        if obj.corrected_by:
            return obj.corrected_by.get_full_name() or obj.corrected_by.username
        return 'System'

class ExtractedFieldSerializer(serializers.ModelSerializer):
    history = FieldCorrectionHistorySerializer(many=True, read_only=True)
    # Compatibility properties for frontend
    field_label = serializers.CharField(source='field_name', read_only=True)
    field_value = serializers.CharField(source='extracted_value', read_only=True)

    class Meta:
        model = ExtractedField
        fields = [
            'id', 'document', 'field_name', 'extracted_value', 'confidence',
            'field_key', 'field_label', 'field_value', 'field_type',
            'is_corrected', 'original_value', 'page_number', 'bounding_box',
            'context_snippet', 'created_at', 'updated_at', 'history'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class ExtractedFieldCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExtractedField
        fields = [
            'id', 'document', 'field_name', 'extracted_value',
            'confidence', 'field_key', 'field_type', 'page_number'
        ]
        read_only_fields = ['id']
