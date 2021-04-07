from django.contrib import admin
# Register your models here.
from django.apps import apps

models = apps.get_models()

app = apps.get_app_config('administration')
for model_name, model in app.models.items():
    admin.site.register(model)
