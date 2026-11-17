"""
DocuMind URL Configuration
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView
)

from apps.documents.views import (
    DocumentListCreateView,
    DocumentDetailView,
    DocumentReprocessView,
    DocumentVerifyView,
    DocumentChangeCategoryView,
    DocumentDownloadView
)
from apps.extraction.views import (
    DocumentFieldsView,
    DocumentFieldDetailView,
    DocumentCorrectionHistoryView
)
from apps.analytics.views import (
    DashboardStatsView,
    GlobalSearchView,
    ExportCsvView
)
from apps.audit.views import AuditLogListView

urlpatterns = [
    path('admin/', admin.site.urls),

    # 1. Authentication
    path('api/auth/', include('apps.users.urls')),

    # 2. Document Management
    path('api/documents/', DocumentListCreateView.as_view(), name='document_list_create'),
    path('api/documents/<uuid:pk>/', DocumentDetailView.as_view(), name='document_detail'),
    path('api/documents/<uuid:pk>/reprocess/', DocumentReprocessView.as_view(), name='document_reprocess'),
    path('api/documents/<uuid:pk>/verify/', DocumentVerifyView.as_view(), name='document_verify'),
    path('api/documents/<uuid:pk>/category/', DocumentChangeCategoryView.as_view(), name='document_change_category'),
    path('api/documents/<uuid:pk>/download/', DocumentDownloadView.as_view(), name='document_download'),

    # 4 & 6. Field Extraction & Review / Correction
    path('api/documents/<uuid:doc_id>/fields/', DocumentFieldsView.as_view(), name='document_fields'),
    path('api/documents/<uuid:doc_id>/corrections/', DocumentCorrectionHistoryView.as_view(), name='document_corrections'),
    path('api/fields/<uuid:pk>/', DocumentFieldDetailView.as_view(), name='field_detail'),

    # 7. Search, Analytics, CSV Export & Audit Logs
    path('api/analytics/dashboard/', DashboardStatsView.as_view(), name='dashboard_stats'),
    path('api/search/', GlobalSearchView.as_view(), name='global_search'),
    path('api/export/csv/', ExportCsvView.as_view(), name='export_csv'),
    path('api/audit/logs/', AuditLogListView.as_view(), name='audit_logs'),

    # API Documentation (Swagger / OpenAPI)
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
