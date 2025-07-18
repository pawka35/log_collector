"""Представления приложения logs_collector."""

import csv
import json
from typing import Any

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.http.request import HttpRequest
from django.http.response import FileResponse, Http404
from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import csrf_exempt

from logs_collector.forms import FailedLogEntryForm, LogFilterForm
from logs_collector.models import FailedLogEntry, LogEntry
from logs_collector.services import get_failed_log_file_path, save_failed_log_entry, save_log_entry


@csrf_exempt
def receive_log(request: HttpRequest, *args: Any, **kwargs: Any) -> JsonResponse:
    """Receive log data from the client and store it in the database."""
    if request.method != 'POST':
        raise Http404

    custom_header = request.META.get('HTTP_X_CUSTOM_HEADER')
    if custom_header != settings.CUSTOM_HEADER:
        return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

    data = {'ip': request.META.get('REMOTE_ADDR', '')}
    try:
        if request.body:
            data.update(json.loads(request.body.decode()))

        # Проверяем наличи ключа в запросе.
        plugin_key = data.get('pluginKey')
        if plugin_key is None:
            return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)
        if plugin_key != settings.PLUGIN_KEY:
            return JsonResponse({'status': 'error', 'message': 'Invalid key'}, status=403)

        save_log_entry(data)
        return JsonResponse({'status': 'ok'})

    except Exception as e:
        save_failed_log_entry(request, e, data['ip'])
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
    excel_cell_max_length = 32760
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
            f'{log.html[:excel_cell_max_length]}...' if len(log.html) > excel_cell_max_length else log.html,
            log.response_time,
            log.ip_address,
        ])

    return response


@login_required()
def failed_log_list(request: HttpRequest) -> HttpResponse:
    """View to list failed logs."""
    form = FailedLogEntryForm(request, request.GET or None)
    return render(
        request,
        'failed_log.html',
        {
            'form': form,
            'page_obj': form.get_page(),
        },
    )


@login_required
def download_unparsed_log(request: HttpRequest, failed_log_id: int) -> FileResponse:
    """Download unparsed log file."""
    failed_log = get_object_or_404(FailedLogEntry, pk=failed_log_id)
    file_path = get_failed_log_file_path(failed_log.id)
    if not file_path.exists():
        raise Http404('Файл не найден')
    return FileResponse(file_path.open('rb'), as_attachment=True, filename=file_path.name, content_type='text/plain')
