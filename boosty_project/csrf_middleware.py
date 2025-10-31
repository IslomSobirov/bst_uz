from django.utils.deprecation import MiddlewareMixin


class DisableCSRFMiddleware(MiddlewareMixin):
    def process_request(self, request):
        setattr(request, '_dont_enforce_csrf_checks', True)
        return None

    def process_view(self, request, view_func, view_args, view_kwargs):
        setattr(request, '_dont_enforce_csrf_checks', True)
        return None
