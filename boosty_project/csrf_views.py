from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def csrf_failure(request, reason=""):
    """Custom CSRF failure view that allows all requests"""
    return HttpResponse("CSRF check bypassed", status=200)
