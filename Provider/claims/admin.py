from django.contrib import admin
from .models import Claim, ClaimDocument, ClaimStatusHistory

@admin.register(Claim)
class ClaimAdmin(admin.ModelAdmin):
    """Admin interface for Claim model"""
    
    list_display = (
        'claim_number', 'patient', 'provider', 'status', 'priority',
        'amount_requested', 'amount_approved', 'date_submitted'
    )
    list_filter = ('status', 'priority', 'date_submitted', 'provider')
    search_fields = (
        'claim_number', 'patient__username', 'provider__username',
        'diagnosis_description', 'procedure_description'
    )
    readonly_fields = ('claim_number', 'date_submitted', 'date_updated')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('claim_number', 'patient', 'provider', 'status', 'priority')
        }),
        ('Medical Information', {
            'fields': (
                'diagnosis_code', 'diagnosis_description',
                'procedure_code', 'procedure_description',
                'date_of_service'
            )
        }),
        ('Financial Information', {
            'fields': ('amount_requested', 'amount_approved')
        }),
        ('Provider Information', {
            'fields': ('provider_npi', 'provider_tax_id')
        }),
        ('Additional Information', {
            'fields': ('notes', 'rejection_reason')
        }),
        ('Timestamps', {
            'fields': ('date_submitted', 'date_updated', 'date_processed'),
            'classes': ('collapse',)
        }),
    )
    
    date_hierarchy = 'date_submitted'


@admin.register(ClaimDocument)
class ClaimDocumentAdmin(admin.ModelAdmin):
    """Admin interface for ClaimDocument model"""
    
    list_display = ('claim', 'document_type', 'filename', 'uploaded_at', 'uploaded_by')
    list_filter = ('document_type', 'uploaded_at')
    search_fields = ('claim__claim_number', 'filename', 'uploaded_by__username')
    readonly_fields = ('uploaded_at',)


@admin.register(ClaimStatusHistory)
class ClaimStatusHistoryAdmin(admin.ModelAdmin):
    """Admin interface for ClaimStatusHistory model"""
    
    list_display = ('claim', 'previous_status', 'new_status', 'changed_by', 'changed_at')
    list_filter = ('previous_status', 'new_status', 'changed_at')
    search_fields = ('claim__claim_number', 'changed_by__username')
    readonly_fields = ('changed_at',)
    
    date_hierarchy = 'changed_at'
