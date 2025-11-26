from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
import requests
from bs4 import BeautifulSoup

from SegundoParcialOnostre.email_utils import send_brevo_email
from .forms import ScraperForm


HEADERS = {"User-Agent": "Mozilla/5.0 (Scraper/1.0 Codex Demo)"}


def _buscar_wikipedia(keyword: str, lang: str):
    """
    Usa la API de Wikipedia para obtener resultados de búsqueda con extracto corto.
    """
    url = f"https://{lang}.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "list": "search",
        "srsearch": keyword,
        "format": "json",
        "srlimit": 5,
    }
    try:
        resp = requests.get(url, params=params, timeout=10, headers=HEADERS)
        resp.raise_for_status()
        data = resp.json()
        results = []
        for item in data.get("query", {}).get("search", []):
            snippet_html = item.get("snippet", "")
            snippet = BeautifulSoup(snippet_html, "html.parser").get_text()
            results.append(
                {
                    "texto": item.get("title", ""),
                    "autor": snippet,
                    "idioma": lang.upper(),
                }
            )
        return results
    except Exception:
        return []


def _buscar_quotes(keyword: str):
    """
    Busca resultados en Wikipedia ES con extractos.
    """
    resultados = []
    resultados.extend(_buscar_wikipedia(keyword, "es"))
    return resultados


@login_required
def scraper_view(request):
    results = []
    form = ScraperForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        keyword = form.cleaned_data["keyword"]
        action = request.POST.get("action", "search")
        results = _buscar_quotes(keyword)
        if not results:
            messages.warning(request, "No se encontraron resultados o hubo un error.")
        else:
            messages.success(request, f"Se encontraron {len(results)} resultados.")
            if action == "send" and request.user.email:
                cuerpo = "\n".join([f"- {r['texto']} ({r['autor']})" for r in results[:10]])
                filas_html = "".join(
                    f"<tr><td>{r['texto']}</td><td>{r['autor']}</td></tr>"
                    for r in results[:20]
                )
                html = (
                    "<h3>Resultados de scraping</h3>"
                    "<table border='1' cellpadding='6' cellspacing='0'>"
                    "<thead><tr><th>Título</th><th>Extracto</th></tr></thead>"
                    f"<tbody>{filas_html}</tbody></table>"
                )
                ok = send_brevo_email(
                    [request.user.email],
                    f"Resultados de scraping para '{keyword}'",
                    cuerpo,
                    html=html,
                )
                if ok:
                    messages.info(request, "Resultados enviados a tu correo.")
                else:
                    messages.warning(request, "No se pudo enviar correo (revisa API key).")

    return render(
        request,
        "scraper/form.html",
        {"form": form, "results": results},
    )
