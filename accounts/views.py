from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LoginView, LogoutView, PasswordResetView
from django.shortcuts import redirect, render
from django.urls import reverse_lazy

from SegundoParcialOnostre.email_utils import send_brevo_email
from .forms import RegistrationForm, BrevoPasswordResetForm


class CustomLoginView(LoginView):
    template_name = "registration/login.html"
    authentication_form = AuthenticationForm

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        for field in form.fields.values():
            field.widget.attrs["class"] = "form-control"
        return form


class CustomLogoutView(LogoutView):
    next_page = reverse_lazy("login")


def logout_view(request):
    from django.contrib.auth import logout

    logout(request)
    messages.info(request, "Sesión cerrada.")
    return redirect("login")


class BrevoPasswordResetView(PasswordResetView):
    form_class = BrevoPasswordResetForm
    template_name = "registration/password_reset_form.html"
    email_template_name = "registration/password_reset_email.txt"
    subject_template_name = "registration/password_reset_subject.txt"
    success_url = reverse_lazy("password_reset_done")


def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            sent = send_brevo_email(
                [user.email],
                "Bienvenido al dashboard",
                "Gracias por registrarte. Ya puedes empezar a cargar alumnos.",
            )
            messages.success(request, "Registro exitoso. Te damos la bienvenida.")
            if not sent:
                messages.warning(
                    request,
                    "No se pudo enviar el correo de bienvenida. "
                    "Verifica BREVO_API_KEY, BREVO_SENDER_EMAIL y BREVO_SENDER_NAME.",
                )
            return redirect("dashboard")
    else:
        form = RegistrationForm()
    return render(request, "accounts/register.html", {"form": form})
