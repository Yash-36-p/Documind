import os
from rest_framework import serializers
from .models import Document, DocumentPage, ProcessingLog
from apps.extraction.serializers import ExtractedFieldSerializer, FieldCorrectionHistorySerializer

class ProcessingLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProcessingLog
        fields = ['id', 'log_level', 'stage', 'message', 'details', 'created_at']

class DocumentPageSerializer(serializers.ModelSerializer):
    thumbnail_url = serializers.SerializerMethodField()

    class Meta:
        model = DocumentPage
        fields = [
            'id', 'page_number', 'text', 'ocr_confidence',
            'extraction_method', 'thumbnail_url', 'metadata'
        ]

    def get_thumbnail_url(self, obj):
        if obj.thumbnail:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.thumbnail.url)
            return obj.thumbnail.url
        return None

class DocumentListSerializer(serializers.ModelSerializer):
    document_type_display = serializers.CharField(source='get_document_type_display', read_only=True)
    category_display = serializers.CharField(source='get_document_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    uploaded_by_name = serializers.SerializerMethodField()
    preview_url = serializers.SerializerMethodField()
    fields_count = serializers.IntegerField(source='extracted_fields.count', read_only=True)
    # Compatibility aliases
    category = serializers.CharField(source='document_type', read_only=True)
    created_at = serializers.DateTimeField(source='uploaded_at', read_only=True)
    summary_preview = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = [
            'id', 'filename', 'title', 'document_type', 'document_type_display',
            'category', 'category_display', 'status', 'status_display',
            'confidence', 'ocr_confidence', 'classification_confidence',
            'uploaded_by', 'uploaded_by_name', 'uploaded_at', 'created_at',
            'page_count', 'file_size', 'file_type', 'is_verified',
            'preview_url', 'fields_count', 'updated_at',
            'summary_preview',
        ]

    def get_summary_preview(self, obj):
        """Return first 150 chars of summary for the list view."""
        if obj.summary:
            return obj.summary[:150] + ('…' if len(obj.summary) > 150 else '')
        return ''

    def get_uploaded_by_name(self, obj):
        if obj.uploaded_by:
            return obj.uploaded_by.get_full_name() or obj.uploaded_by.username
        return 'System'

    def get_preview_url(self, obj):
        if obj.preview_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.preview_image.url)
            return obj.preview_image.url
        return None

class DocumentDetailSerializer(serializers.ModelSerializer):
    document_type_display = serializers.CharField(source='get_document_type_display', read_only=True)
    category_display = serializers.CharField(source='get_document_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    uploaded_by_name = serializers.SerializerMethodField()
    verified_by_name = serializers.SerializerMethodField()
    preview_url = serializers.SerializerMethodField()
    file_url = serializers.SerializerMethodField()
    pages = DocumentPageSerializer(many=True, read_only=True)
    extracted_fields = ExtractedFieldSerializer(many=True, read_only=True)
    fields = ExtractedFieldSerializer(source='extracted_fields', many=True, read_only=True)
    processing_logs = ProcessingLogSerializer(many=True, read_only=True)
    correction_logs = FieldCorrectionHistorySerializer(many=True, read_only=True)
    # Compatibility aliases
    category = serializers.CharField(source='document_type', read_only=True)
    created_at = serializers.DateTimeField(source='uploaded_at', read_only=True)
    key_points = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = [
            'id', 'filename', 'title', 'document_type', 'document_type_display',
            'category', 'category_display', 'status', 'status_display',
            'confidence', 'ocr_confidence', 'classification_confidence',
            'classification_explanation', 'raw_text', 'file_type',
            'mime_type', 'file_size', 'page_count', 'error_message',
            'is_verified', 'verified_by_name', 'verified_at',
            'uploaded_by', 'uploaded_by_name', 'uploaded_at', 'created_at',
            'preview_url', 'file_url', 'processing_time_ms', 'metadata',
            'summary', 'key_points',
            'pages', 'extracted_fields', 'fields', 'processing_logs',
            'correction_logs', 'updated_at'
        ]

    def get_key_points(self, obj):
        return obj.metadata.get('key_points', []) if obj.metadata else []

    def get_uploaded_by_name(self, obj):
        if obj.uploaded_by:
            return obj.uploaded_by.get_full_name() or obj.uploaded_by.username
        return 'System'

    def get_verified_by_name(self, obj):
        if obj.verified_by:
            return obj.verified_by.get_full_name() or obj.verified_by.username
        return None

    def get_preview_url(self, obj):
        if obj.preview_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.preview_image.url)
            return obj.preview_image.url
        return None

    def get_file_url(self, obj):
        if obj.file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.file.url)
            return obj.file.url
        return None

class DocumentUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ['id', 'filename', 'title', 'file']
        read_only_fields = ['id', 'filename']

    def validate_file(self, value):
        valid_extensions = ['.pdf', '.png', '.jpg', '.jpeg', '.webp', '.tiff', '.bmp']
        ext = os.path.splitext(value.name)[1].lower()
        if ext not in valid_extensions:
            raise serializers.ValidationError(
                f"Unsupported file format '{ext}'. Allowed: PDF, PNG, JPG, JPEG."
            )
        if value.size > 50 * 1024 * 1024:
            raise serializers.ValidationError("File size exceeds 50MB limit.")
        return value

    def create(self, validated_data):
        file_obj = validated_data['file']
        filename = file_obj.name
        ext = os.path.splitext(filename)[1].lower().replace('.', '')
        file_type = 'image' if ext in ['jpg', 'jpeg', 'png', 'webp', 'tiff', 'bmp'] else 'pdf'

        title = validated_data.get('title')
        if not title:
            title = os.path.splitext(filename)[0].replace('_', ' ').replace('-', ' ').title()

        doc = Document.objects.create(
            filename=filename,
            title=title,
            file=file_obj,
            file_type=file_type,
            file_size=file_obj.size,
            mime_type=getattr(file_obj, 'content_type', 'application/octet-stream'),
            uploaded_by=self.context['request'].user if self.context.get('request') and self.context['request'].user.is_authenticated else None
        )
        return doc
