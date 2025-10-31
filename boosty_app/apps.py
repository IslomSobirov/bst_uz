from django.apps import AppConfig


class BoostyAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'boosty_app'

    def ready(self):
        import boosty_app.signals
