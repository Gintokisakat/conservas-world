from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    String,
    Table,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base

product_country = Table(
    "product_country",
    Base.metadata,
    Column("product_id", ForeignKey("products.id", ondelete="CASCADE"), primary_key=True),
    Column("country_id", ForeignKey("countries.id", ondelete="CASCADE"), primary_key=True),
    Column("role", String(20), default="origin"),
)

product_ingredient = Table(
    "product_ingredient",
    Base.metadata,
    Column("product_id", ForeignKey("products.id", ondelete="CASCADE"), primary_key=True),
    Column("ingredient_id", ForeignKey("ingredients.id", ondelete="CASCADE"), primary_key=True),
    Column("percent", Float, nullable=True),
)

product_category = Table(
    "product_category",
    Base.metadata,
    Column("product_id", ForeignKey("products.id", ondelete="CASCADE"), primary_key=True),
    Column("category_id", ForeignKey("categories.id", ondelete="CASCADE"), primary_key=True),
)

product_microbe = Table(
    "product_microbe",
    Base.metadata,
    Column("product_id", ForeignKey("products.id", ondelete="CASCADE"), primary_key=True),
    Column("microbe_id", ForeignKey("microbes.id", ondelete="CASCADE"), primary_key=True),
)

product_reference = Table(
    "product_reference",
    Base.metadata,
    Column("product_id", ForeignKey("products.id", ondelete="CASCADE"), primary_key=True),
    Column("reference_id", ForeignKey("references.id", ondelete="CASCADE"), primary_key=True),
)


class ProductUse(Base):
    """El producto `product` usa al producto `used_product` como ingrediente."""

    __tablename__ = "product_uses"
    __table_args__ = (UniqueConstraint("product_id", "used_product_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE"), index=True
    )
    used_product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE"), index=True
    )

    product: Mapped["Product"] = relationship(
        foreign_keys=[product_id], back_populates="uses"
    )
    used_product: Mapped["Product"] = relationship(
        foreign_keys=[used_product_id], back_populates="used_by"
    )


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    description: Mapped[str | None] = mapped_column(Text)
    method: Mapped[str | None] = mapped_column(Text)
    fermentation_time: Mapped[str | None] = mapped_column(String(100))
    storage_life: Mapped[str | None] = mapped_column(String(150))
    status: Mapped[str] = mapped_column(String(20), default="imported")
    source_tag: Mapped[str | None] = mapped_column(String(50), index=True)
    substrate: Mapped[str | None] = mapped_column(String(150), index=True)
    image_url: Mapped[str | None] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    aliases: Mapped[list["ProductAlias"]] = relationship(
        back_populates="product", cascade="all, delete-orphan"
    )
    countries: Mapped[list["Country"]] = relationship(
        secondary=product_country, back_populates="products"
    )
    ingredients: Mapped[list["Ingredient"]] = relationship(
        secondary=product_ingredient, back_populates="products"
    )
    categories: Mapped[list["Category"]] = relationship(
        secondary=product_category, back_populates="products"
    )
    microbes: Mapped[list["Microbe"]] = relationship(
        secondary=product_microbe, back_populates="products"
    )
    references: Mapped[list["Reference"]] = relationship(
        secondary=product_reference, back_populates="products"
    )
    uses: Mapped[list["ProductUse"]] = relationship(
        back_populates="product", cascade="all, delete-orphan", foreign_keys="ProductUse.product_id"
    )
    used_by: Mapped[list["ProductUse"]] = relationship(
        back_populates="used_product", foreign_keys="ProductUse.used_product_id"
    )
    dairy: Mapped["DairyFerment | None"] = relationship(
        back_populates="product", cascade="all, delete-orphan"
    )
    metagenome: Mapped["CheeseMetagenome | None"] = relationship(
        back_populates="product", cascade="all, delete-orphan"
    )
    reviews: Mapped[list["Review"]] = relationship(
        back_populates="product", cascade="all, delete-orphan"
    )


