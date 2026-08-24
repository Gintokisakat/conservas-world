# API pública — Conservas del Mundo

API REST de solo lectura sobre el catálogo de conservas, fermentos y encurtidos tradicionales.

- **Base URL local**: `http://localhost:8000`
- **API versionada**: `http://localhost:8000/api/v1` (mismo contrato que la raíz)
- **Documentación interactiva (OpenAPI/Swagger)**: `/docs`
- **Landing de la API**: `/api`
- **Healthcheck**: `/api/health`
- **Rate limit**: 120 peticiones/minuto por IP. Cada respuesta incluye `X-RateLimit-Limit`, `X-RateLimit-Remaining` y `X-RateLimit-Reset`. Al superarlo se responde `429`.

Todos los endpoints devuelven JSON (UTF-8). Los parámetros `lang` aceptan `es` (por defecto) o `en`.

---

## Productos

### `GET /products`
Lista paginada con filtros.

| Parámetro | Tipo | Descripción |
|---|---|---|
| `q` | str | Búsqueda full-text (FTS5) por nombre/descripción |
| `category` | str | Código de categoría (`fermento_lactico`, `encurtido_fermentado`, …) |
| `country` | str | Nombre o código ISO del país |
| `continent` | str | Continente |
| `ingredient` | str | Ingrediente canónico |
| `source` | str | Fuente (`fermdb`, `wikipedia`, `openfoodfacts`, `wikidata`, `ark_of_taste`, `fdfdb`) |
| `diet` | str | Etiqueta de dieta (`vegetarian`, `vegan`, `gluten_free`, …) |
| `fermentation_time` | str | Rango de tiempo de fermentación |
| `gi` | bool | Solo con indicación geográfica |
| `page`, `page_size` | int | Paginación |

```bash
curl "http://localhost:8000/api/v1/products?q=kimchi&continent=Asia&page_size=2"
```

### `GET /products/{id}`
Detalle completo: alias bilingües, países, ingredientes, categorías, microbios, referencias, sustrato, usos, imagen y lácteo asociado si existe.

### `GET /products/random`
Producto aleatorio activo.

### `GET /products/dairy`
Productos lácteos fermentados (de FDF-DB), con clasificación e indicación geográfica.

### `GET /products/geo`
Puntos geográficos para mapas: `{id, name, lat, lng, country, continent, category, source_tag, substrate}`. Acepta los mismos filtros que `/products`.

### `GET /products/{id}/related`
Relacionados por categoría compartida.

### `GET /products/{id}/pairings`
Pairings de sabor por ingredientes compartidos.

### `GET /products/{id}/safety?lang=es`
Perfil de seguridad predictiva: riesgo, rango de pH, aw, sal %, temperatura de conservación, vida útil estimada y alertas según el tipo de fermento.

### `GET /products/{id}/etymology?lang=es`
Etimología del nombre cuando existe entrada curada (`null` si no).

### `GET /products/{id}/export`
Ficha completa del producto en JSON descargable.

---

## Búsqueda

### `GET /search/suggest?q=`
Sugerencias agrupadas: productos, categorías, países e ingredientes.

### `GET /search/semantic?q=&limit=10`
Búsqueda semántica ligera (TF-IDF + similitud coseno) sobre nombre, descripción, método e ingredientes. Devuelve hits con `score` de similitud.

```bash
curl "http://localhost:8000/api/v1/search/semantic?q=pasta%20de%20soja%20japonesa"
```

---

## Referencia

| Endpoint | Descripción |
|---|---|
| `GET /categories` | Taxonomía de 16 categorías |
| `GET /countries?continent=` | 147 países con coordenadas |
| `GET /ingredients?q=` | 203 ingredientes canónicos |
| `GET /microbes` | 41 microbios fermentadores |
| `GET /references` | Referencias bibliográficas |
| `GET /diets` | Etiquetas de dieta disponibles |
| `GET /seasonal?month=` | Fermentos por estacionalidad |
| `GET /glossary?q=` | Glosario (326 términos) |

## Ingredientes

| Endpoint | Descripción |
|---|---|
| `GET /ingredients/{id}/nutrition` | Información nutricional (fuente FDC) |
| `GET /ingredients/{id}/shelf-life?lang=` | Vida útil estilo FoodKeeper: días en nevera/congelador/despensa + notas |

---

## Herramientas

### `GET /recommendations?ingredients=repollo,zanahoria&products=kimchi`
Dado lo que tenés, devuelve:
- `make`: qué podés fermentar con tus ingredientes (por sustrato)
- `use`: qué podés preparar con tus fermentados (~4.900 vínculos de uso)

### `GET /timers/{product_id}?temp_c=21`
Tiempo estimado de fermentación ajustado por temperatura (modelo Q10, referencia 21 °C). Ejemplo: un fermento de 14 días a 18 °C se alarga ~1,3×.

### `GET /flavor-map?continent=&category=&detail=`
Perfil de sabor promedio por continente en 7 ejes (ácido, salado, dulce, umami, amargo, picante, fermentado) con desglose por producto.

### `GET /timeline`
Hitos históricos de la fermentación.

---

## Contenido educativo

### `GET /guides` · `GET /guides/{slug}?lang=`
Guías paso a paso curadas: kimchi, chucrut, kombucha, miso y yogur. Cada paso incluye duración, temperatura opcional y aviso de inocuidad.

### `GET /course` · `GET /course/{slug}?lang=`
Curso de fermentación en 5 módulos (historia, ciencia, tipos, seguridad, recetas) con lecciones y secciones bilingües.

### `GET /podcast?topic=&ferment=&lang=` · `GET /podcast/topics`
Índice de episodios reales de FermUp y Ferment Radio filtrable por tema (`ciencia`, `cultura`, `salud`, `recetas`, `arte`) y por fermento. Los episodios enlazan a sus fuentes originales.

### `GET /etymology/search?q=&lang=`
Búsqueda de etimologías curadas (kimchi, sauerkraut, garum, escabeche…).

---

## Estadísticas

### `GET /stats`
Totales globales, cobertura de ingredientes, vínculos de uso y distribuciones por categoría, continente y fuente.

---

## Errores

| Código | Significado |
|---|---|
| `404` | Recurso inexistente |
| `422` | Parámetro inválido (validación Pydantic) |
| `429` | Rate limit excedido — reintentar tras `X-RateLimit-Reset` |

Ejemplo de error:

```json
{ "detail": "Producto no encontrado" }
```

## Servidor MCP

Además de la HTTP API, el catálogo está disponible vía MCP (`mcp_server/`) para asistentes de IA, con herramientas de búsqueda, detalle, recomendaciones y temporizadores.
