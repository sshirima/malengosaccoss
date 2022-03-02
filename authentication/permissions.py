from django.shortcuts import render
from django.contrib.auth.mixins import UserPassesTestMixin
from django.views.generic import ListView, DetailView, UpdateView
from django_tables2 import RequestConfig


class BaseUserPassesTestMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff

    def handle_no_permission(self):
        return render(self.request, '403.html')


class BaseListView(ListView):

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
        RequestConfig(self.request, paginate={"per_page": self.paginate_by}).configure(table)
        context[self.context_filter_name]=filter
        context[self.context_table_name]=table

        return context


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