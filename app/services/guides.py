"""Guías paso a paso interactivas (3.4).

Contenido curado en código (sin dependencia de BD) para no interferir con el
pipeline de ingesta: cada guía tiene pasos con duración/temperatura y un aviso
de inocuidad opcional. El frontend las muestra como un stepper y puede iniciar
un temporizador por paso.
"""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class GuideStep:
    number: int
    title_es: str
    title_en: str
    body_es: str
    body_en: str
    duration_min: int | None = None
    temp_c: int | None = None
    safety: bool = False


@dataclass(frozen=True)
class Guide:
    slug: str
    category_es: str
    category_en: str
    title_es: str
    title_en: str
    intro_es: str
    intro_en: str
    total_min: int
    difficulty_es: str
    difficulty_en: str
    steps: list[GuideStep] = field(default_factory=list)


GUIDES: list[Guide] = [
    Guide(
        slug="kimchi",
        category_es="Vegetales",
        category_en="Vegetables",
        title_es="Kimchi de repollo",
        title_en="Napa cabbage kimchi",
        intro_es="Fermentación láctica salada en seco, tradicional de Corea. Resultado: picante, ácido y efervescente.",
        intro_en="Traditional Korean salt-dry lactic fermentation. Result: spicy, sour and effervescent.",
        total_min=60,
        difficulty_es="Intermedia",
        difficulty_en="Intermediate",
        steps=[
            GuideStep(1, "Preparar el repollo", "Prep the cabbage",
                      "Corta el repollo napa en cuartos, salpica sal gruesa entre las hojas (2.5% del peso) y deja reposar 2 horas hasta que suelte agua.",
                      "Cut napa cabbage into quarters, sprinkle coarse salt between leaves (2.5% of weight) and rest 2 hours until it releases water.",
                      duration_min=15, temp_c=21),
            GuideStep(2, "Lavar y mezclar la pasta", "Rinse and mix the paste",
                      "Enjuaga el repollo para retirar el exceso de sal y mezcla la pasta: ajo, jengibre, gochugaru, cebollino, zanahoria y ajo tierno.",
                      "Rinse cabbage to remove excess salt and mix the paste: garlic, ginger, gochugaru, scallions, carrot and garlic chives.",
                      duration_min=30, temp_c=21),
            GuideStep(3, "Empacar en el frasco", "Pack into the jar",
                      "Presiona el kimchi dentro de un frasco limpio hasta que el líquido lo cubra, dejando 3 cm de espacio libre. Cierra sin apretar del todo.",
                      "Press kimchi into a clean jar until liquid covers it, leaving 3 cm of headspace. Close loosely.",
                      duration_min=10, temp_c=21),
            GuideStep(4, "Fermentar a temperatura ambiente", "Ferment at room temperature",
                      "Déjalo 2-4 días a temperatura ambiente fuera de la luz solar, purgando el CO2 a diario. Prueba cada día hasta el punto que prefieras.",
                      "Leave 2-4 days at room temperature away from sunlight, burping daily. Taste daily until it reaches your preferred point.",
                      duration_min=5, temp_c=20, safety=True),
            GuideStep(5, "Madurar en frío", "Cold mature",
                      "Traslada a la nevera. Sigue fermentando lentamente y mejora con las semanas; se conserva meses.",
                      "Move to the fridge. It keeps fermenting slowly and improves over weeks; keeps for months.",
                      duration_min=5, temp_c=4),
        ],
    ),
    Guide(
        slug="chucrut",
        category_es="Vegetales",
        category_en="Vegetables",
        title_es="Chucrut (sauerkraut)",
        title_en="Sauerkraut",
        intro_es="El fermento láctico más sencillo: repollo y sal. Sigue enriqueciéndose con el tiempo.",
        intro_en="The simplest lactic ferment: cabbage and salt. Improves over time.",
        total_min=30,
        difficulty_es="Fácil",
        difficulty_en="Easy",
        steps=[
            GuideStep(1, "Cortar y salar", "Shred and salt",
                      "Corta el repollo en juliana fina y masajea con sal marina al 2-2.5% de su peso hasta que suelte salmuera.",
                      "Finely shred cabbage and massage with sea salt at 2-2.5% of its weight until brine is released.",
                      duration_min=20, temp_c=21),
            GuideStep(2, "Empacar bajo la salmuera", "Pack under brine",
                      "Prensa el repollo en un frasco dejando los vegetales 100% sumergidos. Añade un peso limpio.",
                      "Press cabbage into a jar keeping vegetables 100% submerged. Add a clean weight.",
                      duration_min=10, temp_c=21),
            GuideStep(3, "Fermentar 1-4 semanas", "Ferment 1-4 weeks",
                      "Mantén a 18-21°C fuera de la luz, purgando el CO2 si usas tapa hermética. Catando a partir de la semana.",
                      "Keep at 18-21°C out of light, burping if using an airtight lid. Taste from week one.",
                      duration_min=5, temp_c=19, safety=True),
            GuideStep(4, "Refrigerar", "Refrigerate",
                      "Guarda en frío cuando alcance el punto deseado; dura meses y sigue mejorando.",
                      "Chill once it reaches the desired point; lasts months and keeps improving.",
                      duration_min=5, temp_c=4),
        ],
    ),
    Guide(
        slug="kombucha",
        category_es="Bebidas",
        category_en="Drinks",
        title_es="Kombucha",
        title_en="Kombucha",
        intro_es="Té dulce fermentado por una colonia simbiótica de bacterias y levaduras (SCOBY).",
        intro_en="Sweet tea fermented by a symbiotic colony of bacteria and yeast (SCOBY).",
        total_min=45,
        difficulty_es="Intermedia",
        difficulty_en="Intermediate",
        steps=[
            GuideStep(1, "Preparar el té azucarado", "Prepare sweet tea",
                      "Hierve agua, añade 8 bolsitas de té negro y 150-200 g de azúcar por litro. Deja enfriar a temperatura ambiente.",
                      "Boil water, add 8 black tea bags and 150-200 g of sugar per litre. Cool to room temperature.",
                      duration_min=15, temp_c=25),
            GuideStep(2, "Inocular con el SCOBY", "Inoculate with SCOBY",
                      "Vierte el té frío en un frasco limpio, añade el SCOBY con un poco de kombucha de arranque y cubre con tela transpirable.",
                      "Pour cool tea into a clean jar, add SCOBY with a little starter kombucha and cover with breathable cloth.",
                      duration_min=10, temp_c=25),
            GuideStep(3, "Primera fermentación", "First fermentation",
                      "Fermenta 7-14 días a 22-30°C, fuera de la luz. Aparecerá una nueva película (SCOBY hijo) en la superficie.",
                      "Ferment 7-14 days at 22-30°C, away from light. A new pellicle (baby SCOBY) forms on top.",
                      duration_min=5, temp_c=25, safety=True),
            GuideStep(4, "Embotellar y aromatizar", "Bottle and flavour",
                      "Embotella dejando 2 cm de aire, añade fruta/jengibre si quieres y fermenta 2-4 días más para carbonatación.",
                      "Bottle with 2 cm headspace, add fruit/ginger if desired and ferment 2-4 more days for carbonation.",
                      duration_min=15, temp_c=22),
            GuideStep(5, "Refrigerar", "Refrigerate",
                      "Cuando esté efervescente, refrigera para frenar la fermentación. Consume frío.",
                      "Once fizzy, refrigerate to slow fermentation. Serve chilled.",
                      duration_min=5, temp_c=4),
        ],
    ),
    Guide(
        slug="miso",
        category_es="Fermentos de soja",
        category_en="Soy ferments",
        title_es="Miso casero",
        title_en="Homemade miso",
        intro_es="Soja cocida, sal y koji fermentando meses hasta un condimento umami profundo.",
        intro_en="Cooked soybeans, salt and koji fermenting for months into a deep umami seasoning.",
        total_min=90,
        difficulty_es="Avanzada",
        difficulty_en="Advanced",
        steps=[
            GuideStep(1, "Cocer y machacar la soja", "Cook and mash the soybeans",
                      "Remoja la soja 12 h y cuécela hasta que se deshaga al apretar. Machácala o tritúrala.",
                      "Soak soybeans 12 h and cook until they crush easily. Mash or blend them.",
                      duration_min=60, temp_c=100),
            GuideStep(2, "Mezclar con koji y sal", "Mix with koji and salt",
                      "A 60°C (sin que queme), mezcla con sal (8-12%) y koji (30-50% del peso de soja).",
                      "Once cooled to 60°C (cool enough to handle), mix with salt (8-12%) and koji (30-50% of soybean weight).",
                      duration_min=20, temp_c=60),
            GuideStep(3, "Empacar y presionar", "Pack and press",
                      "Compacta en un recipiente sin burbujas, alisa la superficie y cubre con sal y un peso.",
                      "Pack into a container without air pockets, smooth the surface and top with salt and a weight.",
                      duration_min=10, temp_c=21),
            GuideStep(4, "Madurar 3-12 meses", "Age 3-12 months",
                      "Fermenta a 20-25°C fuera de la luz. Revisa a los 3 meses; el miso más joven es más dulce y salado.",
                      "Ferment at 20-25°C away from light. Check at 3 months; younger miso is sweeter and saltier.",
                      duration_min=5, temp_c=22, safety=True),
        ],
    ),
    Guide(
        slug="yogur",
        category_es="Lácteos",
        category_en="Dairy",
        title_es="Yogur casero",
        title_en="Homemade yogurt",
        intro_es="Leche entera fermentada a 42-45°C con un cultivo vivo de Lactobacillus y Streptococcus.",
        intro_en="Whole milk fermented at 42-45°C with a live Lactobacillus and Streptococcus culture.",
        total_min=45,
        difficulty_es="Fácil",
        difficulty_en="Easy",
        steps=[
            GuideStep(1, "Pasteurizar la leche", "Pasteurise the milk",
                      "Calienta la leche a 85°C durante 1 minuto (mejora la textura) y enfría a 43-45°C.",
                      "Heat milk to 85°C for 1 minute (improves texture) then cool to 43-45°C.",
                      duration_min=20, temp_c=85),
            GuideStep(2, "Inocular el cultivo", "Inoculate the culture",
                      "Añade 2 cucharadas de yogur natural vivo y mezcla suavemente.",
                      "Add 2 tablespoons of live plain yogurt and mix gently.",
                      duration_min=5, temp_c=43),
            GuideStep(3, "Incubar 6-10 horas", "Incubate 6-10 hours",
                      "Mantén a 42-45°C (yogurtera, horno con luz o termos) hasta que cuaje. Más horas = más ácido.",
                      "Keep at 42-45°C (yogurt maker, oven with light or thermos) until set. Longer = more acidic.",
                      duration_min=10, temp_c=43, safety=True),
            GuideStep(4, "Refrigerar", "Refrigerate",
                      "Enfría al menos 4 horas antes de consumir. Se conserva 1-2 semanas.",
                      "Chill at least 4 hours before eating. Keeps 1-2 weeks.",
                      duration_min=10, temp_c=4),
        ],
    ),
]


