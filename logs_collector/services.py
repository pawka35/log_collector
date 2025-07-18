"""Сервисы приложения log_collector."""

from __future__ import annotations

import base64
from datetime import timezone
from pathlib import Path
from typing import TYPE_CHECKING

from logs_collector.models import FailedLogEntry, LogEntry


if TYPE_CHECKING:
    from django.http.request import HttpRequest


def decode_base64(field: str) -> bytes:
    """Decode a base64 encoded string."""
    if field and isinstance(field, str):
        # Удаляем пробелы и переносы строк
        field = field.strip().replace('\n', '').replace('\r', '')
        # Добавляем padding, если нужно
        missing_padding = len(field) % 4
        if missing_padding:
            field += '=' * (4 - missing_padding)
        return base64.b64decode(field)

    return b''


def get_failed_log_file_path(failed_log_id: int) -> Path:
    """Возвращает путь к файлу с нераспарсенным логом."""
    error_dir_path = Path(FailedLogEntry.FOLDER_NAME)
    error_dir_path.mkdir(parents=True, exist_ok=True)
    return error_dir_path.joinpath(f'log_{failed_log_id}.txt')


def save_log_entry(data: dict) -> None:
    """Сохраняет запись лога в базу данных."""
    LogEntry.objects.create(
        time=data.get('time', ''),
        url=data.get('url', ''),
        method=data.get('method', ''),
        type=data.get('type', ''),
        initiator=data.get('initiator', ''),
        tab_id=data.get('tabId', ''),
        request_id=data.get('requestId', ''),
        request_body=decode_base64(data.get('requestBody', '')),
        response=decode_base64(data.get('response', '')),
        status_code=data.get('statusCode') or '',
        source=data.get('source', ''),
        html=decode_base64(data.get('html', '')),
        response_time=data.get('responseTime', ''),
        employee=data.get('employee', 'unauthorized'),
        ip_address=data['ip'],
    )


def save_failed_log_entry(request: HttpRequest, exception: str, ip: str) -> None:
    """Сохраняет запись неудачного лога в базу данных и файл."""
    failed_log = FailedLogEntry.objects.create(
        raw_data=request.body.decode(errors='ignore') or '', error_message=str(exception), ip_address=ip
    )

    # Сохраняем нераспарсенный лог в файл.
    file_path = get_failed_log_file_path(failed_log.id)

    with file_path.open('w', encoding='utf-8') as f:
        f.write(f'Failed log ID: {failed_log.id}\n')
        f.write(f'Time: {timezone.now().strftime("%d-%m-%Y %HH:%MM:%SS")}\n')
        f.write(f'IP: {ip}\n')
        f.write(f'Error: {exception!s}\n')
        f.write('Raw data:\n')
        try:
            f.write(request.body.decode('utf-8', errors='replace'))
        except Exception:
            f.write(str(request.body))