class ProductAlias(Base):
    __tablename__ = "product_aliases"
    __table_args__ = (UniqueConstraint("product_id", "name", "language"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(255))
    language: Mapped[str | None] = mapped_column(String(10))

    product: Mapped["Product"] = relationship(back_populates="aliases")


class Country(Base):
    __tablename__ = "countries"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    iso2: Mapped[str | None] = mapped_column(String(2))
    iso3: Mapped[str | None] = mapped_column(String(3))
    continent: Mapped[str | None] = mapped_column(String(50), index=True)
    latitude: Mapped[float | None] = mapped_column(Float)
    longitude: Mapped[float | None] = mapped_column(Float)

    products: Mapped[list["Product"]] = relationship(
        secondary=product_country, back_populates="countries"
    )


class Ingredient(Base):
    __tablename__ = "ingredients"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(150), unique=True, index=True)
    category: Mapped[str | None] = mapped_column(String(50), index=True)

    products: Mapped[list["Product"]] = relationship(
        secondary=product_ingredient, back_populates="ingredients"
    )
    nutrition: Mapped["NutritionData | None"] = relationship(
        back_populates="ingredient", cascade="all, delete-orphan"
    )


class NutritionData(Base):
    """Valores por 100 g tomados de la USDA FoodData Central (fdcId)."""

    __tablename__ = "nutrition_data"

    id: Mapped[int] = mapped_column(primary_key=True)
    ingredient_id: Mapped[int] = mapped_column(
        ForeignKey("ingredients.id", ondelete="CASCADE"),
        unique=True,
        index=True,
    )
    fdc_id: Mapped[str] = mapped_column(String(30))
    calories: Mapped[float | None] = mapped_column(Float)
    protein_g: Mapped[float | None] = mapped_column(Float)
    fat_g: Mapped[float | None] = mapped_column(Float)
    carbs_g: Mapped[float | None] = mapped_column(Float)
    fiber_g: Mapped[float | None] = mapped_column(Float)
    sodium_mg: Mapped[float | None] = mapped_column(Float)
    potassium_mg: Mapped[float | None] = mapped_column(Float)
    vitamin_c_mg: Mapped[float | None] = mapped_column(Float)
    iron_mg: Mapped[float | None] = mapped_column(Float)
    calcium_mg: Mapped[float | None] = mapped_column(Float)
    zinc_mg: Mapped[float | None] = mapped_column(Float)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    ingredient: Mapped["Ingredient"] = relationship(back_populates="nutrition")


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(60), unique=True)
    name: Mapped[str] = mapped_column(String(150))
    description: Mapped[str | None] = mapped_column(Text)

    products: Mapped[list["Product"]] = relationship(
        secondary=product_category, back_populates="categories"
    )


class Microbe(Base):
    __tablename__ = "microbes"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(150), unique=True)

    products: Mapped[list["Product"]] = relationship(
        secondary=product_microbe, back_populates="microbes"
    )


class Reference(Base):
    __tablename__ = "references"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(500))
    ref_type: Mapped[str | None] = mapped_column(String(50))
    url: Mapped[str | None] = mapped_column(String(500))
    doi: Mapped[str | None] = mapped_column(String(200))

    products: Mapped[list["Product"]] = relationship(
        secondary=product_reference, back_populates="references"
    )


class GlossaryTerm(Base):
    """Término de fermentación/conservación con su definición (bilingüe)."""

    __tablename__ = "glossary"
    __table_args__ = (UniqueConstraint("term", "language"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    term: Mapped[str] = mapped_column(String(150), index=True)
    definition: Mapped[str] = mapped_column(Text)
    language: Mapped[str] = mapped_column(String(10), default="es", index=True)
    related_product_id: Mapped[int | None] = mapped_column(
        ForeignKey("products.id", ondelete="SET NULL"), index=True, nullable=True
    )

    related_product: Mapped["Product | None"] = relationship()


class DairyFerment(Base):
    """Metadatos de lácteo fermentado tradicional según FDF-DB (roadmap 2.13)."""

    __tablename__ = "dairy_ferments"

    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE"), unique=True, index=True
    )
    name: Mapped[str] = mapped_column(String(255))
    classification: Mapped[str | None] = mapped_column(String(50))
    country: Mapped[str | None] = mapped_column(String(255))
    region: Mapped[str | None] = mapped_column(String(255))
    milk_type: Mapped[str | None] = mapped_column(String(150))
    treatment: Mapped[str | None] = mapped_column(String(150))
    ripening: Mapped[str | None] = mapped_column(String(255))
    microbiota_json: Mapped[str | None] = mapped_column(Text)
    geographical_indication: Mapped[bool] = mapped_column(Boolean, default=False)
    characteristics: Mapped[str | None] = mapped_column(Text)

    product: Mapped["Product"] = relationship(back_populates="dairy")


class CheeseMetagenome(Base):
    """Subtipos de queso con metagenomas asociados según MetaCheeseDB (roadmap 2.13).

    Almacena por producto el subtipo de queso de MetaCheeseDB y los taxones
    característicos derivados de sus metagenomas (abundancia media y prevalencia).
    """

    __tablename__ = "cheese_metagenomes"

    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE"), unique=True, index=True
    )
    subtype: Mapped[str] = mapped_column(String(255))
    sample_count: Mapped[int] = mapped_column(default=0)
    taxa_json: Mapped[str | None] = mapped_column(Text)
    url: Mapped[str | None] = mapped_column(String(500))

    product: Mapped["Product"] = relationship(back_populates="metagenome")


