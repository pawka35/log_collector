"""Формы приложения logs_collector."""

from typing import Any

from django import forms
from django.core.paginator import Page, Paginator
from django.db.models import CharField, EmailField, Q, QuerySet, SlugField, TextChoices, TextField
from django.http.request import HttpRequest

from logs_collector.models import LogEntry


class LogFilterForm(forms.Form):
    """Form for filtering and sorting log entries."""

    class SortChoices(TextChoices):
        """Choices for sorting log entries."""

        INITIATOR = 'initiator'
        RECEIVED_AT = 'received_at'

    sort = forms.ChoiceField(choices=SortChoices.choices, required=False, initial='received_at')
    order = forms.ChoiceField(choices=[('asc', 'Ascending'), ('desc', 'Descending')], required=False, initial='desc')
    search = forms.CharField(required=False, label='Search text')
    ip_address = forms.CharField(required=False, label='IP Address')
    date_from = forms.DateTimeField(
        required=False, label='From date', widget=forms.DateTimeInput(attrs={'type': 'datetime-local'})
    )
    date_to = forms.DateTimeField(
        required=False, label='To date', widget=forms.DateTimeInput(attrs={'type': 'datetime-local'})
    )
    url = forms.CharField(required=False, label='URL')
    initiator = forms.CharField(required=False, label='Initiator')
    request_body = forms.CharField(required=False, label='Request body')
    html = forms.CharField(required=False, label='HTML')
    employee = forms.MultipleChoiceField(required=False, label='Employee')

    def __init__(self, request: HttpRequest, *args: Any, **kwargs: Any) -> None:
        """Initialize the form with request data and set sort field and order."""
        super().__init__(*args, **kwargs)
        self.sort_field = request.GET.get('sort', 'received_at')
        self.sort_order = request.GET.get('order', 'desc')
        self.sort_prefix = '' if self.sort_order == 'asc' else '-'
        self.page_number = request.GET.get('page')
        # Set choices for employee.
        self.fields['employee'].queryset = (
            LogEntry.objects.values_list('employee', flat=True).distinct().order_by('employee')
        )
        self.fields['employee'].choices = [(e, e) for e in self.fields['employee'].queryset if e]

    def _get_text_search_q(self, value: str) -> Q:
        """Возвращает выражение Q для поиска по всем полям, поддерживающим текстовый поиск модели LogEntry."""
        text_field_types = (CharField, TextField, EmailField, SlugField)
        q = Q()

        for field in LogEntry._meta.get_fields():
            if field.concrete and isinstance(field, text_field_types):
                q |= Q(**{f'{field.name}__icontains': value})

        return q

    def filter_queryset(self, queryset: QuerySet) -> QuerySet:
        """Filter the queryset based on form data."""
        cleaned_data = self.cleaned_data

        if cleaned_data['search']:
            queryset = queryset.filter(self._get_text_search_q(cleaned_data['search']))

        if cleaned_data['ip_address']:
            queryset = queryset.filter(ip_address__icontains=cleaned_data['ip_address'])

        if cleaned_data['date_from']:
            queryset = queryset.filter(received_at__gte=cleaned_data['date_from'])
        if cleaned_data['date_to']:
            queryset = queryset.filter(received_at__lte=cleaned_data['date_to'])

        if cleaned_data['url']:
            queryset = queryset.filter(url__icontains=cleaned_data['url'])
        if cleaned_data['initiator']:
            queryset = queryset.filter(initiator__icontains=cleaned_data['initiator'])
        if cleaned_data['request_body']:
            queryset = queryset.filter(requestBody__icontains=cleaned_data['request_body'])
        if cleaned_data['html']:
            queryset = queryset.filter(html__icontains=cleaned_data['html'])
        if cleaned_data.get('employee'):
            queryset = queryset.filter(employee__in=cleaned_data['employee'])

        return queryset

    def order_queryset(self, queryset: QuerySet[LogEntry]) -> QuerySet[LogEntry]:
        """Order the queryset based on the selected sort field and order."""
        return queryset.order_by(f'{self.sort_prefix}{self.sort_field}')

    def get_initial_queryset(self) -> QuerySet[LogEntry]:
        """Get the initial queryset of log entries."""
        return LogEntry.objects.all()

    def get_items(self) -> QuerySet[LogEntry]:
        """Get filtered and sorted log entries based on form data."""
        queryset = self.get_initial_queryset()
        if not self.is_valid():
            return queryset

        queryset = self.filter_queryset(queryset)
        return self.order_queryset(queryset)

    def get_page(self) -> Page:
        """Get a page of log entries based on the form data."""
        paginator = Paginator(self.get_items(), 25)
        return paginator.get_page(self.page_number)
