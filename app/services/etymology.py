"""Etimología de alimentos fermentados (2.9).

Contenido curado en código para términos emblemáticos de fermentación,
sin depender del dataset etymology-db (~500MB) ni de scraping. La búsqueda
coincide por nombre de ingrediente o de producto.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Etymology:
    term: str
    origin: str
    period: str
    es: str
    en: str


ENTRIES: dict[str, Etymology] = {
    "kimchi": Etymology(
        "kimchi", "coreano 김치", "S. VII d.C.",
        "Del coreano 'kimchi', a su vez del chino antiguo 'chimchae' (vegetales en salmuera). La forma actual se consolidó en el siglo VII con la llegada del chile en el XVI.",
        "From Korean 'kimchi', from Old Chinese 'chimchae' (salted vegetables). The modern form emerged in the 7th century, with chili arriving in the 16th.",
    ),
    "sauerkraut": Etymology(
        "sauerkraut", "alemán", "S. XVI d.C.",
        "Del alemán 'sauer' (ácido) + 'Kraut' (repollo o hierba). La palabra viajó por Europa: 'chucrut' en español y 'sourkrout' en inglés antiguo.",
        "From German 'sauer' (sour) + 'Kraut' (cabbage or herb). The word travelled through Europe: 'chucrut' in Spanish and 'sourcrout' in old English.",
    ),
    "miso": Etymology(
        "miso", "japonés 味噌", "S. VIII d.C.",
        "Del japonés 'miso', del chino antiguo 'hisho' (pasta de soja fermentada). El carácter 味 significa 'sabor' y 噌 deriva de 'condimento'.",
        "From Japanese 'miso', from Old Chinese 'hisho' (fermented soybean paste). The character 味 means 'flavour' and 噌 derives from 'seasoning'.",
    ),
    "kombucha": Etymology(
        "kombucha", "japonés 昆布茶", "S. XIX d.C.",
        "Del japonés 'konbu' (alga) + 'cha' (té); originalmente un té de algas en Japón. En Occidente se adoptó para el té fermentado con SCOBY.",
        "From Japanese 'konbu' (kelp) + 'cha' (tea); originally a kelp tea in Japan. The West adopted it for SCOBY-fermented tea.",
    ),
    "yogurt": Etymology(
        "yogur", "turco 'yoğurt'", "S. XI d.C.",
        "Del turco otomano 'yoğurt', de la raíz 'yoğurmak' (espesar o amasar). Entró en las lenguas europeas a través del búlgaro en el siglo XIX.",
        "From Ottoman Turkish 'yoğurt', from the root 'yoğurmak' (to thicken or knead). It reached European languages via Bulgarian in the 19th century.",
    ),
    "kefir": Etymology(
        "kéfir", "turco 'köpük'", "S. XIX d.C.",
        "Del turco 'köpük' (espuma), por la efervescencia del fermento. Los granos de kéfir se nombran así desde el Cáucaso, donde se originaron.",
        "From Turkish 'köpük' (foam), for the ferment's effervescence. Kefir grains have been named so since their origins in the Caucasus.",
    ),
    "vinagre": Etymology(
        "vinagre", "francés 'vinaigre'", "S. XIII d.C.",
        "Del francés 'vinaigre', contracción de 'vin' (vino) + 'aigre' (agrio). Del latín 'vinum acre'. El inglés 'vinegar' comparte el mismo origen.",
        "From French 'vinaigre', contraction of 'vin' (wine) + 'aigre' (sour). From Latin 'vinum acre'. English 'vinegar' shares the same origin.",
    ),
    "chucrut": Etymology(
        "chucrut", "francés 'choucroute'", "S. XVIII d.C.",
        "Del francés 'choucroute', adaptación del alemán 'Sauerkraut'. Llegó al español y al resto de Europa con las guerras y la migración.",
        "From French 'choucroute', adaptation of German 'Sauerkraut'. It reached Spanish and the rest of Europe through wars and migration.",
    ),
    "tempeh": Etymology(
        "tempeh", "javanés 'témpé'", "S. XVII d.C.",
        "Del javanés 'témpé', alimento tradicional de Java. Documentado por colonos holandeses en el siglo XVII como 'tempeh'.",
        "From Javanese 'témpé', a traditional Java food. Documented by Dutch colonists in the 17th century as 'tempeh'.",
    ),
    "natto": Etymology(
        "natto", "japonés 納豆", "S. XI d.C.",
        "Del japonés 'nattō' (納 = almacenado, 豆 = frijol). Referido al frijol de soja fermentado conservado en paja de arroz.",
        "From Japanese 'nattō' (納 = stored, 豆 = bean). Refers to soybeans fermented and stored in rice straw.",
    ),
    "garum": Etymology(
        "garum", "latín", "S. I a.C.",
        "Del latín 'garum', del griego 'gáron'. Salsa de pescado fermentado del Mediterráneo clásico, antecesora del 'nam pla' tailandés.",
        "From Latin 'garum', from Greek 'gáron'. A fermented fish sauce of the classical Mediterranean, ancestor of Thai 'nam pla'.",
    ),
    "escabeche": Etymology(
        "escabeche", "árabe 'sikbāj'", "S. XII d.C.",
        "Del árabe andalusí 'sikbāj' (guiso avinagrado), del persa 'sikbā'. Técnica de conserva agria llegada a España en la Edad Media.",
        "From Andalusian Arabic 'sikbāj' (vinegared stew), from Persian 'sikbā'. A sour preservation technique that reached Spain in the Middle Ages.",
    ),
    "miso_koji": Etymology(
        "koji", "japonés 麹", "S. VIII d.C.",
        "Del japonés 'kōji' (麹), la levadura de arroz que inocula miso, sake y shoyu. La técnica llegó de China con la fermentación de grano.",
        "From Japanese 'kōji' (麹), the rice mold that inoculates miso, sake and shoyu. The technique came from China with grain fermentation.",
    ),
    "pickle": Etymology(
        "pickle", "neerlandés 'pekel'", "S. XVI d.C.",
        "Del neerlandés 'pekel' (salmuera) o del bajo alemán 'pōkel'. El inglés 'to pickle' (encurtir) deriva de este término salmuerado.",
        "From Dutch 'pekel' (brine) or Low German 'pōkel'. English 'to pickle' derives from this brining term.",
    ),
    "shoyu": Etymology(
        "shoyu", "japonés 醤油", "S. XVI d.C.",
        "Del japonés 'shōyu' (醤油, pasta de soja + aceite). Derivado del chino 'jiàngyóu' (salsa de soja). El 'soy sauce' inglés viene de 'shoyu'.",
        "From Japanese 'shōyu' (醤油, soybean paste + oil). Derived from Chinese 'jiàngyóu' (soy sauce). English 'soy sauce' comes from 'shoyu'.",
    ),
    "sourdough": Etymology(
        "sourdough", "inglés", "S. XVII d.C.",
        "Del inglés 'sour' (ácido) + 'dough' (masa). El 'masa madre' en español refleja la idea de una masa que 'madre' al pan.",
        "From English 'sour' + 'dough'. Spanish 'masa madre' (mother dough) reflects the idea of a dough that gives birth to bread.",
    ),
    "brine": Etymology(
        "salmuera", "latín 'salamura'", "S. X d.C.",
        "Del latín tardío 'salamura', de 'sal' (sal) + 'muria' (agua salada). El inglés 'brine' comparte raíz con 'sal' y 'saline'.",
        "From Late Latin 'salamura', from 'sal' (salt) + 'muria' (salt water). English 'brine' shares roots with 'sal' and 'saline'.",
    ),
    "kombucha_scoby": Etymology(
        "scoby", "inglés (sigla)", "S. XX d.C.",
        "Acrónimo de 'Symbiotic Culture Of Bacteria and Yeast', acuñado en inglés en 1995 por Len Porchet. La película se llama también 'madre'.",
        "Acronym for 'Symbiotic Culture Of Bacteria and Yeast', coined in English in 1995 by Len Porchet. The pellicle is also called the 'mother'.",
    ),
    "aji": Etymology(
        "aji", "taíno", "S. XV d.C.",
        "Del taíno 'ají', una de las primeras palabras americanas incorporadas al español por Colón. Designa los chiles en muchas regiones.",
        "From Taino 'ají', one of the first American words adopted into Spanish by Columbus. It names chiles in many regions.",
    ),
    "chipotle": Etymology(
        "chipotle", "náhuatl 'chīlpoctli'", "S. XVI d.C.",
        "Del náhuatl 'chīlpoctli': 'chīlli' (chile) + 'poctli' (ahumado). Chile ahumado, técnica de conservación prehispánica.",
        "From Nahuatl 'chīlpoctli': 'chīlli' (chili) + 'poctli' (smoked). A smoked chili, a pre-Hispanic preservation technique.",
    ),
    "soy": Etymology(
        "soja", "japonés 'shōyu'", "S. XVII d.C.",
        "El inglés 'soy' viene del japonés 'shōyu' (salsa de soja). El español 'soja' deriva del neerlandés 'soja', del japonés 'shōyu'.",
        "English 'soy' comes from Japanese 'shōyu' (soy sauce). Spanish 'soja' derives from Dutch 'soja', from Japanese 'shōyu'.",
    ),
}


def _normalize(term: str) -> str:
    return term.lower().strip()


def lookup(term: str) -> Etymology | None:
    t = _normalize(term)
    if not t:
        return None
    for key, entry in ENTRIES.items():
        if t == key or t in key or key in t:
            return entry
    return None


def search_terms(query: str, limit: int = 8) -> list[dict]:
    q = _normalize(query)
    if not q:
        return []
    matches = []
    for key, entry in ENTRIES.items():
        if q in key or key in q:
            matches.append({"term": entry.term, "origin": entry.origin, "period": entry.period})
    return matches[:limit]


def etymology_out(entry: Etymology, lang: str = "es") -> dict:
    is_en = lang == "en"
    return {
        "term": entry.term,
        "origin": entry.origin,
        "period": entry.period,
        "text": entry.en if is_en else entry.es,
    }