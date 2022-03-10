from django.views.generic import ListView, DetailView, UpdateView
from django_tables2 import RequestConfig
from django_tables2.export.export import TableExport

from core.utils import get_filename_with_timestamps

class BaseListView(ListView):
    export_filename = None

    def get_queryset(self, *args, **kwargs):

        if self.request.user.is_staff:
            # qs = self.model.objects.filter(**kwargs)
            qs = self.model.objects.all()
        else:
            qs = self.model.objects.filter(**kwargs)

        self.filter = self.filterset_class(self.request.GET, queryset=qs)
        return self.filter.qs

    def get_context_data(self, queryset, **kwargs):
        context = super(BaseListView, self).get_context_data()
        filter = self.filterset_class(self.request.GET, queryset=queryset)
        table = self.table_class(filter.qs)
        RequestConfig(self.request, paginate={"per_page": self.get_pagination()}).configure(table)
        context[self.context_filter_name]=filter
        context[self.context_table_name]=table
        return context

    def get_pagination(self):
        pagination = self.request.GET.get('pagination')
        if pagination:
            return int(pagination)
        return self.paginate_by


    def get_export_response(self, request, **kwargs):
        try:
            export_format = request.GET.get("_export", None)
            if TableExport.is_valid_format(export_format):
                filter = self.filterset_class(request.GET, queryset=self.object_list)
                export_table = self.table_class_export(filter.qs)
                exporter = TableExport(export_format, export_table)
                filename = get_filename_with_timestamps(self.export_filename)
                return True, exporter.response("{}.{}".format(filename, export_format))

        except Exception as e:
            print('Error, getting export response:{}'.format(str(e)))
            return False, None
        return False, None


class BaseDetailView(DetailView):
    def get_queryset(self, **kwargs):

        if self.request.user.is_staff:
            return self.model.objects.filter(id=kwargs['id'])

        return self.model.objects.filter(**kwargs)


class BaseUpdateView(UpdateView):
    def get_queryset(self, **kwargs):

        if self.request.user.is_staff:
            return self.model.objects.filter(id=kwargs['id'])

        return self.model.objects.filter(**kwargs)