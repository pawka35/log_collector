"""Модели приложения logs_collector."""

from django.db import models
from django.utils import timezone


class LogEntry(models.Model):
    """Модель для хранения записей логов."""

    # Данные из лога.
    time = models.CharField(max_length=255, default='', blank=True)
    url = models.TextField(default='', blank=True)
    method = models.CharField(max_length=10, default='', blank=True)
    type = models.CharField(max_length=50, default='', blank=True)
    initiator = models.CharField(max_length=255, default='', blank=True)
    tab_id = models.CharField(max_length=100, default='', blank=True)
    request_id = models.CharField(max_length=100, default='', blank=True)
    request_body = models.BinaryField(null=True, blank=True)
    response = models.BinaryField(null=True, blank=True)
    status_code = models.CharField(max_length=10, default='', blank=True)
    source = models.CharField(max_length=255, default='', blank=True)
    html = models.BinaryField(null=True, blank=True)
    response_time = models.CharField(max_length=255, default='', blank=True)
    employee = models.CharField(max_length=255)

    # Дополнительная информация.
    received_at = models.DateTimeField(default=timezone.now, db_index=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True, db_index=True)

    class Meta:
        """Meta class for LogEntry model."""

        ordering = ('-received_at',)
        indexes = [
            models.Index(fields=['ip_address']),
            models.Index(fields=['received_at']),
            models.Index(fields=['url']),
        ]

    def __str__(self) -> str:
        """Строковое представление для LogEntry."""
        return f'{self.ip_address} | {self.url} | {self.received_at:%Y-%m-%d %H:%M:%S}'


class FailedLogEntry(models.Model):
    """Модель для хранения неудачных попыток записи логов."""

    raw_data = models.TextField()  # если будет ошибка \"Data too long\", заменить на max_length=16777215
    error_message = models.TextField()
    received_at = models.DateTimeField(default=timezone.now)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        """Meta class for FailedLogEntry model."""

        ordering = ('-received_at',)

    def __str__(self) -> str:
        """Строковое представление для FailedLogEntry."""
        return f'FAILED {self.received_at:%Y-%m-%d %H:%M:%S} | {self.error_message[:80]}'
