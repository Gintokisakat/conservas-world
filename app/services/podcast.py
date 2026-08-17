"""Podcast index (4.5).

Índice curado de episodios reales de FermUp y Ferment Radio, con enlaces
externos a las fuentes originales (sin embeber audio para respetar derechos).
"""

from dataclasses import dataclass

TOPICS_ES = {
    "ciencia": "Ciencia",
    "cultura": "Cultura e historia",
    "salud": "Salud y microbioma",
    "recetas": "Recetas y técnicas",
    "arte": "Arte y fermentación",
}

TOPICS_EN = {
    "ciencia": "Science",
    "cultura": "Culture & history",
    "salud": "Health & microbiome",
    "recetas": "Recipes & techniques",
    "arte": "Art & fermentation",
}


@dataclass(frozen=True)
class PodcastEpisode:
    show: str
    number: int
    title_es: str
    title_en: str
    topic: str
    ferments: tuple[str, ...]
    duration_min: int | None
    summary_es: str
    summary_en: str
    url: str


EPISODES: tuple[PodcastEpisode, ...] = (
    PodcastEpisode(
        "FermUp", 3, "Coles ácidas", "Sour Cabbages", "recetas",
        ("chucrut", "repollo"), 45,
        "Historia y cómo hacer chucrut: del origen europeo a la técnica casera.",
        "History and how-to of sauerkraut: from its European origins to home technique.",
        "https://www.fermup.com/podcast/3/",
    ),
    PodcastEpisode(
        "FermUp", 95, "Explosiones de fermentación", "Fermentation Explosions", "seguridad",
        ("kombucha",), 55,
        "Kombucha, botellas que explotan y eventos de fermentación. Sección de preguntas de oyentes.",
        "Kombucha, exploding bottles and fermentation events. Listener questions segment.",
        "https://www.fermup.com/podcast/95/",
    ),
    PodcastEpisode(
        "FermUp", 96, "Condimentos como conducto", "Condiment Conduits", "recetas",
        ("condimentos",), 33,
        "Salsas fermentadas como puente entre cocinas y culturas, con ilustración de fermentos.",
        "Fermented condiments as a conduit between cuisines, with ferment illustration.",
        "https://www.fermup.com/podcast/96/",
    ),
    PodcastEpisode(
        "FermUp", 97, "Moscas de la fruta", "Fruit Fly Eggs", "recetas",
        ("kombucha",), 32,
        "Moscas de la fruta en la kombucha y las últimas giras de Fermentation on Wheels.",
        "Fruit flies in kombucha and the latest Fermentation on Wheels travels.",
        "https://www.fermup.com/podcast/97/",
    ),
    PodcastEpisode(
        "FermUp", 99, "Ciruelas umeboshi", "Umeboshi Plums", "recetas",
        ("umeboshi", "encurtidos"), 25,
        "Umeboshi y encurtidos con Ozuke, más el festival de fermentación de Portland.",
        "Umeboshi plums and pickles with Ozuke, plus the Portland fermentation festival.",
        "https://www.fermup.com/podcast/99/",
    ),
    PodcastEpisode(
        "FermUp", 100, "Bill Shurtleff y la soja", "Bill Shurtleff on Soy", "cultura",
        ("miso", "tempeh", "tofu"), 30,
        "Entrevista con Bill Shurtleff del Soy Info Center sobre tofu, miso y tempeh.",
        "Interview with Bill Shurtleff of the Soy Info Center on tofu, miso and tempeh.",
        "https://www.fermup.com/podcast/100/",
    ),
    PodcastEpisode(
        "FermUp", 101, "Sandor Katz", "Sandor Katz", "cultura",
        ("fermentación salvaje",), 24,
        "Conversación con Sandor Katz, autor de The Art of Fermentation, sobre fermentación salvaje.",
        "Conversation with Sandor Katz, author of The Art of Fermentation, on wild fermentation.",
        "https://www.fermup.com/podcast/101/",
    ),
    PodcastEpisode(
        "Ferment Radio", 1, "Fermentation on Wheels", "Fermentation on Wheels", "cultura",
        ("cultura",), 30,
        "Tara Whitsitt cruza EE. UU. enseñando fermentación y repartiendo cultivos iniciadores.",
        "Tara Whitsitt drives across the USA teaching fermentation and sharing starter cultures.",
        "https://fermentradio.com/",
    ),
    PodcastEpisode(
        "Ferment Radio", 14, "Fermentos inuit de Groenlandia", "Greenlandic Inuit Ferments", "cultura",
        ("pescado", "carne"), 35,
        "Aviaja Hauptmann investiga los microbiomas de fermentos nativos de Groenlandia y su legado.",
        "Aviaja Hauptmann researches the microbiomes of native Greenlandic ferments and their legacy.",
        "https://fermentradio.com/",
    ),
    PodcastEpisode(
        "Ferment Radio", 20, "Música fúngica", "Fungi Music", "arte",
        ("micelio",), 30,
        "Tosca Terán traduce bioseñales del micelio de los hongos en música.",
        "Tosca Terán turns biosignals from mushroom mycelium into music.",
        "https://fermentradio.com/",
    ),
    PodcastEpisode(
        "Ferment Radio", 22, "Etnomicrobiología", "Ethnomicrobiology", "cultura",
        ("cultura",), 40,
        "César Enrique Giraldo Herrera acerca la chamanería a la microbiología: una etnomicrobiología.",
        "César Enrique Giraldo Herrera brings shamanism closer to microbiology: an ethnomicrobiology.",
        "https://fermentradio.com/",
    ),
    PodcastEpisode(
        "Ferment Radio", 36, "David Zilber y la Noma", "David Zilber and Noma", "recetas",
        ("noma",), 45,
        "El autor de The Noma Guide to Fermentation recorre su camino del matadero al laboratorio.",
        "The author of The Noma Guide to Fermentation walks from butcher shop to the lab.",
        "https://fermentradio.com/",
    ),
    PodcastEpisode(
        "Ferment Radio", 38, "Tés fermentados de forrajeo", "Foraged Fermented Teas", "recetas",
        ("té",), 35,
        "Paulina Gretkierewicz convierte estaciones y paisajes de Copenhague en tés fermentados.",
        "Paulina Gretkierewicz turns Copenhagen's seasons and landscapes into fermented teas.",
        "https://fermentradio.com/",
    ),
    PodcastEpisode(
        "Ferment Radio", 48, "Descubre a tu microbio interior", "Discover your Microbial Child", "salud",
        ("microbioma",), 40,
        "Zsuzsa Millei explora la relación entre infancia, cuidado y vida microbiana.",
        "Zsuzsa Millei explores the relationship between childhood, care and microbial life.",
        "https://open.spotify.com/episode/5GqKpep4QyHYfaqj499Q3N",
    ),
    PodcastEpisode(
        "Ferment Radio", 49, "Fermentar entre las estrellas", "Ferment Among the Stars", "ciencia",
        ("miso", "koji"), 45,
        "Joshua Evans y su equipo enviaron miso al espacio: microbiología y microgravedad.",
        "Joshua Evans and his team sent miso into space: microbiology and microgravity.",
        "https://open.spotify.com/episode/0QxD2pQ4bmpykqMDtC15HV",
    ),
    PodcastEpisode(
        "Ferment Radio", 51, "Fermento en la Tierra", "Ferment on Earth", "ciencia",
        ("miso", "koji"), 40,
        "El miso vuelve del espacio: qué significa fermentar fuera de la Tierra para los sistemas alimentarios.",
        "The miso returns from space: what fermenting beyond Earth means for earthly food systems.",
        "https://open.spotify.com/episode/1mLsZZR9XpZUXCIxVPTgOl",
    ),
    PodcastEpisode(
        "Ferment Radio", 52, "Siente la ciencia", "Come on Feel the Science", "ciencia",
        ("microbioma",), 40,
        "Kirsty Hendry habla de cómo evolucionan las ideas y el conocimiento sobre el microbioma humano.",
        "Kirsty Hendry discusses how ideas and knowledge about the human microbiome evolve.",
        "https://open.spotify.com/episode/4kFMhTXTuKlLxWHp7tVhV9",
    ),
    PodcastEpisode(
        "Ferment Radio", 53, "Camina tu camino fermentado", "Walk Your Desire Path of Fermentation", "cultura",
        ("yogur",), 40,
        "Johnny Drain, autor de Adventures in Fermentation, del yogur de su abuela a la alta cocina.",
        "Johnny Drain, author of Adventures in Fermentation, from grandma's yogurt to high-end kitchens.",
        "https://open.spotify.com/episode/0n85n0GLOXXs2ytpbXtQAz",
    ),
)


