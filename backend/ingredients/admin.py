# admin.py
from django.contrib import admin
from .models import Symptom, Drug

admin.site.register(Symptom)
admin.site.register(Drug)
