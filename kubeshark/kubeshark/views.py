from django.http import HttpResponse

def shark(request):
    return HttpResponse(
        "<h2>Shark Attack!</h2><img src='http://www.esheled.com/wp-content/uploads/2015/01/KubernetesLogo.png'/>"
    )
