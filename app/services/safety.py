"""Evaluación predictiva de pH/seguridad (2.3).

Perfiles curados por tipo de fermento (basados en guías BCCDC, pH pickling
calculators y literatura de fermentación) que se aplican heurísticamente
según el método y el nombre del producto. Sin escrituras a BD.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class SafetyProfile:
    key: str
    label_es: str
    label_en: str
    ph_min: float
    ph_max: float
    aw_min: float
    aw_max: float
    salt_min: float
    salt_max: float
    storage_temp_c: str
    shelf_life_days: int
    risk: str
    alerts_es: list[str]
    alerts_en: list[str]


PROFILES: list[SafetyProfile] = [
    SafetyProfile(
        key="lacto_vegetables",
        label_es="Vegetales lactofermentados",
        label_en="Lacto-fermented vegetables",
        ph_min=3.4, ph_max=4.6, aw_min=0.95, aw_max=1.0,
        salt_min=2.0, salt_max=5.0, storage_temp_c="4–10",
        shelf_life_days=180, risk="bajo",
        alerts_es=["Mantener pH < 4.6 para inocuidad.", "Sal > 2% previene patógenos como Clostridium."],
        alerts_en=["Keep pH below 4.6 for safety.", "Salt above 2% prevents pathogens like Clostridium."],
    ),
    SafetyProfile(
        key="acetic",
        label_es="Encurtidos y vinagres",
        label_en="Pickles and vinegars",
        ph_min=2.4, ph_max=3.8, aw_min=0.9, aw_max=1.0,
        salt_min=2.0, salt_max=6.0, storage_temp_c="4–20",
        shelf_life_days=365, risk="bajo",
        alerts_es=["La acidez acética (pH < 4.6) garantiza conservación segura.", "Verificar acidez ≥ 4.5% en encurtidos de larga duración."],
        alerts_en=["Acetic acidity (pH < 4.6) ensures safe preservation.", "Check acidity ≥ 4.5% for long-term pickles."],
    ),
    SafetyProfile(
        key="alcohol",
        label_es="Bebidas fermentadas",
        label_en="Fermented beverages",
        ph_min=3.0, ph_max=4.5, aw_min=0.98, aw_max=1.0,
        salt_min=0.0, salt_max=0.0, storage_temp_c="4–12",
        shelf_life_days=120, risk="bajo",
        alerts_es=["El alcohol y el pH ácido protegen frente a patógenos.", "Evitar contaminación por moho en superficie."],
        alerts_en=["Alcohol and acidic pH protect against pathogens.", "Avoid surface mold contamination."],
    ),
    SafetyProfile(
        key="koji",
        label_es="Fermentos de soja/koji",
        label_en="Soy/koji ferments",
        ph_min=4.8, ph_max=5.2, aw_min=0.85, aw_max=0.95,
        salt_min=8.0, salt_max=12.0, storage_temp_c="4–10",
        shelf_life_days=365, risk="medio",
        alerts_es=["La alta salinidad (8–12%) evita el botulismo; vigilar moho en superficie.", "No es ácido: la sal es el factor de seguridad."],
        alerts_en=["High salt (8–12%) prevents botulism; watch for surface mold.", "Not acidic: salt is the safety factor."],
    ),
    SafetyProfile(
        key="dairy",
        label_es="Lácteos fermentados",
        label_en="Fermented dairy",
        ph_min=4.3, ph_max=4.8, aw_min=0.96, aw_max=1.0,
        salt_min=1.0, salt_max=3.0, storage_temp_c="2–6",
        shelf_life_days=21, risk="bajo",
        alerts_es=["Conservar refrigerado.", "pH < 4.8 y cadena de frío son críticos."],
        alerts_en=["Keep refrigerated.", "pH below 4.8 and cold chain are critical."],
    ),
    SafetyProfile(
        key="cured",
        label_es="Curados y salazones",
        label_en="Cured and salted",
        ph_min=5.0, ph_max=6.5, aw_min=0.82, aw_max=0.92,
        salt_min=6.0, salt_max=15.0, storage_temp_c="4–12",
        shelf_life_days=180, risk="medio",
        alerts_es=["La baja actividad de agua (aw < 0.92) controla patógenos.", "Salazón ≥ 6% y temperatura fría recomendadas."],
        alerts_en=["Low water activity (aw < 0.92) controls pathogens.", "Salting ≥ 6% and cold temperature recommended."],
    ),
]

DEFAULT_PROFILE = SafetyProfile(
    key="generic",
    label_es="Fermento genérico",
    label_en="Generic ferment",
    ph_min=3.5, ph_max=5.5, aw_min=0.85, aw_max=1.0,
    salt_min=0.0, salt_max=15.0, storage_temp_c="4–20",
    shelf_life_days=90, risk="bajo",
    alerts_es=["Verificar ausencia de moho negro y olor pútrido antes de consumir.", "Si dudas, desecha."],
    alerts_en=["Check for black mold and putrid smell before eating.", "When in doubt, throw it out."],
)

CATEGORY_RULES: list[tuple[tuple[str, ...], str]] = [
    (("vinagre", "vinegar", "acetic", "encurtid", "pickle", "vinaigrette"), "acetic"),
    (("koji", "miso", "soja", "soy", "shoyu", "tamari"), "koji"),
    (("cerveza", "beer", "vino", "wine", "kombucha", "kefir de agua", "hidromiel", "mead", "sidra", "cider", "sake", "tepache"), "alcohol"),
    (("queso", "cheese", "yogur", "yogurt", "leche", "milk", "kéfir", "kefir", "buttermilk",
      "burrata", "mozzarella", "fromage", "quark", "ricotta", "paneer", "feta", "chèvre",
      "cheddar", "gouda", "manchego", "brie", "camembert", "parmesan", "parmesano", "pecorino"), "dairy"),
    (("curado", "cured", "salazón", "jamón", "ham", "salami", "anchoa", "anchovy", "bacalao", "cod"), "cured"),
    (("lacto", "sauerkraut", "chucrut", "kimchi", "pepinillo", "gherkin"), "lacto_vegetables"),
]


def classify(product) -> SafetyProfile:
    if getattr(product, "dairy", None) is not None or getattr(product, "metagenome", None) is not None:
        return next(p for p in PROFILES if p.key == "dairy")
    name = (product.name or "").lower()
    method = (product.method or "").lower()
    text = f"{name} {method}"
    for keywords, key in CATEGORY_RULES:
        if any(kw in text for kw in keywords):
            for profile in PROFILES:
                if profile.key == key:
                    return profile
    return DEFAULT_PROFILE


def safety_assessment(product, lang: str = "es") -> dict:
    profile = classify(product)
    is_en = lang == "en"
    alerts = profile.alerts_en if is_en else profile.alerts_es
    return {
        "product_id": product.id,
        "name": product.name,
        "category": profile.label_en if is_en else profile.label_es,
        "risk": profile.risk,
        "ph_min": profile.ph_min,
        "ph_max": profile.ph_max,
        "ph_requirement": "pH < 4.6" if profile.ph_max < 4.8 else "alta sal / aw baja",
        "aw_min": profile.aw_min,
        "aw_max": profile.aw_max,
        "salt_pct_min": profile.salt_min,
        "salt_pct_max": profile.salt_max,
        "storage_temp_c": profile.storage_temp_c,
        "shelf_life_days": profile.shelf_life_days,
        "alerts": alerts,
    }