from rest_framework import serializers
from .models import DocumentField, FieldCorrectionHistory

class FieldCorrectionHistorySerializer(serializers.ModelSerializer):
    corrected_by_name = serializers.SerializerMethodField()

    class Meta:
        model = FieldCorrectionHistory
        fields = [
            'id', 'field_key', 'field_label', 'previous_value', 'new_value',
            'corrected_by', 'corrected_by_name', 'corrected_at',
            'correction_type', 'notes'
        ]

    def get_corrected_by_name(self, obj):
        if obj.corrected_by:
            return obj.corrected_by.get_full_name() or obj.corrected_by.username
        return 'System'

class DocumentFieldSerializer(serializers.ModelSerializer):
    history = FieldCorrectionHistorySerializer(many=True, read_only=True)

    class Meta:
        model = DocumentField
        fields = [
            'id', 'document', 'field_key', 'field_label', 'field_value',
            'original_value', 'confidence', 'field_type', 'is_corrected',
            'page_number', 'bounding_box', 'context_snippet',
            'created_at', 'updated_at', 'history'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class DocumentFieldCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentField
        fields = [
            'id', 'document', 'field_key', 'field_label', 'field_value',
            'field_type', 'confidence', 'page_number'
        ]
        read_only_fields = ['id']
