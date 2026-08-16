"""Curaduría del gap regional África subsahariana / Oriente Medio (roadmap 2.14).

Registros verificados contra fuentes bibliográficas; no se inventan datos.
"""

from ingest.normalize import resolve_country


def _country(name: str) -> dict:
    info = resolve_country(name)
    if info is None:
        raise ValueError(f"País no resuelto: {name}")
    info["role"] = "origin"
    return info


def load_source() -> list[dict]:
    return [
        {
            "name": "Mbuja",
            "aliases": [],
            "description": (
                "Condimento tradicional camerunés elaborado a partir de semillas de "
                "roselle (Hibiscus sabdariffa) fermentadas por bacterias del género "
                "Bacillus. Las semillas se fermentan unos 7 días, se muelen y se "
                "someten a una segunda fermentación de unos 3 días más. El proceso "
                "alcalino produce un condimento rico en proteína y umami, usado para "
                "dar sabor a sopas y guisos."
            ),
            "method": None,
            "fermentation_time": "7-10 días",
            "countries": [_country("Cameroon")],
            "ingredients": [{"name": "roselle", "category": "fruta"}],
            "categories": ["fermento_alcalino"],
            "microbes": ["Bacillus"],
            "references": [
                {
                    "title": (
                        "Genotypic and phenotypic diversity among Bacillus species "
                        "isolated from Mbuja, a Cameroonian traditional fermented condiment"
                    ),
                    "ref_type": "literature",
                    "url": None,
                    "doi": "10.4314/ajb.v12i12",
                }
            ],
            "source_tag": "regional",
        },
        {
            "name": "Torshi",
            "aliases": [{"name": "turshi", "language": "en"}],
            "description": (
                "Encurtido de hortalizas típico de Irán y Oriente Medio. Verduras "
                "variadas (col, zanahoria, pepino, ajo, berenjena) se fermentan en "
                "salmuera con vinagre y especias, y se sirven como acompañamiento "
                "ácido y crujiente de las comidas."
            ),
            "method": None,
            "fermentation_time": None,
            "countries": [_country("Iran")],
            "ingredients": [{"name": "vegetables", "category": "vegetal"}],
            "categories": ["encurtido_fermentado"],
            "microbes": ["Lactobacillus"],
            "references": [],
            "source_tag": "regional",
        },
        {
            "name": "Dibis",
            "aliases": [
                {"name": "dibs", "language": "ar"},
                {"name": "rub", "language": "ar"},
                {"name": "silan", "language": "he"},
                {"name": "date molasses", "language": "en"},
                {"name": "date honey", "language": "en"},
            ],
            "description": (
                "Jarabe o melaza de dátil (Phoenix dactylifera) propio de Irak y "
                "Oriente Medio. Los dátiles se cuecen, se trituran y el jugo se reduce "
                "hasta obtener un sirope muy dulce que se conserva por su alta "
                "concentración de azúcar; su elaboración no implica fermentación. "
                "También se conoce como dibs, rub, silan, date honey o date molasses."
            ),
            "method": None,
            "fermentation_time": None,
            "countries": [_country("Iraq")],
            "ingredients": [{"name": "date", "category": "fruta"}],
            "categories": ["conserva_azucar"],
            "microbes": [],
            "references": [
                {
                    "title": "Wikipedia: Date honey",
                    "ref_type": "web",
                    "url": "https://en.wikipedia.org/wiki/Date_honey",
                    "doi": None,
                }
            ],
            "source_tag": "regional",
        },
    ]
