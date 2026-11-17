import csv
from datetime import timedelta
from django.utils import timezone
from django.db.models import Count, Avg, Q
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions

from apps.documents.models import Document
from apps.extraction.models import ExtractedField, FieldCorrectionHistory
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

        avg_stats = Document.objects.filter(status=Document.Status.COMPLETED).aggregate(
            avg_conf=Avg('confidence'),
            avg_ocr=Avg('ocr_confidence'),
            avg_time=Avg('processing_time_ms')
        )
        avg_conf = round(avg_stats['avg_conf'] or 0.0, 1)
        avg_ocr = round(avg_stats['avg_ocr'] or 0.0, 1)
        avg_time = int(avg_stats['avg_time'] or 0)

        # Document type distribution
        cat_counts = Document.objects.values('document_type').annotate(count=Count('id')).order_by('-count')
        category_dist = []
        for item in cat_counts:
            dtype = item['document_type']
            cnt = item['count']
            pct = round((cnt / total_docs * 100), 1) if total_docs > 0 else 0
            category_dist.append({
                'category': dtype,
                'label': dtype,
                'count': cnt,
                'percentage': pct
            })

        total_corrections = FieldCorrectionHistory.objects.count()
        total_fields = ExtractedField.objects.count()
        corrected_fields = ExtractedField.objects.filter(is_corrected=True).count()
        accuracy_rate = round(((total_fields - corrected_fields) / max(1, total_fields)) * 100, 1)

        today = timezone.now().date()
        daily_trends = []
        for i in range(6, -1, -1):
            day = today - timedelta(days=i)
            day_count = Document.objects.filter(
                uploaded_at__date=day
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
            'average_confidence': avg_conf,
            'average_ocr_confidence': avg_ocr,
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
            Q(filename__icontains=query) |
            Q(title__icontains=query) |
            Q(raw_text__icontains=query) |
            Q(extracted_fields__field_name__icontains=query) |
            Q(extracted_fields__extracted_value__icontains=query)
        ).distinct()[:50]

        results = []
        for doc in docs:
            snippet = ''
            if doc.raw_text:
                idx = doc.raw_text.lower().find(query.lower())
                if idx != -1:
                    start = max(0, idx - 60)
                    end = min(len(doc.raw_text), idx + len(query) + 60)
                    snippet = f"...{doc.raw_text[start:end]}..."
                else:
                    snippet = doc.raw_text[:120] + "..."

            matched_fields = []
            for f in doc.extracted_fields.all():
                if query.lower() in f.extracted_value.lower() or query.lower() in f.field_name.lower():
                    matched_fields.append({
                        'label': f.field_name,
                        'value': f.extracted_value
                    })

            results.append({
                'id': doc.id,
                'filename': doc.filename,
                'title': doc.title or doc.filename,
                'document_type': doc.document_type,
                'category_display': doc.get_document_type_display(),
                'status': doc.status,
                'status_display': doc.get_status_display(),
                'confidence': doc.confidence,
                'ocr_confidence': doc.ocr_confidence,
                'uploaded_at': doc.uploaded_at,
                'created_at': doc.uploaded_at,
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
        doc_type = request.query_params.get('document_type') or request.query_params.get('category')
        status_param = request.query_params.get('status')
        verified = request.query_params.get('verified')

        queryset = Document.objects.all().prefetch_related('extracted_fields')

        if doc_id:
            queryset = queryset.filter(id=doc_id)
        else:
            if doc_type and doc_type != 'all':
                queryset = queryset.filter(document_type__iexact=doc_type)
            if status_param and status_param != 'all':
                queryset = queryset.filter(status__iexact=status_param)
            if verified in ['true', '1']:
                queryset = queryset.filter(is_verified=True)

        response = HttpResponse(content_type='text/csv')
        filename = f"documind_export_{timezone.now().strftime('%Y%m%d_%H%M%S')}.csv"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'

        writer = csv.writer(response)
        writer.writerow([
            'Document ID', 'Filename', 'Document Type', 'Status',
            'Confidence (%)', 'OCR Confidence (%)', 'Is Verified',
            'Uploaded By', 'Uploaded At',
            'Invoice Number', 'Vendor', 'Invoice Date', 'Total Amount',
            'All Extracted Fields'
        ])

        for doc in queryset:
            fields_map = {f.field_name.lower(): f.extracted_value for f in doc.extracted_fields.all()}
            all_fields_str = "; ".join([f"{f.field_name}: {f.extracted_value}" for f in doc.extracted_fields.all()])

            # Find common fields
            inv_num = fields_map.get('invoice number', fields_map.get('invoice / reference #', ''))
            vendor = fields_map.get('vendor', fields_map.get('vendor / organization', fields_map.get('vendor / issuer', '')))
            inv_date = fields_map.get('invoice date', fields_map.get('document date', fields_map.get('date', '')))
            total = fields_map.get('total amount', '')

            writer.writerow([
                doc.id,
                doc.filename,
                doc.document_type,
                doc.status,
                f"{doc.confidence}%",
                f"{doc.ocr_confidence}%",
                'Yes' if doc.is_verified else 'No',
                doc.uploaded_by.username if doc.uploaded_by else 'System',
                doc.uploaded_at.strftime('%Y-%m-%d %H:%M:%S'),
                inv_num,
                vendor,
                inv_date,
                total,
                all_fields_str
            ])

        log_activity(
            AuditLog.Action.EXPORT,
            user=request.user,
            request=request,
            details={"count": queryset.count(), "doc_id": doc_id or 'bulk'}
        )

        return response
