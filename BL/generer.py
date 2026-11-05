import base64
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from playwright.sync_api import sync_playwright
from datetime import datetime

from config import COMPANY_INFO
from models.CommandeBL import CommandeBL


def creer_BL_data(commande: CommandeBL, ref_BL):
    return {
        "company": COMPANY_INFO,
        "client": {
            "name": commande.client,
            "address": "",
            "email": ""
        },
        "invoice": {
            "reference": ref_BL or f"BL-{datetime.now().strftime('%Y%m%d')}-01",
            "date": datetime.now().strftime("%d/%m/%Y"),
            "status": "en_attente",
            "status_label": "EN ATTENTE"
        },
        "currency": commande.devise.value,
        "items": [
            {
                "name": article.nom_produit,
                "description": "",
                "qty": article.quantite,
                "unit_price": article.prix_unitaire if article.prix_unitaire else 0
            }
            for article in commande.articles
        ],
        "discount": 0
    }


BASE_DIR = Path(__file__).parent
TEMPLATES_DIR = BASE_DIR / "templates"
OUTPUT_DIR = BASE_DIR / "output"
LOGO_PATH = BASE_DIR / "static" / "logo.png"


def image_to_base64(path: Path) -> str:
    if not path.exists():
        return ""
    data = base64.b64encode(path.read_bytes()).decode("utf-8")
    return f"data:image/png;base64,{data}"


def render_html(context: dict) -> str:
    env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))
    template = env.get_template("template.html")
    css_content = (TEMPLATES_DIR / "style.css").read_text(encoding="utf-8")
    context["inline_css"] = css_content
    return template.render(**context)


def html_to_pdf(html_content: str, output_path: Path):
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.set_content(
            html_content,
            wait_until="networkidle"
        )
        page.pdf(
            path=str(output_path),
            format="A4",
            print_background=True,
            margin={
                "top": "0mm",
                "bottom": "0mm",
                "left": "0mm",
                "right": "0mm"
            },
        )
        browser.close()


def generate_bl(valeur, ref_BL):
    data = creer_BL_data(valeur, ref_BL)
    OUTPUT_DIR.mkdir(exist_ok=True)
    data["logo_path"] = image_to_base64(LOGO_PATH)

    subtotal = sum(
        item["qty"] * item["unit_price"]
        for item in data["items"]
    )

    vat_rate = 19
    vat_amount = subtotal * vat_rate / 100
    discount = 0
    total = subtotal + vat_amount - discount

    data.update({
        "subtotal": round(subtotal, 2),
        "vat_rate": vat_rate,
        "vat_amount": round(vat_amount, 2),
        "discount": discount,
        "total": round(total, 2),
    })

    reference = data["invoice"]["reference"]
    filename = f"{reference}.pdf"
    output_path = OUTPUT_DIR / filename

    html_content = render_html(data)
    html_to_pdf(html_content, output_path)
    print(f"BL générée : {output_path}")
