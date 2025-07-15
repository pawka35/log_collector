"""logs_collector.apps."""

from django.apps import AppConfig


class LogsCollectorConfig(AppConfig):
    """Configuration for the logs collector app."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'logs_collector'
