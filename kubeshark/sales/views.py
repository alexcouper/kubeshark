from django.shortcuts import render
from django.views.generic import View

from .models import KnownKubeShark


class SharkView(View):
    template_name = 'signup.html'

    def get(self, request):
        return render(request, self.template_name)
