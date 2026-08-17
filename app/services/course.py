"""Curso de fermentación (4.4).

Contenido educativo curado en código (5 módulos), bilingüe ES/EN, sin auth:
el progreso y el certificado se gestionan en el frontend (localStorage).
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class LessonSection:
    heading_es: str
    heading_en: str
    body_es: str
    body_en: str
    bullets_es: tuple[str, ...] = ()
    bullets_en: tuple[str, ...] = ()


@dataclass(frozen=True)
class Lesson:
    slug: str
    title_es: str
    title_en: str
    duration_min: int
    sections: tuple[LessonSection, ...]


@dataclass(frozen=True)
class CourseModule:
    slug: str
    title_es: str
    title_en: str
    subtitle_es: str
    subtitle_en: str
    difficulty: int
    estimated_hours: int
    lessons: tuple[Lesson, ...]


MODULES: tuple[CourseModule, ...] = (
    CourseModule(
        slug="historia",
        title_es="Historia de la fermentación",
        title_en="History of fermentation",
        subtitle_es="De los orígenes prehistóricos al renacimiento artesanal.",
        subtitle_en="From prehistoric origins to the artisanal renaissance.",
        difficulty=1,
        estimated_hours=1,
        lessons=(
            Lesson(
                slug="origenes",
                title_es="Orígenes prehistóricos",
                title_en="Prehistoric origins",
                duration_min=12,
                sections=(
                    LessonSection(
                        "Las conservas más antiguas",
                        "The oldest preserves",
                        "La fermentación es anterior a la agricultura: vasijas de 8.000 años en Jiahu (China) contienen restos de una bebida fermentada de arroz, miel y frutas.",
                        "Fermentation predates agriculture: 8,000-year-old vessels at Jiahu (China) hold traces of a fermented drink of rice, honey and fruit.",
                        ("La primera fermentación fue accidental", "El control llegó con la cerámica", "La levadura domesticada viajó con la migración humana"),
                        ("The first fermentation was accidental", "Control came with pottery", "Domesticated yeast travelled with human migration"),
                    ),
                    LessonSection(
                        "¿Por qué fermentar?",
                        "Why ferment?",
                        "Sin refrigeración, fermentar era la forma principal de conservar cosechas y carne. También eliminaba toxinas y mejoraba la digestibilidad.",
                        "Without refrigeration, fermentation was the main way to preserve harvests and meat. It also removed toxins and improved digestibility.",
                    ),
                ),
            ),
            Lesson(
                slug="mundo-antiguo",
                title_es="Fermentos del mundo antiguo",
                title_en="Ferments of the ancient world",
                duration_min=12,
                sections=(
                    LessonSection(
                        "Del Nilo al Danubio",
                        "From the Nile to the Danube",
                        "Egipto hizo pan y cerveza; Mesopotamia, vino y queso; Grecia y Roma, garum y vinagre; Asia, miso, tempeh y kimchi.",
                        "Egypt made bread and beer; Mesopotamia, wine and cheese; Greece and Rome, garum and vinegar; Asia, miso, tempeh and kimchi.",
                        ("Garum: salsa de pescado del Mediterráneo", "La cerveza se pagaba como salario en Egipto", "El vinagre se usaba como desinfectante"),
                        ("Garum: Mediterranean fish sauce", "Beer was paid as wages in Egypt", "Vinegar was used as a disinfectant"),
                    ),
                ),
            ),
            Lesson(
                slug="era-industrial",
                title_es="Edad Media y era industrial",
                title_en="Middle Ages and the industrial era",
                duration_min=10,
                sections=(
                    LessonSection(
                        "Chucrut en los barcos",
                        "Sauerkraut on the ships",
                        "Cook ordenó chucrut para la Marina Real para combatir el escorbuto. Pasteur explicó en 1857 que la fermentación la causan microorganismos.",
                        "Cook ordered sauerkraut for the Royal Navy against scurvy. Pasteur showed in 1857 that fermentation is caused by microorganisms.",
                    ),
                    LessonSection(
                        "La industrialización",
                        "Industrialisation",
                        "La pasteurización, la refrigeración y los cultivos puros desplazaron la fermentación espontánea hacia producción a gran escala y estándares higiénicos.",
                        "Pasteurisation, refrigeration and pure cultures moved spontaneous fermentation toward large-scale production and hygienic standards.",
                    ),
                ),
            ),
            Lesson(
                slug="renacimiento",
                title_es="Resurgimiento moderno",
                title_en="Modern revival",
                duration_min=8,
                sections=(
                    LessonSection(
                        "El boom artesanal",
                        "The artisanal boom",
                        "Desde 2010 el interés por la salud intestinal, los sabores complejos y la sostenibilidad ha impulsado un renacimiento de la fermentación casera y de proximidad.",
                        "Since 2010, interest in gut health, complex flavours and sustainability has driven a renaissance of home and local fermentation.",
                    ),
                ),
            ),
        ),
    ),
    CourseModule(
        slug="ciencia",
        title_es="Ciencia básica",
        title_en="Basic science",
        subtitle_es="Quiénes fermentan, qué comen y cómo controlarlo.",
        subtitle_en="Who ferments, what they eat, and how to control it.",
        difficulty=2,
        estimated_hours=1,
        lessons=(
            Lesson(
                slug="microorganismos",
                title_es="Los microorganismos",
                title_en="The microorganisms",
                duration_min=14,
                sections=(
                    LessonSection(
                        "Bacterias, levaduras y mohos",
                        "Bacteria, yeast and moulds",
                        "Los actores principales son bacterias lácticas (Lactobacillus, Leuconostoc), levaduras (Saccharomyces) y mohos nobles (Aspergillus, Penicillium).",
                        "The main actors are lactic acid bacteria (Lactobacillus, Leuconostoc), yeast (Saccharomyces) and noble moulds (Aspergillus, Penicillium).",
                        ("Las lácticas producen ácido láctico", "Las levaduras producen etanol y CO₂", "Los mohos digieren almidones y proteínas"),
                        ("LAB produce lactic acid", "Yeast produces ethanol and CO₂", "Moulds digest starches and proteins"),
                    ),
                    LessonSection(
                        "Quién gana la carrera",
                        "Who wins the race",
                        "En la lactofermentación, las lácticas acidifican rápido y bajan el pH por debajo de 4,6, excluyendo a patógenos. En salmuera, la sal selecciona especies.",
                        "In lacto-fermentation, LAB acidify fast and drop pH below 4.6, excluding pathogens. In brine, salt selects the species.",
                    ),
                ),
            ),
            Lesson(
                slug="quimica",
                title_es="Química de la fermentación",
                title_en="Chemistry of fermentation",
                duration_min=14,
                sections=(
                    LessonSection(
                        "pH, sal, azúcar y agua",
                        "pH, salt, sugar and water",
                        "El pH mide acidez (fermentos seguros: <4,6). La sal deshidrata, dificulta patógenos y favorece las lácticas. El azúcar alimenta las levaduras. El agua es el vehículo.",
                        "pH measures acidity (safe ferments: <4.6). Salt dehydrates, hinders pathogens and favours LAB. Sugar feeds yeast. Water is the vehicle.",
                        ("pH < 4,6 bloquea Clostridium botulinum", "2-5% de sal en peso es el rango lacto típico", "Agua clorada inhibe la fermentación"),
                        ("pH < 4.6 blocks Clostridium botulinum", "2-5% salt by weight is the typical lacto range", "Chlorinated water inhibits fermentation"),
                    ),
                ),
            ),
            Lesson(
                slug="anaerobiosis",
                title_es="Anaerobiosis y oxígeno",
                title_en="Anaerobiosis and oxygen",
                duration_min=10,
                sections=(
                    LessonSection(
                        "Sin aire, sin mohos",
                        "No air, no moulds",
                        "Mantener los vegetales sumergidos crea anaerobiosis: los mohos necesitan oxígeno, las lácticas no. Un sello de agua deja escapar el CO₂.",
                        "Keeping vegetables submerged creates anaerobiosis: moulds need oxygen, LAB do not. An airlock lets CO₂ escape.",
                    ),
                ),
            ),
            Lesson(
                slug="tiempo-temperatura",
                title_es="Temperatura y tiempo",
                title_en="Temperature and time",
                duration_min=10,
                sections=(
                    LessonSection(
                        "Velocidad de reacción",
                        "Reaction speed",
                        "La actividad microbiana se duplica aprox. cada 10 °C (regla Q10). Más calor fermenta más rápido pero produce sabores menos delicados.",
                        "Microbial activity roughly doubles every 10 °C (Q10 rule). More heat ferments faster but yields less delicate flavours.",
                        ("15-20 °C: sabores delicados, más lentos", "20-25 °C: rango lacto equilibrado", ">30 °C: riesgo de fermentos no deseados"),
                        ("15-20 °C: delicate, slower flavours", "20-25 °C: balanced lacto range", ">30 °C: risk of unwanted ferments"),
                    ),
                ),
            ),
        ),
    ),
    CourseModule(
        slug="tipos",
        title_es="Tipos de fermentación",
        title_en="Types of fermentation",
        subtitle_es="Láctea, alcohólica, acética y con mohos.",
        subtitle_en="Lactic, alcoholic, acetic, and mould-based.",
        difficulty=2,
        estimated_hours=1,
        lessons=(
            Lesson(
                slug="lacto",
                title_es="Lactofermentación",
                title_en="Lacto-fermentation",
                duration_min=12,
                sections=(
                    LessonSection(
                        "Vegetales en salmuera",
                        "Vegetables in brine",
                        "Chucrut, kimchi y pepinillos: vegetales + sal, sumergidos, a temperatura ambiente durante días o semanas. Produce ácido láctico y probióticos.",
                        "Sauerkraut, kimchi and pickles: vegetables + salt, submerged, at room temperature for days or weeks. Produces lactic acid and probiotics.",
                        ("Ejemplos: chucrut, kimchi, curtidos", "Rango de sal típico: 2-5%", "Resultado: crujiente y ácido"),
                        ("Examples: sauerkraut, kimchi, pickles", "Typical salt range: 2-5%", "Result: crunchy and sour"),
                    ),
                ),
            ),
            Lesson(
                slug="alcoholica",
                title_es="Fermentación alcohólica",
                title_en="Alcoholic fermentation",
                duration_min=10,
                sections=(
                    LessonSection(
                        "De azúcar a alcohol",
                        "From sugar to alcohol",
                        "Levaduras convierten azúcares en etanol y CO₂: cerveza, vino, sake, sidra y kombucha (en parte). Requiere azúcares disponibles y anaerobiosis.",
                        "Yeast converts sugars into ethanol and CO₂: beer, wine, sake, cider and kombucha (in part). Needs available sugars and anaerobiosis.",
                    ),
                ),
            ),
            Lesson(
                slug="acetica",
                title_es="Fermentación acética",
                title_en="Acetic fermentation",
                duration_min=10,
                sections=(
                    LessonSection(
                        "Del vino al vinagre",
                        "From wine to vinegar",
                        "Bacterias acéticas (Acetobacter) oxidan el alcohol a ácido acético en presencia de oxígeno. Por eso el vinagre necesita aire y la 'madre'.",
                        "Acetic bacteria (Acetobacter) oxidise alcohol into acetic acid in the presence of oxygen. That is why vinegar needs air and the 'mother'.",
                    ),
                ),
            ),
            Lesson(
                slug="mohos",
                title_es="Fermentación con mohos",
                title_en="Mould-based fermentation",
                duration_min=12,
                sections=(
                    LessonSection(
                        "Koji, miso, tempeh y queso",
                        "Koji, miso, tempeh and cheese",
                        "Aspergillus oryzae en el koji, Rhizopus en el tempeh, Penicillium en quesos y hongos en el natto: mohos que digieren almidón y proteína.",
                        "Aspergillus oryzae in koji, Rhizopus in tempeh, Penicillium in cheeses and bacteria in natto: moulds that break down starch and protein.",
                        ("El koji inocula miso, sake y shoyu", "El tempeh se inocula con Rhizopus", "Corteza de queso: Penicillium"),
                        ("Koji inoculates miso, sake and shoyu", "Tempeh is inoculated with Rhizopus", "Cheese rind: Penicillium"),
                    ),
                ),
            ),
            Lesson(
                slug="lacteos",
                title_es="Fermentos lácteos",
                title_en="Dairy ferments",
                duration_min=10,
                sections=(
                    LessonSection(
                        "Yogur, kéfir y quesos",
                        "Yogurt, kefir and cheese",
                        "Lácticas coagulan la leche y producen acidez: yogur (Streptococcus + Lactobacillus), kéfir (simbiosis de granos), quesos (cuajo + cultivos).",
                        "LAB coagulate milk and produce acidity: yogurt (Streptococcus + Lactobacillus), kefir (grain symbiosis), cheeses (rennet + cultures).",
                    ),
                ),
            ),
        ),
    ),
    CourseModule(
        slug="seguridad",
        title_es="Seguridad",
        title_en="Safety",
        subtitle_es="Cómo fermentar sin riesgos y detectar alertas.",
        subtitle_en="How to ferment safely and spot warnings.",
        difficulty=1,
        estimated_hours=1,
        lessons=(
            Lesson(
                slug="principios",
                title_es="Principios de conservación",
                title_en="Preservation principles",
                duration_min=12,
                sections=(
                    LessonSection(
                        "Tres barreras",
                        "Three barriers",
                        "Acidez (pH <4,6), sal (aw baja) y anaerobiosis bloquean patógenos. Combinadas, hacen el fermento seguro para consumo.",
                        "Acidity (pH <4.6), salt (low aw) and anaerobiosis block pathogens. Combined, they make the ferment safe to eat.",
                    ),
                ),
            ),
            Lesson(
                slug="alarmas",
                title_es="Señales de alarma",
                title_en="Warning signs",
                duration_min=12,
                sections=(
                    LessonSection(
                        "Cuándo descartar",
                        "When to discard",
                        "Descartar si hay moho negro/verde/rosado (no el blanco en curtidos), olor pútrido, viscosidad extrema o textura 'babosa' con mal olor.",
                        "Discard if there is black/green/pink mould (not white on pickles), putrid smell, extreme sliminess or a slimy texture with a bad odour.",
                        ("El moho blanco en la salmuera suele ser Kahm, inocuo", "El CO₂ excesivo puede romper frascos: ventilar", "Sabor amargo + burbujas anómalas = descartar"),
                        ("White mould on brine is usually harmless Kahm", "Excess CO₂ can burst jars: vent them", "Bitter taste + odd bubbles = discard"),
                    ),
                ),
            ),
            Lesson(
                slug="botulismo",
                title_es="Botulismo y pH",
                title_en="Botulism and pH",
                duration_min=12,
                sections=(
                    LessonSection(
                        "Clostridium botulinum",
                        "Clostridium botulinum",
                        "C. botulinum forma esporas resistentes y produce toxina en ambientes sin oxígeno, poco ácidos y con baja sal. Por eso el enlatado exige pH <4,6 o presión.",
                        "C. botulinum forms resistant spores and produces toxin in low-oxygen, low-acid, low-salt environments. That is why canning requires pH <4.6 or pressure.",
                        ("Nunca probar conservas de baja acidez sospechosas", "Acidificar con vinagre o lactofermentar reduce el riesgo", "La toxina se destruye hirviendo 10 min"),
                        ("Never taste suspect low-acid preserves", "Acidifying with vinegar or lacto-fermentation lowers risk", "The toxin is destroyed by boiling 10 min"),
                    ),
                ),
            ),
            Lesson(
                slug="buenas-practicas",
                title_es="Buenas prácticas",
                title_en="Good practices",
                duration_min=10,
                sections=(
                    LessonSection(
                        "Higiene y registro",
                        "Hygiene and records",
                        "Utensilios limpios, manos lavadas, salmuera cubriendo todo, etiquetar fecha y lote. Registrar pH y temperatura en lotes grandes.",
                        "Clean tools, washed hands, brine covering everything, label date and batch. Record pH and temperature on large batches.",
                    ),
                ),
            ),
        ),
    ),
    CourseModule(
        slug="recetas",
        title_es="Recetas prácticas",
        title_en="Practical recipes",
        subtitle_es="Cinco recetas para empezar, paso a paso.",
        subtitle_en="Five recipes to get started, step by step.",
        difficulty=1,
        estimated_hours=2,
        lessons=(
            Lesson(
                slug="chucrut",
                title_es="Chucrut básico",
                title_en="Basic sauerkraut",
                duration_min=20,
                sections=(
                    LessonSection(
                        "Repollo + 2% sal",
                        "Cabbage + 2% salt",
                        "Rallar repollo, mezclar con 20 g de sal por kg, machacar hasta soltar agua, envasar bien prensado y cubierto, fermentar 1-4 semanas a 20 °C.",
                        "Shred cabbage, mix with 20 g salt per kg, pound until juices release, pack tightly and submerged, ferment 1-4 weeks at 20 °C.",
                    ),
                ),
            ),
            Lesson(
                slug="kimchi",
                title_es="Kimchi clásico",
                title_en="Classic kimchi",
                duration_min=25,
                sections=(
                    LessonSection(
                        "Baechu kimchi",
                        "Baechu kimchi",
                        "Salar la col en salmuera al 3% durante 2-6 h, enjuagar, mezclar con pasta de ajo, jengibre, gochugaru y pescado/verdura, fermentar 2-7 días.",
                        "Brine the cabbage at 3% for 2-6 h, rinse, mix with a paste of garlic, ginger, gochugaru and fish/veggie, ferment 2-7 days.",
                    ),
                ),
            ),
            Lesson(
                slug="kombucha",
                title_es="Kombucha",
                title_en="Kombucha",
                duration_min=20,
                sections=(
                    LessonSection(
                        "Té + azúcar + SCOBY",
                        "Tea + sugar + SCOBY",
                        "Preparar té dulce al 7-8%, enfriar, añadir SCOBY y líquido previo, fermentar 7-14 días a 22-26 °C, luego segunda fermentación con fruta para carbona.",
                        "Brew sweet tea at 7-8%, cool, add SCOBY and starter liquid, ferment 7-14 days at 22-26 °C, then second ferment with fruit to carbonate.",
                    ),
                ),
            ),
            Lesson(
                slug="yogur",
                title_es="Yogur casero",
                title_en="Homemade yogurt",
                duration_min=20,
                sections=(
                    LessonSection(
                        "Leche + cultivo",
                        "Milk + culture",
                        "Calentar leche a 82 °C, enfriar a 43 °C, inocular 2 cucharadas de yogur, mantener 4-8 h a 43 °C hasta cuajar, refrigerar.",
                        "Heat milk to 82 °C, cool to 43 °C, inoculate 2 tablespoons of yogurt, hold 4-8 h at 43 °C until set, refrigerate.",
                    ),
                ),
            ),
            Lesson(
                slug="miso",
                title_es="Miso casero",
                title_en="Homemade miso",
                duration_min=30,
                sections=(
                    LessonSection(
                        "Soja + koji + sal",
                        "Soybeans + koji + salt",
                        "Cocer y triturar soja, mezclar con koji y 8-12% de sal, prensar en un tarro, fermentar 3-12 meses a 15-20 °C con poco oxígeno.",
                        "Cook and mash soybeans, mix with koji and 8-12% salt, press into a jar, ferment 3-12 months at 15-20 °C with little oxygen.",
                    ),
                ),
            ),
        ),
    ),
)


def module_list(lang: str = "es") -> list[dict]:
    is_en = lang == "en"
    return [
        {
            "slug": m.slug,
            "title": m.title_en if is_en else m.title_es,
            "subtitle": m.subtitle_en if is_en else m.subtitle_es,
            "difficulty": m.difficulty,
            "estimated_hours": m.estimated_hours,
            "lesson_count": len(m.lessons),
        }
        for m in MODULES
    ]


def _section_out(s: LessonSection, is_en: bool) -> dict:
    return {
        "heading": s.heading_en if is_en else s.heading_es,
        "body": s.body_en if is_en else s.body_es,
        "bullets": list(s.bullets_en if is_en else s.bullets_es),
    }


def module_detail(slug: str, lang: str = "es") -> dict | None:
    is_en = lang == "en"
    for m in MODULES:
        if m.slug == slug:
            return {
                "slug": m.slug,
                "title": m.title_en if is_en else m.title_es,
                "subtitle": m.subtitle_en if is_en else m.subtitle_es,
                "difficulty": m.difficulty,
                "estimated_hours": m.estimated_hours,
                "lesson_count": len(m.lessons),
                "lessons": [
                    {
                        "slug": lesson.slug,
                        "title": lesson.title_en if is_en else lesson.title_es,
                        "duration_min": lesson.duration_min,
                        "sections": [_section_out(s, is_en) for s in lesson.sections],
                    }
                    for lesson in m.lessons
                ],
            }
    return None