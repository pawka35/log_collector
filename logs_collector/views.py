"""Представления приложения logs_collector."""

import csv
import json
from pathlib import Path
from typing import Any

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.http.request import HttpRequest
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from logs_collector.forms import LogFilterForm
from logs_collector.models import FailedLogEntry, LogEntry
from logs_collector.services import decode_base64


@csrf_exempt
def receive_log(request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
    """Receive log data from the client and store it in the database."""
    ip = request.META.get('REMOTE_ADDR', '')
    try:
        data = json.loads(request.body.decode())

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
            ip_address=ip,
        )
        return JsonResponse({'status': 'ok'})

    except Exception as e:
        FailedLogEntry.objects.create(
            raw_data=request.body.decode(errors='ignore') or '', error_message=str(e), ip_address=ip
        )

        # Сохраняем нераспарсенный лог в файл.
        error_dir = Path('unparsed_logs')
        error_dir.mkdir(parents=True, exist_ok=True)
        timestamp = timezone.now().strftime('%Y%m%d_%H%M%S_%f')
        filename = error_dir / f'log_{timestamp}.txt'

        with filename.open('w', encoding='utf-8') as f:
            f.write(f'Time: {timestamp}\n')
            f.write(f'IP: {ip}\n')
            f.write(f'Error: {e!s}\n')
            f.write('Raw data:\n')
            try:
                f.write(request.body.decode('utf-8', errors='replace'))
            except Exception:
                f.write(str(request.body))

        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


@login_required
def log_list(request: HttpRequest) -> HttpResponse:
    """View to list logs with filtering and sorting."""
    form = LogFilterForm(request, request.GET or None)

    return render(
        request,
        'log_list.html',
        {
            'form': form,
            'page_obj': form.get_page(),
        },
    )


@login_required
def view_log_html(request: HttpRequest, pk: int) -> HttpResponse:
    """View to view log html."""
    log = get_object_or_404(LogEntry, pk=pk)
    html_content = log.html.decode('utf-8', errors='replace')
    return HttpResponse(html_content)


@login_required
def export_logs_csv(request: HttpRequest) -> HttpResponse:
    """Export logs to CSV file."""
    form = LogFilterForm(request, request.GET or None)
    logs = form.get_items()
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="logs.csv"'

    writer = csv.writer(response)
    writer.writerow([
        'employee',
        'received_at',
        'time',
        'url',
        'method',
        'type',
        'initiator',
        'tab_id',
        'request_id',
        'request_body',
        'response',
        'status_code',
        'source',
        'html',
        'response_time',
        'ip_address',
    ])

    for log in logs:
        writer.writerow([
            log.employee,
            log.received_at,
            log.time,
            log.url,
            log.method,
            log.type,
            log.initiator,
            log.tab_id,
            log.request_id,
            log.request_body,
            log.response,
            log.status_code,
            log.source,
            f'{log.html[:32760]}...' if len(log.html) > 32767 else log.html,
            log.response_time,
            log.ip_address,
        ])

    return response
