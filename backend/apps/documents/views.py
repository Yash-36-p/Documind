import os
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.http import FileResponse, Http404
from django.utils import timezone
from django.db.models import Q

from .models import Document
from .serializers import (
    DocumentListSerializer,
    DocumentDetailSerializer,
    DocumentUploadSerializer,
)
from .services import queue_document_processing
from apps.users.permissions import IsReviewerOrAdmin, IsViewerOrAboveReadOnly
from apps.audit.utils import log_activity
from apps.audit.models import AuditLog
from apps.extraction.models import FieldCorrectionHistory

class DocumentListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated, IsViewerOrAboveReadOnly]
    parser_classes = [MultiPartParser, FormParser]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return DocumentUploadSerializer
        return DocumentListSerializer

    def get_queryset(self):
        queryset = Document.objects.all().prefetch_related('extracted_fields')

        # Query filters
        search = self.request.query_params.get('search')
        doc_type = self.request.query_params.get('document_type') or self.request.query_params.get('category')
        doc_status = self.request.query_params.get('status')
        verified = self.request.query_params.get('verified')
        min_conf = self.request.query_params.get('min_confidence')

        if search:
            queryset = queryset.filter(
                Q(filename__icontains=search) |
                Q(title__icontains=search) |
                Q(raw_text__icontains=search) |
                Q(extracted_fields__field_name__icontains=search) |
                Q(extracted_fields__extracted_value__icontains=search)
            ).distinct()

        if doc_type and doc_type != 'all':
            queryset = queryset.filter(document_type__iexact=doc_type)

        if doc_status and doc_status != 'all':
            queryset = queryset.filter(status__iexact=doc_status)

        if verified in ['true', '1']:
            queryset = queryset.filter(is_verified=True)
        elif verified in ['false', '0']:
            queryset = queryset.filter(is_verified=False)

        if min_conf:
            try:
                queryset = queryset.filter(confidence__gte=float(min_conf))
            except ValueError:
                pass

        return queryset

    def perform_create(self, serializer):
        doc = serializer.save()
        log_activity(
            AuditLog.Action.UPLOAD,
            user=self.request.user,
            document=doc,
            request=self.request,
            details={"filename": doc.filename, "size": doc.file_size}
        )
        queue_document_processing(doc.id)


class DocumentDetailView(generics.RetrieveDestroyAPIView):
    queryset = Document.objects.all().prefetch_related('extracted_fields', 'pages', 'processing_logs', 'correction_logs')
    serializer_class = DocumentDetailSerializer
    permission_classes = [permissions.IsAuthenticated, IsViewerOrAboveReadOnly]

    def perform_destroy(self, instance):
        title = instance.filename or instance.title
        doc_id = instance.id
        if instance.file and os.path.exists(instance.file.path):
            try:
                os.remove(instance.file.path)
            except OSError:
                pass

        log_activity(
            AuditLog.Action.DELETE,
            user=self.request.user,
            details={"document_id": doc_id, "title": title},
            request=self.request
        )
        instance.delete()


class DocumentReprocessView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsReviewerOrAdmin]

    def post(self, request, pk):
        try:
            doc = Document.objects.get(pk=pk)
        except Document.DoesNotExist:
            return Response({"error": "Document not found"}, status=status.HTTP_404_NOT_FOUND)

        log_activity(
            AuditLog.Action.PROCESS_START,
            user=request.user,
            document=doc,
            request=request,
            details={"reason": "Manual re-process requested"}
        )

        task_id = queue_document_processing(doc.id)
        return Response({
            "message": "Document re-processing initiated",
            "task_id": str(task_id) if task_id else None,
            "status": doc.status
        })


class DocumentVerifyView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsReviewerOrAdmin]

    def post(self, request, pk):
        try:
            doc = Document.objects.get(pk=pk)
        except Document.DoesNotExist:
            return Response({"error": "Document not found"}, status=status.HTTP_404_NOT_FOUND)

        is_verified = request.data.get('is_verified', True)
        doc.is_verified = bool(is_verified)
        if doc.is_verified:
            doc.verified_by = request.user
            doc.verified_at = timezone.now()
        else:
            doc.verified_by = None
            doc.verified_at = None
        doc.save(update_fields=['is_verified', 'verified_by', 'verified_at'])

        log_activity(
            AuditLog.Action.VERIFY,
            user=request.user,
            document=doc,
            request=request,
            details={"is_verified": doc.is_verified}
        )

        return Response({
            "message": "Verification status updated",
            "is_verified": doc.is_verified,
            "verified_by": doc.verified_by.get_full_name() or doc.verified_by.username if doc.verified_by else None,
            "verified_at": doc.verified_at
        })


class DocumentChangeCategoryView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsReviewerOrAdmin]

    def patch(self, request, pk):
        try:
            doc = Document.objects.get(pk=pk)
        except Document.DoesNotExist:
            return Response({"error": "Document not found"}, status=status.HTTP_404_NOT_FOUND)

        new_doc_type = request.data.get('document_type') or request.data.get('category')
        
        # Check against Document.DocumentType values or matching case-insensitively
        matched_val = None
        for val in Document.DocumentType.values:
            if val.lower() == new_doc_type.lower() or val.lower().startswith(new_doc_type.lower()):
                matched_val = val
                break

        if not matched_val:
            return Response({"error": f"Invalid document type '{new_doc_type}'"}, status=status.HTTP_400_BAD_REQUEST)

        prev_type = doc.document_type
        doc.document_type = matched_val
        doc.classification_confidence = 100.0
        doc.save(update_fields=['document_type', 'classification_confidence'])

        FieldCorrectionHistory.objects.create(
            document=doc,
            field_name='Document Type',
            field_key='document_type',
            previous_value=prev_type,
            new_value=matched_val,
            corrected_by=request.user,
            correction_type='classification_override',
            notes=request.data.get('notes', 'Manual type override')
        )

        log_activity(
            AuditLog.Action.CLASSIFICATION_CHANGE,
            user=request.user,
            document=doc,
            request=request,
            details={"previous": prev_type, "new": matched_val}
        )

        return Response({
            "message": "Document type updated successfully",
            "document_type": doc.document_type,
            "category": doc.document_type,
            "category_display": doc.get_document_type_display()
        })


class DocumentDownloadView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        try:
            doc = Document.objects.get(pk=pk)
        except Document.DoesNotExist:
            raise Http404

        if not doc.file or not os.path.exists(doc.file.path):
            raise Http404("File not found on storage")

        response = FileResponse(open(doc.file.path, 'rb'), as_attachment=True, filename=doc.filename)
        return response
