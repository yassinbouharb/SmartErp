import base64
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from playwright.sync_api import sync_playwright
from datetime import datetime

from config import COMPANY_INFO
from models.CommandeFacture import CommandeFacture


# =========================================================
# PRÉPARATION DES DONNÉES DE FACTURE
# =========================================================

def creer_facture_data(
    commande: CommandeFacture,
    ref_facture,
    client_data: dict
):
    """
    Prépare les données nécessaires à la génération de la facture.

    Les prix présents dans commande.articles sont considérés
    comme des prix TTC.

    Ils seront convertis en HT avec une TVA de 19 %.
    """

    vat_rate = 19

    items = []

    for article in commande.articles:

        # Prix reçu = TTC
        prix_ttc = float(article.prix_unitaire)

        # Conversion TTC -> HT
        prix_ht = prix_ttc / (
            1 + vat_rate / 100
        )

        items.append({

            "name": article.nom_produit,
            "description": "",
            "qty": article.quantite,

            # Prix affiché sur la facture
            "unit_price": prix_ht,

            # Prix original TTC conservé
            "unit_price_ttc": prix_ttc
        })

    return {

        # =====================================================
        # ENTREPRISE
        # =====================================================

        "company": COMPANY_INFO,

        # =====================================================
        # CLIENT
        # =====================================================

        "client": {
            "name": client_data.get(
                "nom",
                ""
            ),

            "code": client_data.get(
                "code",
                ""
            ),

            "contact": client_data.get(
                "contact",
                ""
            ),

            "telephone": client_data.get(
                "telephone",
                ""
            ),

            "ville": client_data.get(
                "ville",
                ""
            ),

            "matricule_fiscal": client_data.get(
                "matricule_fiscale",
                ""
            ),

            "email": client_data.get(
                "email",
                ""
            )
        },

        # =====================================================
        # FACTURE
        # =====================================================

        "invoice": {

            "reference": (
                ref_facture
                or f"FAC-{datetime.now().strftime('%Y%m%d')}-01"
            ),

            "date": datetime.now().strftime(
                "%d/%m/%Y"
            ),

            "status": "due",

            "status_label": "EN ATTENTE DE PAIEMENT"
        },

        # =====================================================
        # DEVISE
        # =====================================================

        "currency": commande.devise.value,

        # =====================================================
        # TVA
        # =====================================================

        "vat_rate": vat_rate,

        # =====================================================
        # ARTICLES
        # =====================================================

        "items": items,

        # =====================================================
        # REMISE
        # =====================================================

        "discount": 0
    }


# =========================================================
# CHEMINS
# =========================================================

BASE_DIR = Path(__file__).parent

TEMPLATES_DIR = BASE_DIR / "templates"

OUTPUT_DIR = BASE_DIR / "output"

LOGO_PATH = BASE_DIR / "static" / "logo.png"


# =========================================================
# IMAGE -> BASE64
# =========================================================

def image_to_base64(path: Path) -> str:
    """
    Intègre le logo directement dans le HTML.
    """

    if not path.exists():
        return ""

    data = base64.b64encode(
        path.read_bytes()
    ).decode("utf-8")

    return f"data:image/png;base64,{data}"


# =========================================================
# HTML
# =========================================================

def render_html(context: dict) -> str:

    env = Environment(
        loader=FileSystemLoader(
            TEMPLATES_DIR
        )
    )

    template = env.get_template(
        "template.html"
    )

    css_content = (
        TEMPLATES_DIR / "style.css"
    ).read_text(
        encoding="utf-8"
    )

    context["inline_css"] = css_content

    return template.render(
        **context
    )


# =========================================================
# HTML -> PDF
# =========================================================

def html_to_pdf(
    html_content: str,
    output_path: Path
):

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


# =========================================================
# GÉNÉRATION FACTURE
# =========================================================

def generate_invoice(
    commande: CommandeFacture,
    ref_facture,
    client_data: dict
):
    """
    Génère le PDF de la facture.

    Les prix reçus dans commande.articles sont TTC.

    Exemple client_data :

    {
        "code": "CL001",
        "nom": "ABC SARL",
        "contact": "",
        "telephone": "22123456",
        "ville": "Tunis",
        "solde": 0.0,
        "matricule_fiscale": "1234567A"
    }
    """

    # =====================================================
    # Préparation des données
    # =====================================================

    data = creer_facture_data(
        commande,
        ref_facture,
        client_data
    )

    OUTPUT_DIR.mkdir(
        exist_ok=True
    )

    # =====================================================
    # LOGO
    # =====================================================

    data["logo_path"] = image_to_base64(
        LOGO_PATH
    )

    # =====================================================
    # SOUS-TOTAL HT
    # =====================================================

    subtotal = sum(
        item["qty"] * item["unit_price"]
        for item in data["items"]
    )

    # =====================================================
    # TVA
    # =====================================================

    vat_rate = data.get(
        "vat_rate",
        19
    )

    vat_amount = (
        subtotal * vat_rate / 100
    )

    # =====================================================
    # REMISE
    # =====================================================

    discount = data.get(
        "discount",
        0
    )

    # =====================================================
    # TOTAL TTC
    # =====================================================

    total = (
        subtotal
        + vat_amount
        - discount
    )

    # =====================================================
    # ARRONDI MONÉTAIRE
    # =====================================================

    subtotal = round(
        subtotal,
        2
    )

    vat_amount = round(
        vat_amount,
        2
    )

    total = round(
        total,
        2
    )

    discount = round(
        discount,
        2
    )

    # =====================================================
    # DONNÉES FINALES
    # =====================================================

    data.update({

        # Sous-total HT
        "subtotal": subtotal,

        # TVA
        "vat_rate": vat_rate,
        "vat_amount": vat_amount,

        # Remise
        "discount": discount,

        # Total TTC
        "total": total
    })

    # =====================================================
    # NOM DU PDF
    # =====================================================

    reference = data[
        "invoice"
    ][
        "reference"
    ]

    filename = f"{reference}.pdf"

    output_path = (
        OUTPUT_DIR / filename
    )

    # =====================================================
    # GÉNÉRATION HTML
    # =====================================================

    html_content = render_html(
        data
    )

    # =====================================================
    # GÉNÉRATION PDF
    # =====================================================

    html_to_pdf(
        html_content,
        output_path
    )

    print(
        f"Facture générée : {output_path}"
    )

    return output_path