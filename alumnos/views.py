from io import BytesIO

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from SegundoParcialOnostre.email_utils import send_brevo_email
from .forms import AlumnoForm
from .models import Alumno


@login_required
def dashboard(request):
    alumnos = Alumno.objects.filter(user=request.user)
    if request.method == "POST":
        form = AlumnoForm(request.POST)
        if form.is_valid():
            alumno = form.save(commit=False)
            alumno.user = request.user
            alumno.save()
            messages.success(request, "Alumno creado.")
            return redirect("dashboard")
    else:
        form = AlumnoForm()
    return render(request, "alumnos/dashboard.html", {"alumnos": alumnos, "form": form})


@login_required
def eliminar_alumno(request, pk):
    alumno = get_object_or_404(Alumno, pk=pk, user=request.user)
    if request.method == "POST":
        alumno.delete()
        messages.success(request, "Alumno eliminado.")
    return redirect("dashboard")


@login_required
def enviar_pdf(request, pk):
    alumno = get_object_or_404(Alumno, pk=pk, user=request.user)
    if request.method != "POST":
        return HttpResponseForbidden()

    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    pdf.setTitle("Ficha de alumno")
    pdf.drawString(72, 750, "Ficha de Alumno")
    pdf.drawString(72, 720, f"Nombre: {alumno.nombre} {alumno.apellido}")
    pdf.drawString(72, 700, f"Carrera: {alumno.carrera}")
    pdf.drawString(72, 680, f"Email de contacto: {alumno.email_contacto}")
    pdf.drawString(72, 660, f"Fecha: {timezone.now().date()}")
    pdf.showPage()
    pdf.save()
    data = buffer.getvalue()

    email_to = request.user.email or alumno.email_contacto
    ok = send_brevo_email(
        [email_to],
        "PDF de alumno",
        "Adjuntamos el PDF con los datos del alumno.",
        attachments=[
            {"name": f"alumno_{alumno.pk}.pdf", "content": data, "type": "application/pdf"}
        ],
    )
    if ok:
        messages.success(request, "PDF enviado por correo.")
    else:
        messages.error(request, "No se pudo enviar el correo (revisa API key).")
    return redirect("dashboard")
