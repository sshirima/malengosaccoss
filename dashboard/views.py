from django.shortcuts import render
from django.views.generic import View

# Create your views here.


class DashboardView(View):
    template_name = 'dashboard/index.html'

    def get(self, request):
        return render(request, self.template_name)