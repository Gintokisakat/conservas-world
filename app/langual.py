"""Vocabulario controlado LanguaL (2.16): facetas H/J/A de fermentación y conservación.

Códigos extraídos del thesaurus LanguaL 2017 (langual.org / Danish Food Informatics).
Solo se incluyen los descriptores relevantes para fermentos y conservas del mundo.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class LanguaLTerm:
    facet: str
    label_en: str
    label_es: str
    scope_es: str | None = None
    scope_en: str | None = None

    def label(self, lang: str) -> str:
        return self.label_es if lang == "es" else self.label_en


_LANGUAL_TERMS: dict[str, LanguaLTerm] = {
    # Faceta A — Tipo de producto
    "A0783": LanguaLTerm(
        facet="A",
        label_en="Fermented milk product (EuroFIR)",
        label_es="Producto lácteo fermentado (EuroFIR)",
    ),
    # Faceta H — Tratamiento aplicado (fermentación)
    "H0101": LanguaLTerm(facet="H", label_en="Lactic acid fermented", label_es="Fermentado con ácido láctico"),
    "H0102": LanguaLTerm(facet="H", label_en="Proteolytic fermented", label_es="Fermentado proteolítico"),
    "H0107": LanguaLTerm(facet="H", label_en="Lactic acid-other agent fermented", label_es="Fermentado láctico-otro agente"),
    "H0123": LanguaLTerm(facet="H", label_en="Alcohol-acetic acid fermented", label_es="Fermentado alcohólico-acético"),
    "H0127": LanguaLTerm(facet="H", label_en="Lipolytic fermented", label_es="Fermentado lipolítico"),
    "H0128": LanguaLTerm(facet="H", label_en="Fermented/modified, multiple component", label_es="Fermentado/modificado multicomponente"),
    "H0190": LanguaLTerm(facet="H", label_en="Pickled", label_es="Encurtido"),
    "H0200": LanguaLTerm(facet="H", label_en="Acidified", label_es="Acidificado"),
    "H0230": LanguaLTerm(facet="H", label_en="Fermented/modified, single component", label_es="Fermentado/modificado de componente único"),
    "H0232": LanguaLTerm(facet="H", label_en="Alcohol fermented", label_es="Fermentado alcohólico"),
    "H0256": LanguaLTerm(facet="H", label_en="Carbohydrate fermented", label_es="Fermentado de carbohidratos"),
    "H0300": LanguaLTerm(facet="H", label_en="Acetic acid fermented", label_es="Fermentado acético"),
    # Faceta J — Método de conservación
    "J0100": LanguaLTerm(facet="J", label_en="Preserved by adding chemicals", label_es="Conservado añadiendo productos químicos"),
    "J0103": LanguaLTerm(facet="J", label_en="Preserved by salting", label_es="Conservado por salado"),
    "J0104": LanguaLTerm(facet="J", label_en="Preserved by fermentation", label_es="Conservado por fermentación"),
    "J0106": LanguaLTerm(facet="J", label_en="Preserved by smoking", label_es="Conservado por ahumado"),
    "J0120": LanguaLTerm(facet="J", label_en="Preserved by heat treatment", label_es="Conservado por tratamiento térmico"),
    "J0135": LanguaLTerm(facet="J", label_en="Pasteurized by heat", label_es="Pasteurizado por calor"),
    "J0139": LanguaLTerm(facet="J", label_en="Preserved by dry salting", label_es="Conservado por sal seca"),
    "J0145": LanguaLTerm(facet="J", label_en="Preserved by reducing water activity", label_es="Conservado reduciendo la actividad de agua"),
}

# Mapeo categoría interna -> códigos LanguaL
# Las categorías de fermentación van con su descriptor de faceta H + J0104
# (conservado por fermentación); las conservas no fermentadas solo con faceta J.
CATEGORY_LANGUAL: dict[str, list[str]] = {
    "fermento_lactico": ["H0101", "J0104"],
    "fermento_acetico": ["H0300", "J0104"],
    "fermento_alcoholico": ["H0232", "J0104"],
    "fermento_koji": ["H0256", "J0104"],
    "fermento_cereal": ["H0256", "J0104"],
    "fermento_alcalino": ["H0102", "J0104"],
    "fermento_mixto": ["H0128", "J0104"],
    "encurtido_fermentado": ["H0101", "J0104"],
    "encurtido_salmuera": ["H0190", "J0103"],
    "encurtido_vinagre": ["H0200", "J0100"],
    "curado_sal": ["J0139"],
    "ahumado": ["J0106"],
    "secado": ["J0145"],
    "conserva_aceite": [],
    "conserva_azucar": [],
    "conserva_esterilizada": ["J0120", "J0135"],
    "otro": [],
}

# Nombre legible por categoría (para vitrinas multilingües del Codex)
CATEGORY_LABEL: dict[str, dict[str, str]] = {
    "fermento_lactico": {"es": "Fermento láctico", "en": "Lactic ferment"},
    "fermento_acetico": {"es": "Fermento acético", "en": "Acetic ferment"},
    "fermento_alcoholico": {"es": "Fermento alcohólico", "en": "Alcoholic ferment"},
    "fermento_koji": {"es": "Fermento con hongos", "en": "Mold (koji) ferment"},
    "fermento_cereal": {"es": "Fermento de cereal y tubérculo", "en": "Grain & tuber ferment"},
    "fermento_alcalino": {"es": "Fermento alcalino", "en": "Alkaline ferment"},
    "fermento_mixto": {"es": "Fermento mixto", "en": "Mixed ferment"},
    "encurtido_fermentado": {"es": "Encurtido fermentado", "en": "Fermented pickle"},
    "encurtido_salmuera": {"es": "Encurtido en salmuera", "en": "Brine pickle"},
    "encurtido_vinagre": {"es": "Encurtido en vinagre", "en": "Vinegar pickle"},
    "curado_sal": {"es": "Curado en sal", "en": "Salt-cured"},
    "ahumado": {"es": "Ahumado", "en": "Smoked"},
    "secado": {"es": "Secado", "en": "Dried"},
    "conserva_aceite": {"es": "Conserva en aceite", "en": "Oil preserve"},
    "conserva_azucar": {"es": "Conserva en azúcar", "en": "Sugar preserve"},
    "conserva_esterilizada": {"es": "Conserva esterilizada", "en": "Sterilized preserve"},
    "otro": {"es": "Otro", "en": "Other"},
}