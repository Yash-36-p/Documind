import csv
import io
from datetime import timedelta
from django.utils import timezone
from django.db.models import Count, Avg, Q
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status

from apps.documents.models import Document
from apps.documents.serializers import DocumentListSerializer
from apps.extraction.models import DocumentField, FieldCorrectionHistory
from apps.audit.utils import log_activity
from apps.audit.models import AuditLog

class DashboardStatsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        total_docs = Document.objects.count()
        completed = Document.objects.filter(status=Document.Status.COMPLETED).count()
        processing = Document.objects.filter(status=Document.Status.PROCESSING).count()
        failed = Document.objects.filter(status=Document.Status.FAILED).count()
        pending = Document.objects.filter(status=Document.Status.PENDING).count()
        verified = Document.objects.filter(is_verified=True).count()

        # Confidence averages
        avg_stats = Document.objects.filter(status=Document.Status.COMPLETED).aggregate(
            avg_ocr=Avg('ocr_confidence'),
            avg_class=Avg('classification_confidence'),
            avg_time=Avg('processing_time_ms')
        )
        avg_ocr = round(avg_stats['avg_ocr'] or 0.0, 1)
        avg_class = round(avg_stats['avg_class'] or 0.0, 1)
        avg_time = int(avg_stats['avg_time'] or 0)

        # Category distribution
        cat_counts = Document.objects.values('category').annotate(count=Count('id')).order_by('-count')
        category_map = dict(Document.Category.choices)
        category_dist = []
        for item in cat_counts:
            cat_code = item['category']
            cnt = item['count']
            pct = round((cnt / total_docs * 100), 1) if total_docs > 0 else 0
            category_dist.append({
                'category': cat_code,
                'label': category_map.get(cat_code, cat_code.title()),
                'count': cnt,
                'percentage': pct
            })

        # Correction counts
        total_corrections = FieldCorrectionHistory.objects.count()
        total_fields = DocumentField.objects.count()
        corrected_fields = DocumentField.objects.filter(is_corrected=True).count()
        accuracy_rate = round(((total_fields - corrected_fields) / max(1, total_fields)) * 100, 1)

        # 7-day trend
        today = timezone.now().date()
        daily_trends = []
        for i in range(6, -1, -1):
            day = today - timedelta(days=i)
            day_count = Document.objects.filter(
                created_at__date=day
            ).count()
            daily_trends.append({
                'date': day.strftime('%b %d'),
                'count': day_count
            })

        return Response({
            'total_documents': total_docs,
            'completed_documents': completed,
            'processing_documents': processing,
            'failed_documents': failed,
            'pending_documents': pending,
            'verified_documents': verified,
            'average_ocr_confidence': avg_ocr,
            'average_classification_confidence': avg_class,
            'average_processing_time_ms': avg_time,
            'accuracy_rate': accuracy_rate,
            'total_fields_extracted': total_fields,
            'total_corrections': total_corrections,
            'category_distribution': category_dist,
            'daily_trends': daily_trends
        })


class GlobalSearchView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        query = request.query_params.get('q', '').strip()
        if not query:
            return Response({'query': '', 'results': []})

        docs = Document.objects.filter(
            Q(title__icontains=query) |
            Q(raw_text__icontains=query) |
            Q(fields__field_value__icontains=query)
        ).distinct()[:50]

        results = []
        for doc in docs:
            # Generate snippet highlight
            snippet = ''
            if doc.raw_text:
                idx = doc.raw_text.lower().find(query.lower())
                if idx != -1:
                    start = max(0, idx - 60)
                    end = min(len(doc.raw_text), idx + len(query) + 60)
                    snippet = f"...{doc.raw_text[start:end]}..."
                else:
                    snippet = doc.raw_text[:120] + "..."

            # Matched fields
            matched_fields = []
            for f in doc.fields.all():
                if query.lower() in f.field_value.lower() or query.lower() in f.field_label.lower():
                    matched_fields.append({
                        'label': f.field_label,
                        'value': f.field_value
                    })

            results.append({
                'id': str(doc.id),
                'title': doc.title,
                'category': doc.category,
                'category_display': doc.get_category_display(),
                'status': doc.status,
                'status_display': doc.get_status_display(),
                'ocr_confidence': doc.ocr_confidence,
                'created_at': doc.created_at,
                'snippet': snippet,
                'matched_fields': matched_fields
            })

        return Response({
            'query': query,
            'count': len(results),
            'results': results
        })


class ExportCsvView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        doc_id = request.query_params.get('doc_id')
        category = request.query_params.get('category')
        status_param = request.query_params.get('status')
        verified = request.query_params.get('verified')

        queryset = Document.objects.all().prefetch_related('fields')

        if doc_id:
            queryset = queryset.filter(id=doc_id)
        else:
            if category and category != 'all':
                queryset = queryset.filter(category=category)
            if status_param and status_param != 'all':
                queryset = queryset.filter(status=status_param)
            if verified in ['true', '1']:
                queryset = queryset.filter(is_verified=True)

        response = HttpResponse(content_type='text/csv')
        filename = f"documind_export_{timezone.now().strftime('%Y%m%d_%H%M%S')}.csv"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'

        writer = csv.writer(response)
        # Header row
        writer.writerow([
            'Document ID', 'Title', 'Filename', 'Category', 'Status',
            'OCR Confidence (%)', 'Classification Confidence (%)',
            'Is Verified', 'Page Count', 'File Size (Bytes)',
            'Uploaded By', 'Created At',
            'Invoice / Ref #', 'Total Amount', 'Document Date',
            'Vendor / Organization', 'Email', 'Phone', 'All Extracted Fields'
        ])

        for doc in queryset:
            fields_dict = {f.field_key: f.field_value for f in doc.fields.all()}
            all_fields_str = "; ".join([f"{f.field_label}: {f.field_value}" for f in doc.fields.all()])

            writer.writerow([
                str(doc.id),
                doc.title,
                doc.filename,
                doc.get_category_display(),
                doc.get_status_display(),
                doc.ocr_confidence,
                doc.classification_confidence,
                'Yes' if doc.is_verified else 'No',
                doc.page_count,
                doc.file_size,
                doc.uploaded_by.username if doc.uploaded_by else 'System',
                doc.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                fields_dict.get('invoice_number', fields_dict.get('id_number', '')),
                fields_dict.get('total_amount', ''),
                fields_dict.get('issue_date', fields_dict.get('document_date', '')),
                fields_dict.get('organization_name', ''),
                fields_dict.get('email', ''),
                fields_dict.get('phone', ''),
                all_fields_str
            ])

        log_activity(
            AuditLog.Action.EXPORT,
            user=request.user,
            request=request,
            details={"count": queryset.count(), "doc_id": doc_id or 'bulk'}
        )

        return response
