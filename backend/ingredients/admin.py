from django.contrib import admin
from .models import Drug, DrugComment, DrugReaction, DrugAiSummary

admin.site.register(Drug)
admin.site.register(DrugComment)
admin.site.register(DrugReaction)
admin.site.register(DrugAiSummary)
