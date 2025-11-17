from django.apps import AppConfig

class TiendaConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tienda'

    def ready(self):
        # Importamos signals aquí, cuando los modelos ya están cargados
        import tienda.signals
