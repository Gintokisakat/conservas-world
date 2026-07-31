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


class ProductOut(BaseModel):
    id: int
    name: str
    description: str | None
    method: str | None
    fermentation_time: str | None
    status: str
    source_tag: str | None
    aliases: list[AliasOut] = []
    countries: list[CountryOut] = []
    ingredients: list[IngredientOut] = []
    categories: list[CategoryOut] = []
    microbes: list[MicrobeOut] = []
    references: list[ReferenceOut] = []

    model_config = ConfigDict(from_attributes=True)


class ProductListItem(BaseModel):
    id: int
    name: str
    description: str | None
    source_tag: str | None
    categories: list[CategoryOut] = []
    countries: list[CountryOut] = []

    model_config = ConfigDict(from_attributes=True)


class PaginatedProducts(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[ProductListItem]


class Stats(BaseModel):
    products: int
    countries: int
    ingredients: int
    categories: int
    references: int
    microbes: int
    by_category: dict[str, int]
    by_continent: dict[str, int]
    by_source: dict[str, int]
