# ingredients/apps.py
from django.apps import AppConfig

class IngredientsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ingredients'

    def ready(self):
        from .utils import cache_drugs_on_startup
        cache_drugs_on_startup()
