"""Admin interface for logs_collector app."""

from django.contrib import admin

from .models import FailedLogEntry, LogEntry


@admin.register(LogEntry)
class LogEntryAdmin(admin.ModelAdmin):
    """Admin interface for LogEntry model."""

    SHORT_STRING_LENGTH = 50

    list_display = ('time', 'short_url', 'method', 'status_code', 'received_at', 'ip_address')
    search_fields = ('url', 'method', 'status_code', 'ip_address')
    list_filter = ('method', 'status_code')
    list_display_links = ('time', 'short_url', 'method', 'status_code', 'received_at', 'ip_address')

    def short_url(self, obj: LogEntry) -> str:
        """Return a shortened version of the URL for display."""
        return (
            (obj.url[: self.SHORT_STRING_LENGTH] + '...')
            if obj.url and len(obj.url) > self.SHORT_STRING_LENGTH
            else obj.url
        )

    short_url.short_description = 'url'


@admin.register(FailedLogEntry)
class FailedLogEntryAdmin(admin.ModelAdmin):
    """Admin interface for FailedLogEntry model."""

    list_display = ('error_message', 'received_at', 'ip_address')
    search_fields = ('error_message', 'ip_address')
