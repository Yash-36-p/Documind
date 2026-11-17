from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import ExtractedField, FieldCorrectionHistory
from .serializers import (
    ExtractedFieldSerializer,
    ExtractedFieldCreateUpdateSerializer,
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
        fields = doc.extracted_fields.all()
        serializer = ExtractedFieldSerializer(fields, many=True)
        return Response(serializer.data)

    def post(self, request, doc_id):
        doc = get_object_or_404(Document, id=doc_id)
        if not request.user.is_reviewer_role():
            return Response({"error": "Reviewer permission required to add fields"}, status=status.HTTP_403_FORBIDDEN)

        data = request.data.copy()
        data['document'] = doc.id
        # Map label / value
        if 'field_label' in data and 'field_name' not in data:
            data['field_name'] = data['field_label']
        if 'field_value' in data and 'extracted_value' not in data:
            data['extracted_value'] = data['field_value']

        serializer = ExtractedFieldCreateUpdateSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        field = serializer.save(
            is_corrected=True,
            original_value=data.get('extracted_value', ''),
            confidence=100.0
        )

        FieldCorrectionHistory.objects.create(
            document=doc,
            extracted_field=field,
            field_name=field.field_name,
            field_key=field.field_key,
            previous_value='',
            new_value=field.extracted_value,
            corrected_by=request.user,
            correction_type='field_added',
            notes='Manually added field'
        )

        log_activity(
            AuditLog.Action.FIELD_CREATE,
            user=request.user,
            document=doc,
            request=request,
            details={"field_name": field.field_name, "value": field.extracted_value}
        )

        return Response(ExtractedFieldSerializer(field).data, status=status.HTTP_201_CREATED)


class DocumentFieldDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsReviewerOrAdmin]

    def patch(self, request, pk):
        field = get_object_or_404(ExtractedField, pk=pk)
        old_value = field.extracted_value
        new_value = request.data.get('extracted_value', request.data.get('field_value', old_value))
        notes = request.data.get('notes', '')

        data = request.data.copy()
        if 'field_value' in data:
            data['extracted_value'] = data['field_value']

        serializer = ExtractedFieldCreateUpdateSerializer(field, data=data, partial=True)
        serializer.is_valid(raise_exception=True)

        if str(old_value) != str(new_value):
            field.is_corrected = True
            field.confidence = 100.0 # user verification guarantees correctness
            field.extracted_value = new_value
            field.save()

            FieldCorrectionHistory.objects.create(
                document=field.document,
                extracted_field=field,
                field_name=field.field_name,
                field_key=field.field_key,
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
                    "field_name": field.field_name,
                    "old_value": old_value,
                    "new_value": new_value
                }
            )
        else:
            serializer.save()

        return Response(ExtractedFieldSerializer(field).data)

    def delete(self, request, pk):
        field = get_object_or_404(ExtractedField, pk=pk)
        doc = field.document
        name = field.field_name
        val = field.extracted_value

        FieldCorrectionHistory.objects.create(
            document=doc,
            field_name=name,
            field_key=field.field_key,
            previous_value=val,
            new_value='[DELETED]',
            corrected_by=request.user,
            correction_type='field_deleted'
        )

        log_activity(
            AuditLog.Action.FIELD_DELETE,
            user=request.user,
            document=doc,
            request=request,
            details={"field_name": name, "deleted_value": val}
        )

        field.delete()
        return Response({"message": "Field deleted"}, status=status.HTTP_204_NO_CONTENT)


class DocumentCorrectionHistoryView(generics.ListAPIView):
    serializer_class = FieldCorrectionHistorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        doc_id = self.kwargs.get('doc_id')
        return FieldCorrectionHistory.objects.filter(document_id=doc_id).order_by('-corrected_at')
