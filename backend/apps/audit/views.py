from rest_framework import generics, permissions
from .models import AuditLog
from .serializers import AuditLogSerializer

class AuditLogListView(generics.ListAPIView):
    serializer_class = AuditLogSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = AuditLog.objects.all()

        action = self.request.query_params.get('action')
        doc_id = self.request.query_params.get('document_id')
        user_id = self.request.query_params.get('user_id')

        if action:
            queryset = queryset.filter(action=action)
        if doc_id:
            queryset = queryset.filter(document_id=doc_id)
        if user_id:
            queryset = queryset.filter(user_id=user_id)

        return queryset[:200]
