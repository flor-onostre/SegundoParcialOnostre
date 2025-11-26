from django.urls import path
from .views import dashboard, enviar_pdf, eliminar_alumno

urlpatterns = [
    path("", dashboard, name="dashboard"),
    path("alumnos/<int:pk>/enviar_pdf/", enviar_pdf, name="enviar_pdf"),
    path("alumnos/<int:pk>/eliminar/", eliminar_alumno, name="eliminar_alumno"),
]
