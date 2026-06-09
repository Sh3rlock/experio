from django.contrib import admin

from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('action', 'user', 'method', 'path', 'ip_address', 'created_at')
    list_filter = ('method', 'created_at')
    readonly_fields = ('user', 'action', 'path', 'method', 'ip_address', 'extra', 'created_at')
