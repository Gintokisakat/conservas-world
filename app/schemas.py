from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


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


class TimerOut(BaseModel):
    product_id: int
    product_name: str
    fermentation_time: str | None = None
    method: str | None = None
    storage_life: str | None = None
    temperature_c: float
    estimated_days: dict[str, int | None]
    model: str


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


class SemanticHit(BaseModel):
    product_id: int
    score: float
    name: str
    description: str | None = None
    image_url: str | None = None
    source_tag: str | None = None


class SemanticSearchOut(BaseModel):
    query: str
    hits: list[SemanticHit]


class GuideStepOut(BaseModel):
    number: int
    title: str
    body: str
    duration_min: int | None = None
    temp_c: int | None = None
    safety: bool = False


class GuideListItem(BaseModel):
    slug: str
    category: str
    title: str
    intro: str
    total_min: int
    difficulty: str
    steps: int


class GuideOut(BaseModel):
    slug: str
    category: str
    title: str
    intro: str
    total_min: int
    difficulty: str
    steps: list[GuideStepOut]


class SafetyOut(BaseModel):
    product_id: int
    name: str
    category: str
    risk: str
    ph_min: float
    ph_max: float
    ph_requirement: str
    aw_min: float
    aw_max: float
    salt_pct_min: float
    salt_pct_max: float
    storage_temp_c: str
    shelf_life_days: int
    alerts: list[str]


class EtymologyHit(BaseModel):
    term: str
    origin: str
    period: str


class EtymologySearchOut(BaseModel):
    query: str
    hits: list[EtymologyHit]


class EtymologyOut(BaseModel):
    term: str
    origin: str
    period: str
    text: str


class CourseSection(BaseModel):
    heading: str
    body: str
    bullets: list[str]


class CourseLesson(BaseModel):
    slug: str
    title: str
    duration_min: int
    sections: list[CourseSection]


class CourseModuleItem(BaseModel):
    slug: str
    title: str
    subtitle: str
    difficulty: int
    estimated_hours: int
    lesson_count: int


class CourseModuleDetail(CourseModuleItem):
    lessons: list[CourseLesson]


class PodcastEpisodeOut(BaseModel):
    id: str
    show: str
    number: int
    title: str
    topic: str
    ferments: list[str]
    duration_min: int | None
    summary: str
    url: str


class PodcastTopicOut(BaseModel):
    key: str
    label: str


class PodcastTopicsOut(BaseModel):
    topics: list[PodcastTopicOut]
    ferments: list[str]


class ShelfLifeOut(BaseModel):
    category: str
    fridge_days: int
    freezer_days: int | None
    pantry_days: int | None
    notes: str


class UserCreate(BaseModel):
    email: EmailStr
    username: str = Field(min_length=3, max_length=80, pattern=r"^[a-zA-Z0-9_.-]+$")
    password: str = Field(min_length=8, max_length=128)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


class UserOut(BaseModel):
    id: int
    email: str
    username: str
    created_at: datetime
    preferences: dict


class PreferencesUpdate(BaseModel):
    preferences: dict


class ReviewCreate(BaseModel):
    rating: int = Field(ge=1, le=5)
    text: str | None = Field(default=None, max_length=4000)


class ReviewUpdate(BaseModel):
    rating: int = Field(ge=1, le=5)
    text: str | None = Field(default=None, max_length=4000)


class ReviewAuthor(BaseModel):
    id: int
    username: str


class ReviewOut(BaseModel):
    id: int
    product_id: int
    rating: int
    text: str | None
    flagged: bool
    created_at: datetime
    updated_at: datetime | None
    mine: bool = False


class ReviewsOut(BaseModel):
    total: int
    average: float | None
    items: list[ReviewOut]


class RecipeCreate(BaseModel):
    title: str = Field(min_length=3, max_length=200)
    description: str | None = Field(default=None, max_length=4000)
    steps: list[str] = Field(default_factory=list)
    ingredients: list[str] = Field(default_factory=list)
    product_id: int | None = None
    difficulty: str = Field(default="media", pattern="^(facil|media|dificil)$")
    prep_time_min: int | None = Field(default=None, ge=1, le=10000)


class RecipeUpdate(RecipeCreate):
    pass


class RecipeAuthor(BaseModel):
    id: int
    username: str


class RecipeOut(BaseModel):
    id: int
    title: str
    description: str | None
    steps: list[str]
    ingredients: list[str]
    difficulty: str
    prep_time_min: int | None
    votes: int
    created_at: datetime
    author: RecipeAuthor
    product_id: int | None
    mine: bool = False
    voted: bool = False


class RecipesFeed(BaseModel):
    total: int
    items: list[RecipeOut]


class MoleculeOut(BaseModel):
    name: str
    pubchem_id: int | None


class IngredientMoleculesOut(BaseModel):
    ingredient_id: int
    ingredient_name: str
    total: int
    items: list[MoleculeOut]


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


class FlavorProfileOut(BaseModel):
    picante: float
    ácido: float
    umami: float
    dulce: float
    salado: float
    amargo: float
    fermentado: float


class FlavorProductOut(BaseModel):
    product_id: int
    name: str
    continent: str
    category: str | None
    profile: FlavorProfileOut


class FlavorContinentOut(BaseModel):
    continent: str
    products: int
    profile: FlavorProfileOut


class FlavorMapOut(BaseModel):
    axes: list[str]
    continents: list[FlavorContinentOut]
    detail: list[FlavorProductOut] = []


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


class BatchCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    substrate: str | None = Field(default=None, max_length=120)
    method: str | None = Field(default=None, max_length=40)
    start_date: datetime | None = None
    target_days: int = Field(default=7, ge=1, le=1000)
    temp_c: float | None = Field(default=None, ge=-20, le=80)
    ph: float | None = Field(default=None, ge=0, le=14)
    notes: str | None = Field(default=None, max_length=4000)
    status: str = Field(default="active", pattern="^(active|done|discarded)$")


class BatchUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    substrate: str | None = Field(default=None, max_length=120)
    method: str | None = Field(default=None, max_length=40)
    start_date: datetime | None = None
    target_days: int | None = Field(default=None, ge=1, le=1000)
    temp_c: float | None = Field(default=None, ge=-20, le=80)
    ph: float | None = Field(default=None, ge=0, le=14)
    notes: str | None = Field(default=None, max_length=4000)
    status: str | None = Field(default=None, pattern="^(active|done|discarded)$")


class BatchOut(BaseModel):
    id: int
    name: str
    substrate: str | None
    method: str | None
    start_date: datetime
    target_days: int
    temp_c: float | None
    ph: float | None
    notes: str | None
    status: str
    created_at: datetime
    updated_at: datetime | None


class BatchesOut(BaseModel):
    total: int
    items: list[BatchOut]
