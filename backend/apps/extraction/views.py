from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import DocumentField, FieldCorrectionHistory
from .serializers import (
    DocumentFieldSerializer,
    DocumentFieldCreateUpdateSerializer,
    FieldCorrectionHistorySerializer
)
from apps.documents.models import Document
from apps.users.permissions import IsReviewerOrAdmin, IsViewerOrAboveReadOnly
from apps.audit.utils import log_activity
from apps.audit.models import AuditLog

class DocumentFieldsView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsViewerOrAboveReadOnly]

    def get(self, request, doc_id):
        doc = get_object_or_404(Document, id=doc_id)
        fields = doc.fields.all()
        serializer = DocumentFieldSerializer(fields, many=True)
        return Response(serializer.data)

    def post(self, request, doc_id):
        doc = get_object_or_404(Document, id=doc_id)
        if not request.user.is_reviewer_role():
            return Response({"error": "Reviewer permission required to add fields"}, status=status.HTTP_403_FORBIDDEN)

        data = request.data.copy()
        data['document'] = doc.id
        serializer = DocumentFieldCreateUpdateSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        field = serializer.save(
            is_corrected=True, # user manually added it
            original_value=data.get('field_value', ''),
            confidence=100.0
        )

        # Log creation
        FieldCorrectionHistory.objects.create(
            document=doc,
            document_field=field,
            field_key=field.field_key,
            field_label=field.field_label,
            previous_value='',
            new_value=field.field_value,
            corrected_by=request.user,
            correction_type='field_added',
            notes='Manually added field'
        )

        log_activity(
            AuditLog.Action.FIELD_CREATE,
            user=request.user,
            document=doc,
            request=request,
            details={"field_key": field.field_key, "value": field.field_value}
        )

        return Response(DocumentFieldSerializer(field).data, status=status.HTTP_201_CREATED)


class DocumentFieldDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsReviewerOrAdmin]

    def patch(self, request, pk):
        field = get_object_or_404(DocumentField, pk=pk)
        old_value = field.field_value
        new_value = request.data.get('field_value', old_value)
        notes = request.data.get('notes', '')

        serializer = DocumentFieldCreateUpdateSerializer(field, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        if old_value != new_value:
            field.is_corrected = True
            # Manual edit sets confidence to 100%
            field.confidence = 100.0
            field.save()

            # Record correction log
            FieldCorrectionHistory.objects.create(
                document=field.document,
                document_field=field,
                field_key=field.field_key,
                field_label=field.field_label,
                previous_value=old_value,
                new_value=new_value,
                corrected_by=request.user,
                correction_type='manual_edit',
                notes=notes or 'Value updated by user'
            )

            log_activity(
                AuditLog.Action.FIELD_EDIT,
                user=request.user,
                document=field.document,
                request=request,
                details={
                    "field_key": field.field_key,
                    "old_value": old_value,
                    "new_value": new_value
                }
            )
        else:
            serializer.save()

        return Response(DocumentFieldSerializer(field).data)

    def delete(self, request, pk):
        field = get_object_or_404(DocumentField, pk=pk)
        doc = field.document
        field_key = field.field_key
        field_val = field.field_value

        FieldCorrectionHistory.objects.create(
            document=doc,
            field_key=field_key,
            field_label=field.field_label,
            previous_value=field_val,
            new_value='[DELETED]',
            corrected_by=request.user,
            correction_type='field_deleted'
        )

        log_activity(
            AuditLog.Action.FIELD_DELETE,
            user=request.user,
            document=doc,
            request=request,
            details={"field_key": field_key, "deleted_value": field_val}
        )

        field.delete()
        return Response({"message": "Field deleted"}, status=status.HTTP_204_NO_CONTENT)


class DocumentCorrectionHistoryView(generics.ListAPIView):
    serializer_class = FieldCorrectionHistorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        doc_id = self.kwargs.get('doc_id')
        return FieldCorrectionHistory.objects.filter(document_id=doc_id).order_by('-corrected_at')
