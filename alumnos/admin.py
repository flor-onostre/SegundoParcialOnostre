from django.contrib import admin
from .models import Alumno


@admin.register(Alumno)
class AlumnoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "apellido", "carrera", "email_contacto", "user", "creado_en")
    search_fields = ("nombre", "apellido", "carrera", "email_contacto")
    list_filter = ("carrera",)