def _step_out(step: GuideStep, lang: str) -> dict:
    is_en = lang == "en"
    return {
        "number": step.number,
        "title": step.title_en if is_en else step.title_es,
        "body": step.body_en if is_en else step.body_es,
        "duration_min": step.duration_min,
        "temp_c": step.temp_c,
        "safety": step.safety,
    }


def list_guides(lang: str) -> list[dict]:
    is_en = lang == "en"
    return [
        {
            "slug": g.slug,
            "category": g.category_en if is_en else g.category_es,
            "title": g.title_en if is_en else g.title_es,
            "intro": g.intro_en if is_en else g.intro_es,
            "total_min": g.total_min,
            "difficulty": g.difficulty_en if is_en else g.difficulty_es,
            "steps": len(g.steps),
        }
        for g in GUIDES
    ]


def get_guide(slug: str, lang: str) -> dict | None:
    is_en = lang == "en"
    for g in GUIDES:
        if g.slug == slug:
            return {
                "slug": g.slug,
                "category": g.category_en if is_en else g.category_es,
                "title": g.title_en if is_en else g.title_es,
                "intro": g.intro_en if is_en else g.intro_es,
                "total_min": g.total_min,
                "difficulty": g.difficulty_en if is_en else g.difficulty_es,
                "steps": [_step_out(s, lang) for s in g.steps],
            }
    return None