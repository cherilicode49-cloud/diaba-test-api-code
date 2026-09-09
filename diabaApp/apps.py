from django.apps import AppConfig


class DiabaappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'diabaApp'

    def ready(self):
        import diabaApp.signals
