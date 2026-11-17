import os
from rest_framework import serializers
from .models import Document, DocumentPage
from apps.extraction.serializers import DocumentFieldSerializer, FieldCorrectionHistorySerializer

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
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    uploaded_by_name = serializers.SerializerMethodField()
    preview_url = serializers.SerializerMethodField()
    fields_count = serializers.IntegerField(source='fields.count', read_only=True)

    class Meta:
        model = Document
        fields = [
            'id', 'title', 'filename', 'file_type', 'file_size', 'page_count',
            'status', 'status_display', 'category', 'category_display',
            'classification_confidence', 'ocr_confidence', 'is_verified',
            'uploaded_by_name', 'preview_url', 'fields_count',
            'created_at', 'updated_at'
        ]

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
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    uploaded_by_name = serializers.SerializerMethodField()
    verified_by_name = serializers.SerializerMethodField()
    preview_url = serializers.SerializerMethodField()
    file_url = serializers.SerializerMethodField()
    pages = DocumentPageSerializer(many=True, read_only=True)
    fields = DocumentFieldSerializer(many=True, read_only=True)
    correction_logs = FieldCorrectionHistorySerializer(many=True, read_only=True)

    class Meta:
        model = Document
        fields = [
            'id', 'title', 'filename', 'file_type', 'mime_type', 'file_size',
            'page_count', 'status', 'status_display', 'error_message',
            'category', 'category_display', 'classification_confidence',
            'classification_explanation', 'ocr_confidence', 'raw_text',
            'is_verified', 'verified_by_name', 'verified_at',
            'uploaded_by_name', 'preview_url', 'file_url',
            'processing_time_ms', 'metadata',
            'pages', 'fields', 'correction_logs',
            'created_at', 'updated_at'
        ]

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
        fields = ['id', 'title', 'file']
        read_only_fields = ['id']

    def validate_file(self, value):
        valid_extensions = ['.pdf', '.png', '.jpg', '.jpeg', '.webp', '.tiff', '.bmp']
        ext = os.path.splitext(value.name)[1].lower()
        if ext not in valid_extensions:
            raise serializers.ValidationError(
                f"Unsupported file format '{ext}'. Allowed: PDF, PNG, JPG, JPEG."
            )
        # Limit to 50MB
        if value.size > 50 * 1024 * 1024:
            raise serializers.ValidationError("File size exceeds 50MB limit.")
        return value

    def create(self, validated_data):
        file_obj = validated_data['file']
        ext = os.path.splitext(file_obj.name)[1].lower().replace('.', '')
        if ext in ['jpg', 'jpeg', 'png', 'webp', 'tiff', 'bmp']:
            file_type = 'image'
        else:
            file_type = 'pdf'

        title = validated_data.get('title')
        if not title:
            title = os.path.splitext(file_obj.name)[0].replace('_', ' ').replace('-', ' ').title()

        doc = Document.objects.create(
            title=title,
            file=file_obj,
            file_type=file_type,
            file_size=file_obj.size,
            mime_type=getattr(file_obj, 'content_type', 'application/octet-stream'),
            uploaded_by=self.context['request'].user if self.context.get('request') and self.context['request'].user.is_authenticated else None
        )
        return doc

class DocumentClassificationUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ['category']