def _episode_out(e: PodcastEpisode, is_en: bool) -> dict:
    return {
        "id": f"{e.show.lower().replace(' ', '-')}-{e.number}",
        "show": e.show,
        "number": e.number,
        "title": e.title_en if is_en else e.title_es,
        "topic": e.topic,
        "ferments": list(e.ferments),
        "duration_min": e.duration_min,
        "summary": e.summary_en if is_en else e.summary_es,
        "url": e.url,
    }


def list_episodes(
    topic: str | None = None,
    ferment: str | None = None,
    limit: int = 50,
    lang: str = "es",
) -> list[dict]:
    is_en = lang == "en"
    out = []
    for e in EPISODES:
        if topic and e.topic != topic:
            continue
        if ferment:
            f = ferment.lower()
            if not any(f in tag.lower() for tag in e.ferments):
                continue
        out.append(_episode_out(e, is_en))
    return out[:limit]


def topics_out(lang: str = "es") -> list[dict]:
    table = TOPICS_EN if lang == "en" else TOPICS_ES
    return [{"key": k, "label": v} for k, v in table.items()]


def ferments_out() -> list[str]:
    seen: set[str] = set()
    out = []
    for e in EPISODES:
        for f in e.ferments:
            if f not in seen:
                seen.add(f)
                out.append(f)
    return sorted(out)