class User(Base):
    """Usuario registrado (roadmap 4.1)."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    username: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(300))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    preferences_json: Mapped[str | None] = mapped_column(Text)

    reviews: Mapped[list["Review"]] = relationship(back_populates="user")
    recipes: Mapped[list["Recipe"]] = relationship(back_populates="user")
    batches: Mapped[list["Batch"]] = relationship(back_populates="user")


class Batch(Base):
    """Frasco/fermento en seguimiento del usuario (roadmap 3.1)."""

    __tablename__ = "batches"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    name: Mapped[str] = mapped_column(String(200))
    substrate: Mapped[str | None] = mapped_column(String(120))
    method: Mapped[str | None] = mapped_column(String(40))
    start_date: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    target_days: Mapped[int] = mapped_column(default=7)
    temp_c: Mapped[float | None] = mapped_column(Float)
    ph: Mapped[float | None] = mapped_column(Float)
    notes: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), default="active")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime | None] = mapped_column(DateTime, onupdate=func.now())

    user: Mapped["User"] = relationship(back_populates="batches")


class Review(Base):
    """Reseña de un producto por un usuario (roadmap 4.2)."""

    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE"), index=True
    )
    rating: Mapped[int] = mapped_column()
    text: Mapped[str | None] = mapped_column(Text)
    flagged: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime | None] = mapped_column(DateTime, onupdate=func.now())

    __table_args__ = (UniqueConstraint("user_id", "product_id", name="uq_review_user_product"),)

    user: Mapped["User"] = relationship(back_populates="reviews")
    product: Mapped["Product"] = relationship(back_populates="reviews")


class Recipe(Base):
    """Receta comunitaria vinculada a un producto (roadmap 4.3)."""

    __tablename__ = "recipes"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    product_id: Mapped[int | None] = mapped_column(
        ForeignKey("products.id", ondelete="SET NULL"), index=True
    )
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str | None] = mapped_column(Text)
    steps_json: Mapped[str | None] = mapped_column(Text)
    ingredients_json: Mapped[str | None] = mapped_column(Text)
    difficulty: Mapped[str] = mapped_column(String(20), default="media")
    prep_time_min: Mapped[int | None] = mapped_column()
    votes: Mapped[int] = mapped_column(default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="recipes")


class RecipeVote(Base):
    """Voto positivo único por usuario en una receta comunitaria."""

    __tablename__ = "recipe_votes"

    recipe_id: Mapped[int] = mapped_column(
        ForeignKey("recipes.id", ondelete="CASCADE"), primary_key=True
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )


class FlavorMolecule(Base):
    """Molécula de sabor de FlavorDB asociada a ingredientes."""

    __tablename__ = "flavor_molecules"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    pubchem_id: Mapped[int | None] = mapped_column(index=True)


class IngredientFlavorMolecule(Base):
    """Asociación ingrediente <-> molécula de sabor (FlavorDB)."""

    __tablename__ = "ingredient_flavor_molecules"

    ingredient_id: Mapped[int] = mapped_column(
        ForeignKey("ingredients.id", ondelete="CASCADE"), primary_key=True
    )
    molecule_id: Mapped[int] = mapped_column(
        ForeignKey("flavor_molecules.id", ondelete="CASCADE"), primary_key=True
    )
