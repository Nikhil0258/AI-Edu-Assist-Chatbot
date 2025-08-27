from django.contrib import admin
from .models import Quiz  # Import the Quiz model

# Register your models here.
# Register the Quiz model so it appears in the Django admin panel
admin.site.register(Quiz)