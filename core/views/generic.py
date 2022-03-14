from django.views.generic import ListView, DetailView, UpdateView
from django_tables2 import RequestConfig
from django_tables2.export.export import TableExport
from django.shortcuts import  render

from core.utils import get_filename_with_timestamps

class BaseListView(ListView):

    context_filter_name = 'filter'
    context_table_name = 'table'
    paginate_by = 10

    #Export file
    export_filename = 'file'

    def get(self, request,*args, **kwargs):
        self.object_list = self.get_queryset(*args, **kwargs)
        context = self.get_context_data(*args, **kwargs)

        #Exporting to csv
        exported, response = self.get_export_response(request)
        if exported:
            return response

        return render(request, self.template_name, context)

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