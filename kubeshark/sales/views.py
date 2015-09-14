from django.shortcuts import render
from django.views.generic import View
from django.http import HttpResponseRedirect

from .models import KnownKubeShark


class SharkView(View):
    template_name = 'signup.html'

    def get(self, request):
        sharks = KnownKubeShark.objects.filter().order_by('-created')[:5]
        names = [s.name for s in sharks]
        print([s.created for s in sharks])
        return render(request, self.template_name, context={'sharks':names})

    def post(self, request):
        name = request.POST['name']
        KnownKubeShark.objects.create(name=name)
        return HttpResponseRedirect('/')
