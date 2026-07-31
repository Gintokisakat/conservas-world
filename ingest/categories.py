CATEGORIES = [
    {
        "code": "fermento_lactico",
        "name": "Fermento láctico",
        "description": "Fermentación por bacterias ácido-lácticas (LAB).",
    },
    {
        "code": "fermento_alcoholico",
        "name": "Fermento alcohólico",
        "description": "Fermentación por levaduras que produce alcohol.",
    },
    {
        "code": "fermento_acetico",
        "name": "Fermento acético",
        "description": "Fermentación acética; producción de vinagre.",
    },
    {
        "code": "fermento_alcalino",
        "name": "Fermento alcalino",
        "description": "Fermentación alcalina por Bacillus, típica de África y Asia.",
    },
    {
        "code": "fermento_koji",
        "name": "Fermento con hongos (koji/moho)",
        "description": "Fermentación con hongos filamentosos como Aspergillus.",
    },
    {
        "code": "encurtido_fermentado",
        "name": "Encurtido fermentado",
        "description": "Verduras/frutas conservadas por fermentación láctica en salmuera.",
    },
    {
        "code": "encurtido_vinagre",
        "name": "Encurtido en vinagre",
        "description": "Conservado en vinagre (encurtido rápido, sin fermentación).",
    },
    {
        "code": "encurtido_salmuera",
        "name": "Encurtido en salmuera",
        "description": "Conservado en salmuera, con o sin fermentación.",
    },
    {
        "code": "conserva_esterilizada",
        "name": "Conserva esterilizada",
        "description": "Enlatado/embotellado esterilizado en autoclave o baño maría.",
    },
    {
        "code": "conserva_azucar",
        "name": "Conserva en azúcar",
        "description": "Mermeladas, jaleas, almíbares y dulces conservados en azúcar.",
    },
    {
        "code": "conserva_aceite",
        "name": "Conserva en aceite / confitado",
        "description": "Alimentos conservados sumergidos en aceite.",
    },
    {
        "code": "curado_sal",
        "name": "Curado en sal",
        "description": "Carnes, pescados o vegetales curados con sal.",
    },
    {
        "code": "ahumado",
        "name": "Ahumado",
        "description": "Conservación mediante humo.",
    },
    {
        "code": "secado",
        "name": "Secado",
        "description": "Conservación por deshidratación.",
    },
    {
        "code": "fermento_mixto",
        "name": "Fermento mixto",
        "description": "Combinación de varios tipos de fermentación.",
    },
    {
        "code": "otro",
        "name": "Otro",
        "description": "Método de conservación no cubierto por otras categorías.",
    },
]

CATEGORY_BY_CODE = {c["code"]: c for c in CATEGORIES}


def category_codes():
    return [c["code"] for c in CATEGORIES]
