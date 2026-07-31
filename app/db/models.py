from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
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


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    description: Mapped[str | None] = mapped_column(Text)
    method: Mapped[str | None] = mapped_column(Text)
    fermentation_time: Mapped[str | None] = mapped_column(String(100))
    status: Mapped[str] = mapped_column(String(20), default="imported")
    source_tag: Mapped[str | None] = mapped_column(String(50), index=True)
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
