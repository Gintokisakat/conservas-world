from pydantic import BaseModel, ConfigDict


class CountryOut(BaseModel):
    id: int
    name: str
    iso2: str | None
    iso3: str | None
    continent: str | None

    model_config = ConfigDict(from_attributes=True)


class IngredientOut(BaseModel):
    id: int
    name: str
    category: str | None

    model_config = ConfigDict(from_attributes=True)


class NutritionOut(BaseModel):
    fdc_id: str
    calories: float | None = None
    protein_g: float | None = None
    fat_g: float | None = None
    carbs_g: float | None = None
    fiber_g: float | None = None
    sodium_mg: float | None = None
    potassium_mg: float | None = None
    vitamin_c_mg: float | None = None
    iron_mg: float | None = None
    calcium_mg: float | None = None
    zinc_mg: float | None = None

    model_config = ConfigDict(from_attributes=True)


class CategoryOut(BaseModel):
    id: int
    code: str
    name: str
    description: str | None

    model_config = ConfigDict(from_attributes=True)


class ReferenceOut(BaseModel):
    id: int
    title: str
    ref_type: str | None
    url: str | None
    doi: str | None

    model_config = ConfigDict(from_attributes=True)


class AliasOut(BaseModel):
    id: int
    name: str
    language: str | None

    model_config = ConfigDict(from_attributes=True)


class MicrobeOut(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


class DairyFermentOut(BaseModel):
    classification: str | None = None
    country: str | None = None
    region: str | None = None
    milk_type: str | None = None
    treatment: str | None = None
    ripening: str | None = None
    microbiota: list[str] = []
    geographical_indication: bool = False
    characteristics: str | None = None

    model_config = ConfigDict(from_attributes=True)


class CheeseMetagenomeOut(BaseModel):
    subtype: str
    sample_count: int = 0
    taxa: list[dict] = []
    url: str | None = None

    model_config = ConfigDict(from_attributes=True)


class ProductOut(BaseModel):
    id: int
    name: str
    description: str | None
    method: str | None
    fermentation_time: str | None
    storage_life: str | None = None
    status: str
    source_tag: str | None
    substrate: str | None
    image_url: str | None = None
    aliases: list[AliasOut] = []
    countries: list[CountryOut] = []
    ingredients: list[IngredientOut] = []
    categories: list[CategoryOut] = []
    microbes: list[MicrobeOut] = []
    references: list[ReferenceOut] = []
    uses: list[str] = []
    used_by: list[str] = []
    diet_tags: list[str] = []
    dairy: DairyFermentOut | None = None
    metagenome: CheeseMetagenomeOut | None = None

    model_config = ConfigDict(from_attributes=True)


class ProductListItem(BaseModel):
    id: int
    name: str
    description: str | None
    source_tag: str | None
    substrate: str | None
    image_url: str | None = None
    fermentation_time: str | None = None
    storage_life: str | None = None
    categories: list[CategoryOut] = []
    countries: list[CountryOut] = []
    diet_tags: list[str] = []
    geographical_indication: bool = False

    model_config = ConfigDict(from_attributes=True)


class GeoPointOut(BaseModel):
    id: int
    name: str
    lat: float
    lng: float
    country: str | None = None
    continent: str | None = None
    category: str | None = None
    source_tag: str | None = None
    substrate: str | None = None


class PairingOut(BaseModel):
    id: int
    name: str
    description: str | None
    source_tag: str | None
    substrate: str | None
    image_url: str | None = None
    categories: list[CategoryOut] = []
    countries: list[CountryOut] = []
    shared_ingredients: list[str] = []
    score: float


class PairingsOut(BaseModel):
    product_id: int
    product_name: str
    total: int
    items: list[PairingOut]


class PaginatedProducts(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[ProductListItem]


class SuggestItem(BaseModel):
    type: str
    id: int
    name: str
    category: str | None = None
    country: str | None = None
    substrate: str | None = None


class SearchSuggest(BaseModel):
    products: list[SuggestItem] = []
    ingredients: list[SuggestItem] = []
    glossary: list[SuggestItem] = []


class GlossaryOut(BaseModel):
    id: int
    term: str
    definition: str
    language: str
    related_product_id: int | None = None
    related_product: str | None = None


class RecommendationOut(BaseModel):
    id: int
    name: str
    description: str | None
    source_tag: str | None
    substrate: str | None
    categories: list[CategoryOut] = []
    countries: list[CountryOut] = []
    matched: list[str] = []
    missing: list[str] = []


class UseRecommendationOut(BaseModel):
    id: int
    name: str
    description: str | None
    source_tag: str | None
    substrate: str | None
    categories: list[CategoryOut] = []
    countries: list[CountryOut] = []
    uses_products: list[str] = []


class Recommendations(BaseModel):
    make: list[RecommendationOut] = []
    use: list[UseRecommendationOut] = []


class Stats(BaseModel):
    products: int
    countries: int
    ingredients: int
    categories: int
    references: int
    microbes: int
    products_with_ingredients: int
    products_with_substrate: int
    uses: int
    by_category: dict[str, int]
    by_continent: dict[str, int]
    by_source: dict[str, int]


class SeasonalIngredientOut(BaseModel):
    name: str
    count: int


class SeasonalMonthName(BaseModel):
    es: str
    en: str


class SeasonalOut(BaseModel):
    month: int
    month_name: SeasonalMonthName
    total: int
    ingredients: list[SeasonalIngredientOut] = []
    products: list[ProductListItem] = []


class TimelineText(BaseModel):
    es: str
    en: str


class TimelineEventOut(BaseModel):
    year: int
    era: str
    title: TimelineText
    description: TimelineText
    category: str
    region: str | None = None


class TimelineOut(BaseModel):
    total: int
    events: list[TimelineEventOut]
