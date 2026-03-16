from django.contrib import admin
from .models import Ticket, ScanLog

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('code', 'event_name', 'is_used', 'created_at', 'used_at')
    list_filter = ('is_used', 'event_name')
    search_fields = ('code',)

@admin.register(ScanLog)
class ScanLogAdmin(admin.ModelAdmin):
    list_display = ('scanned_text', 'is_successful', 'message', 'scanned_at')
    list_filter = ('is_successful',)