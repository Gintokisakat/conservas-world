# Roadmap: Conservas del Mundo

## Estado Actual

**Conservas del Mundo** es una plataforma de catálogo y descubrimiento de fermentos, encurtidos y conservas tradicionales del mundo.

### Stack actual
- **Backend**: Python 3.11+ / FastAPI / SQLAlchemy / SQLite (FTS5)
- **Frontend**: HTML/CSS/JS vanilla, i18n (ES/EN), PWA con service worker, Leaflet.js
- **Integración AI**: Servidor MCP (`app/mcp_server.py`) con 5 herramientas
- **Ingesta**: Pipeline automatizado desde 6 fuentes (FermDB, Wikipedia, Open Food Facts, Wikidata, FDF-DB, Curados Regionales)
- **Despliegue**: Docker + Render, GitHub Actions CI (pytest)
- **Tests**: 192 tests pasando al 100% (API, dietas, exportación, FDF-DB, geo, glosario, imágenes, ingredientes, MCP, metacheese, normalización, nutrición, pairings, sugerencias, timeline, vinagres, wikidata)

### Datos actuales
- **6,152 productos activos** (247 descartados por curaduría)
- **Vinagres caseros, fermentos acéticos y bebidas vivas ancestrales** (Tepache, Ginger Bug, Kvass, Hidromiel, Kéfir de Agua, Shio Koji)
- **193 ingredientes canónicos** con aliases multilingües (EN/ES/FR/DE/IT/PT/CZ/FI/TR/AR/JA)
- **133 países**, ~4,900 referencias, 99.98% cobertura de ingredientes
- **Imágenes de productos**: Pipeline automatizado multinivel (OFF → Wikimedia Commons → Wikidata)
- **1.166 lácteos FDF-DB** con Indicación Geográfica (GI/DOP/IGP) y 1.593 metagenomas MetaCheeseDB
- **16 categorías**: fermento_lactico (1,387), encurtido_fermentado (960), conserva_esterilizada (866), fermento_alcoholico (542), fermento_koji (519), conserva_azucar (449), encurtido_vinagre (372), fermento_acetico (234), encurtido_salmuera (155), ahumado (141), conserva_aceite (138), secado (117), curado_sal (68), fermento_mixto (44), fermento_alcalino (5), otros (28)

### Features actuales
- Búsqueda full-text (FTS5) con filtro por técnica/método (Lacto, Acética, Alcohólica, Koji, Encurtidos)
- Detalle de producto (alias, países, ingredientes, categorías, microbios, referencias, sustrato, usos, maridajes)
- "Mi Despensa": recomendaciones basadas en sustratos e ingredientes disponibles
- Temporizadores de fermentación (F1/F2) con lote y notificaciones
- Calculadora interactiva de salinidad y graduación alcohólica (% ABV)
- Asistente de diagnóstico de problemas (Kahm vs Moho, textura blanda, salmuera turbia, olor fétido)
- Servidor MCP (Model Context Protocol) para consulta automatizada por agentes de IA
- Cronología histórica de la fermentación (13.000 a.C. al presente)
- Enciclopedia de microbios fermentadores y glosario técnico
- Etiquetas imprimibles para frascos
- Panel de estadísticas e indicadores globales
- Manual del fermentador (esterilización, salinidad, textura, oxígeno, cultivo de madre de vinagre)
- Sistema de Favoritos y Generador de Lista de Compras
- Despliegue Docker + Render

---

## Proyectos Similares en el Ecosistema

### Bases de datos de fermentación
| Proyecto | URL | Qué tiene | Qué podemos integrar |
|---|---|---|---|
| **FermDB** (Bokulich Lab) | github.com/bokulich-lab/FermDB | 1,000+ fermentos tradicionales, dashboard interactivo | Ya lo usamos como fuente; podemos enriquecer con sus categorías |
| **cFMD** (SegataLab) | github.com/SegataLab/cFMD | 14,904 genomas microbianos, 3,444 metagenomas de alimentos | Asociar cepas microbianas específicas a cada producto |
| **FoodMicroDB** | github.com/yli085/FoodMicroDB | 6,358 datasets de amplicones, análisis de series temporales | Dinámica microbiana a lo largo del tiempo de fermentación |
| **ODFM** | odfm.wikim.re.kr | 197 genomas de bacterias/arqueas/eucariotas de alimentos fermentados | Búsqueda BLAST, análisis ANI |
| **Fermented Foods Microbial Genomes** | zenodo.org/records/15794524 | 13,850 genomas microbianos, 95% representativos a nivel de especie | Referencia genómica completa |
| **TEMPURA** | togodb.org/db/tempura | 8,639 cepas con temperaturas de crecimiento (min/ópt/max) | Datos de temperatura por cepa |
| **LDz-Base** | ldzbase.de | Valores D y z para microorganismos de alimentos | Parámetros de pasteurización/esterilización |
| **FDF-DB (Fermented Dairy Food DB)** | doi.org/10.3390/nu14214581 · quintadb.pro/dccTW7 | **1,852 lácteos fermentados tradicionales** con microbiota + país/región + tratamiento + maduración (CC BY 4.0) | **Cubre el gap de lácteos** (ver 2.13) |
| **MetaCheeseDB** | magliulo.github.io/metacheesedb | 1,593 metagenomas de queso, 156 subtipos, 19 países | Microbioma de queso por subtipo (extiende 2.2) |

### Datasets académicos y regionales
| Proyecto | URL | Qué tiene | Qué podemos integrar |
|---|---|---|---|
| **FoodAtlas** (UC Davis) | foodatlas.ai | Knowledge graph alimentos/químicos/enfermedades, API + descargas | Enriquecer productos con compuestos y efectos |
| **LanguaL** | langual.org/langual_indexed_datasets.asp | 40,000+ alimentos indexados, facetas de conservación/fermentación, 12,605 descriptores, 9 idiomas | Estandarizar categorías + términos multilingües |
| **Flavor Network dataset** (Ahn et al. 2011) | zenodo.org/records/11449658 | Grafo ingredientes–compuestos aromáticos (829KB, CC BY-NC-SA) | Pairing por compuestos (complementa FlavorDB 2.12) |
| **Traditional Animal Foods (Indigenous)** | traditionalanimalfoods.org | Enciclopedia open-access de especies en dietas indígenas de Norteamérica | Productos de origen animal tradicionales |
| **African foodways data** | github.com/ChicAfricanCulture/african-foodways-data | Recetas/ingredientes/prácticas africanas tradicionales (open access) | **Cubre gap de África** (ver 2.16) |
| **INFOODS Middle East tables** | fao.org/infoods/.../middle-east/en/ | Tablas de composición + fermentados tradicionales de Irán (Fars), Bahrain, Egipto | **Cubre gap de Medio Oriente** (ver 2.16) |
| **Nigerian fermented foods** | nature.com/articles/s41538-026-00844-1 | Inventario de 16 fermentados nigerianos (npj Science of Food) | Fermentos de Nigeria (ver 2.16) |
| **DBpedia fermented soy list** | dbpedia.org/page/List_of_fermented_soy_products | Lista estructurada de fermentados de soja por país (RDF/JSON) | Enriquecer categoría soja/Asia |
| **Advanced Multilingual FooDB** | github.com/yiliu-li/Advanced-Multilingual-FooDB-Food-Data | Traducciones multilingües + calorías sobre FooDB (CSV) | Aliases multilingües de ingredientes |

### Imágenes y contenido visual
| Proyecto | URL | Qué tiene | Qué podemos integrar |
|---|---|---|---|
| **Wikimedia Commons** | commons.wikimedia.org | Fotos de millones de alimentos, API gratuita, licencias libres | Fotos de productos en el detalle (mayor impacto visual, ~60% de productos tienen foto) |
| **Open Food Facts photos** | openfoodfacts.org | Fotos de productos ya en nuestra BD (ODbL) | Fotos del producto real con código de barras |
| **Wikipedia/Wikidata images** | wikidata.org | Imagen representativa por concepto alimentario | Miniaturas para cards y detalle |
| **FooDI-ML** (Glovo) | arxiv.org/abs/2110.02035 | 1.5M imágenes de productos + 9.5M nombres, 37 países, 33 idiomas (CC BY-NC-SA) | Imágenes + nombres multilingües de productos comerciales |

### APIs de recetas y datos complementarios
| Proyecto | URL | Qué tiene | Qué podemos integrar |
|---|---|---|---|
| **TheMealDB** | theMealDB.com | Recetas abiertas gratuitas, sin API key, imágenes + instrucciones | Recetas de platos fermentados |
| **open-recipe** (BBC Good Food) | github.com/dspray95/open-recipe | Scraper de ~100K+ recetas (Unlicense) | Corpus de recetas para guías/3.4 |
| **Fruityvice API** | fruityvice.com | Datos botánicos/nutricionales de frutas (gratis, sin key) | Datos de frutas usadas en fermentos |
| **FSIS FoodKeeper** | catalog.data.gov/dataset/fsis-foodkeeper-data | Guía oficial de almacenamiento/shelf-life (EN/ES/PT, JSON oficial USDA, actualizado 2025) | Shelf-life por alimento (complementa 2.3) |

### Seguridad alimentaria
| Proyecto | URL | Qué tiene | Qué podemos integrar |
|---|---|---|---|
| **ComBase** | portal.errc.ars.usda.gov/Combase.aspx | Curvas de crecimiento de patógenos por T/pH/aw | Predicción de crecimiento patógeno |
| **BCCDC Fermented Foods Guidance** | bccdc.ca | Mejores prácticas de seguridad para fermentados | Marco de cumplimiento de seguridad |
| **OpenFoodTox** (EFSA) | efsa.europa.eu | 73 contaminantes en 16 tipos de alimento | Referencia de seguridad química |
| **preserve-calc** | github.com/AdametherzLab/preserve-calc | Calculadora TypeScript: jarabe de azúcar, salmuera, vinagre, ajuste por altitud, compliance USDA | Librería npm para cálculos de preservación |

### Mapas geográficos de alimentos
| Proyecto | URL | Qué tiene | Qué podemos integrar |
|---|---|---|---|
| **TasteAtlas** | tasteatlas.com | 19,788+ platos/ingredientes en mapa interactivo, 10M+ usuarios/mes | Modelo de mapeo geográfico |
| **AnyCheese** | anycheese.com/map | Mapa interactivo de quesos del mundo | Modelo de clustering por país |
| **Open Wine Map** | openwinemap.com | Regiones vinícolas con GeoJSON (20 países europeos) | Datos de regiones vinícolas |
| **Open Brewery DB** | openbrewerydb.org | 11,745+ cervecerías, 23+ países, 14 tipos | API gratuita de cervecerías |
| **ViniGeo** | vinigeo.com | 1,600+ regiones vinícolas con boundaries oficiales | Datos geoespaciales de vino |
| **Foodscapes Report** (TNC) | nature.org | Mapa global de foodscape a 5km×5km resolución | Clasificación de paisajes alimentarios |

### Herencia cultural y tradiciones
| Proyecto | URL | Qué tiene | Qué podemos integrar |
|---|---|---|---|
| **UNESCO ICH** | ich.unesco.org | Kimjang (kimchi), Jang making (salsas fermentadas), Airag (leche de yegua fermentada), Attiéké (fermentación de yuca) | Contexto cultural patrimonial |
| **Slow Food Ark of Taste** | slowfood.com/ark-of-taste | 5,000+ alimentos en peligro de extinción | Clasificación de urgencia de preservación |
| **Thailand Fermented Foods DB** (JIRCAS) | jircas.go.jp | Fermentados tailandeses por materia prima, con fotos y microorganismos | Referencia del sudeste asiático |
| **UNESCO Food Atlas** | unesco.org | 50+ elementos de patrimonio alimentario en 16 países piloto | Modelo de patrimonio alimentario |

### Fermentation tracking (apps)
| Proyecto | URL | Qué tiene | Qué podemos integrar |
|---|---|---|---|
| **Ferment** (open source) | github.com/layogtima/ferment | 30 recetas, 23 artículos wiki, batch tracking, pantry, PWA | Datos de recetas JSON, base de equipos |
| **Fermi** (open source) | github.com/DerYeger/fermi | Nuxt + Tauri, gráficos, asistente IA (OpenRouter), recordatorios | Modelo de integración IA |
| **Fermenter** (open source) | github.com/AdametherzLab/fermenter | pH/gravity/temp/gas tracking, predicción de finalización por regresión lineal | Algoritmos de predicción |
| **Fermentor** | fermentor.org | Journal de experimentos, búsqueda semántica, branching de proyectos, comunidad | Modelo de conocimiento comunitario |
| **FermentBuddy** | fermentbuddy.app | 34+ síntomas de troubleshooting, timers ajustados por temperatura | Base de datos de troubleshooting |
| **BrineLog** | apps.apple.com | Motor de matemáticas de salmuera, gráficos logarítmicos de pH, generador de etiquetas | Cálculos de seguridad |
| **Larder** | apps.apple.com | Calculadora de enlatado con ajuste por altitud, tiempos USDA | Datos de procesamiento |
| **Fermentr** | fermentr.org | Recetas + fermentador, integración MCP/Claude, logs de lote | API de recetas, modelo de integración IA |
| **Puratos Sourdough Library** | sourdoughlibrary.com | 1,500+ masas madre vivas de 30+ países, datos de microbiota | Categoría "masa madre" con perfiles microbianos |
| **Periodic Table of Fermented Foods** (U Alberta) | food-sm.org/fermented | 50+ fermentos organizados tipo tabla periódica por sustrato/microbio | Modelo educativo y de visualización |
| **TakTak** | github.com/csabiu/TakTak | App Kotlin de makgeolli/fermentos coreanos: recetas, batches, notas de cata | Referencia de tracking coreano |
| **FermentOS** | github.com/highaltidude/FermentOS | Homebrewing self-hosted (ex-BrewPilot): recetas, sesiones, inventario; integra iSpindel | Modelo de inventario + integración hardware |
| **iot-sourdough-starter-monitor** | github.com/justinmklam/iot-sourdough-starter-monitor | Monitor de masa madre ESP8266 en la nube (95★) | Futuro: telemetría de masa madre |

### Comunidad y educación
| Proyecto | URL | Qué tiene | Qué podemos integrar |
|---|---|---|---|
| **Harvard Food Fermentation** | pll.harvard.edu | Curso gratuito: ciencia de fermentación, ejercicios prácticos | Estructura educativa |
| **Fermentor.org** | fermentor.org | Comunidad open source, knowledge base compartida | Modelo de comunidad |
| **r/fermentation** | reddit.com/r/fermentation | 15,000+ miembros, megathread semanal de seguridad | Patrones de FAQ |
| **Gutbasket Forum** | gutbasket.com | 6,400+ fermentadores, troubleshooting basado en fotos | Modelo de soporte comunitario |
| **Crock of Time Discord** | crockoftime.com/discord | Comunidad de koji, voz/video, gratuito | Comunidad niche |

### Otros datos útiles
| Proyecto | URL | Qué tiene | Qué podemos integrar |
|---|---|---|---|
| **GASTEREA** | euralex.org | Tesaurus diacrónico de palabras latinas de comida y su herencia en lenguas europeas | Etimología de nombres de fermentos |
| **etymology-db** | github.com/droher/etymology-db | 3.8M entradas etimológicas, 2,900 lenguas (de Wiktionary) | Origen de palabras alimentarias |
| **whatamieating.com** | whatamieating.pobmc.org.uk | 67,413 términos en 307 idiomas + 42,027 plurales | Diccionario alimentario internacional |
| **Seasonal Food Guide** | seasonalfoodguide.org | Calendario estacional por estado de EE.UU. | Qué fermentar según la temporada |
| **The Sifter** | thesifter.org | Miles de libros de cocina históricos (Medieval a presente), 100+ idiomas | Recetas históricas |
| **Flavor Genome Project** | flavorgenomeproject.com | 1B+ puntos de datos de sabores, 200,000 emparejamientos | Pairing de sabores |
| **FoodKG** | github.com/foodkg | Knowledge graph semántico, 67M triples RDF, endpoint SPARQL | Consultas de relaciones ingredientes-recetas |
| **FoodOn** | foodon.org | Ontología farm-to-fork, 9,600+ categorías, OBO Foundry | Estandarización de taxonomía |
| **FlavorDB** | flavordb.foodviz.org | 720 compuestos de sabor en 690 alimentos (descargable, open) | Pairing granular por compuestos químicos (mejora 3.3) |

---

## Roadmap por Fases

### FASE 1 — Quick Wins (1-2 días cada uno)

#### 1.1 Nutrición USDA FoodData Central
- **Fuente**: https://fdc.nal.usda.gov/ (API REST gratuita, datos CC0)
- **Qué hacer**:
  - Nuevo archivo `ingest/sources/usda.py` que consulta la API de FoodData Central
  - Buscar cada ingrediente canónico por nombre, obtener FDC ID
  - Almacenar en tabla `nutrition_data` (fdc_id, calories, protein_g, fat_g, carbs_g, fiber_g, sodium_mg, potassium_mg, vitamin_c_mg, iron_mg, calcium_mg, zinc_mg)
  - Endpoint `GET /ingredients/{id}/nutrition` en la API
  - Mostrar info nutricional en el detalle de ingredientes del frontend
- **Dependencias**: Ninguna nueva (httpx ya está en el proyecto)
- **Riesgo**: Rate limits de USDA (1,000 req/h sin API key, 120,000 con key gratis)

#### 1.2 ruff + mypy + CI lint
- **Qué hacer**:
  - Agregar `ruff` y `mypy` a `pyproject.toml` y al grupo dev
  - Crear configuración básica en `pyproject.toml`
  - Agregar step de linting en `.github/workflows/ci.yml`
  - Corregir errores encontrados
- **Dependencias**: ruff, mypy (dev)
- **Riesgo**: Puede requerir correcciones menores en el código existente

#### 1.3 Dark mode
- **Qué hacer**:
  - Agregar variables CSS `--bg-page-dark`, `--bg-card-dark`, etc. en `style.css`
  - Crear clase `.dark` en `<html>` que active las variables oscuras
  - Agregar toggle en el header (ícono de luna/sol)
  - Guardar preferencia en localStorage
  - Respeta `prefers-color-scheme` del SO
- **Dependencias**: Ninguna
- **Riesgo**: Ninguno

#### 1.4 Autocomplete de búsqueda
- **Qué hacer**:
  - Agregar endpoint `GET /search/suggest?q=...` que retorne top 10 matches de nombres de productos + ingredientes
  - Reemplazar el `<datalist>` actual con un componente autocomplete custom (o Fuse.js ligero)
  - Mostrar: nombre del producto, categoría, país
- **Dependencias**: Ninguna (o fuse.js ~7KB minified)
- **Riesgo**: Bajo

#### 1.5 Calendario estacional
- **Qué hacer**:
  - Nuevo archivo `data/seasonal.json` con meses de disponibilidad por ingrediente canónico
  - Nuevo endpoint `GET /seasonal?month=...&continent=...`
  - Nuevo componente en el frontend: "Qué fermentar este mes"
  - Inspiración: seasonalfoodguide.org, EU seasonal calendar
- **Dependencias**: Ninguna
- **Riesgo**: Requiere investigación de disponibilidad estacional por región

#### 1.6 Exportar receta a PDF/CSV
- **Qué hacer**:
  - Endpoint `GET /products/{id}/export?format=pdf|csv`
  - PDF: usar weasyprint o generar HTML imprimible
  - CSV: ingredientes, pasos, referencias
  - Botón "Exportar" en el modal de detalle del producto
- **Dependencias**: weasyprint (opcional) o solo HTML/CSS print
- **Riesgo**: Bajo

#### 1.7 Etiquetas de dieta/alérgenos
- **Qué hacer**:
  - Derivar automáticamente de los 193 ingredientes canónicos: vegan, vegetariano, sin gluten, sin lácteos, sin soja, picante, halal, kosher
  - Tabla `diet_tags` (ingredient_id, tag, confidence) + mapeo producto→tags vía ingredientes
  - Filtro en la búsqueda: "Mostrar solo productos veganos/sin gluten"
  - Badge en cards y detalle de producto
- **Dependencias**: Ninguna (mismo pipeline que nutrition)
- **Riesgo**: Bajo; los ingredientes son el dato más confiable para derivar etiquetas
- **Valor alto**: es lo que los usuarios preguntan primero ("¿es vegano el kimchi?") y mejora el SEO

#### 1.8 Glosario de términos de fermentación
- **Fuente**: whatamieating.com (67,413 términos), Wiktionary, propio
- **Qué hacer**:
  - Tabla `glossary` (term, definition, language, related_product_id)
  - 200-300 términos esenciales primero: "kahm yeast", "brine", "koji", "tibicos", "canning"
  - Endpoint `GET /glossary`, autocompletado en búsqueda
  - Links desde detalle de producto ("¿Qué es un fermento láctico?")
- **Dependencias**: Ninguna
- **Riesgo**: Bajo; mejora SEO y accesibilidad para principiantes

---

### FASE 2 — Data Integrations (2-5 días cada uno)

#### 2.1 Mapa geográfico interactivo [✅ COMPLETADO]
- **Inspiración**: TasteAtlas, AnyCheese, Open Wine Map, FermDB Dashboard
- **Qué hacer**:
  - Integrar Leaflet.js + OpenStreetMap (gratis, sin API key)
  - Nuevo endpoint `GET /products/geo` que retorne `{lat, lng, name, id, category}` por país
  - Usar `pycountry` para obtener coordenadas centroides de cada país
  - Clustering de productos (Leaflet.markercluster)
  - Click en marcador → popup con nombre + categorías + link al detalle
  - Filtros: por categoría, continente, fuente
  - Opción de vista de mapa completo vs. lista
- **Dependencias**: Leaflet.js (CDN), leaflet.markercluster (CDN)
- **Riesgo**: Coordenadas centroides son aproximadas; idealmente usar polígonos de países

#### 2.2 Microbioma profundo
- **Fuentes**: cFMD (14,904 MAGs), FoodMicroDB (6,358 amplicones), ODFM (197 genomas), TEMPURA (8,639 cepas con temperaturas)
- **Qué hacer**:
  - Crear tabla `microbe_strains` (microbe_id, strain_name, species, genus, food_source, temperature_min, temperature_opt, temperature_max, genome_accession)
  - Poblar desde descargas de cFMD/ODFM (datasets en Zenodo)
  - Nuevo endpoint `GET /microbes/{id}/strains` con info de cepas
  - En el detalle de producto: mostrar cepas específicas asociadas, rangos de temperatura óptimos
  - Vincular con TEMPURA para datos de crecimiento
- **Dependencias**: pandas (ya está), posiblemente biopython para parsing de genomas
- **Riesgo**: Los datos de cFMD están en formato académico (BIOM/TSV), requiere parsing significativo

#### 2.3 pH/seguridad predictiva [✅ COMPLETADO]
- **Fuentes**: ComBase (curvas de crecimiento), BCCDC guidance, pickling pH calculators, preserve-calc
- **Qué hacer**:
  - Tabla `safety_data` (product_id, ph_min, ph_max, aw_min, aw_max, salt_pct_min, salt_pct_max, storage_temp_min, storage_temp_max, shelf_life_days)
  - Poblar con datos de literatura + ComBase para los 16 tipos de fermento
  - Endpoint `GET /products/{id}/safety`
  - Frontend: badge de seguridad con pH/aw/temperatura
  - Calculadora de pH de salmuera mejorada (usando datos de preserve-calc)
  - Alertas: "Este fermento requiere pH < 4.6 para inocuidad"
- **Dependencias**: Ninguna nueva
- **Riesgo**: Los datos de ComBase requieren consulta manual o scraping

#### 2.4 Péptidos bioactivos
- **Fuente**: FermFooDb (2,205 péptidos, 1,032 secuencias únicas)
- **Qué hacer**:
  - Tabla `bioactive_peptides` (product_id, peptide_sequence, activity_type, food_matrix, reference)
  - Descargar dataset de GitHub (FermFooDb)
  - Matching por nombre de alimento canónico
  - Endpoint `GET /products/{id}/peptides`
  - Frontend: sección "Beneficios para la salud" en detalle de producto
- **Dependencias**: Ninguna
- **Riesgo**: FermFooDb tiene licencia CC BY-NC-ND 4.0 (requiere atribución, no comercial)

#### 2.5 Ontología FoodOn
- **Fuente**: foodon.org (9,600+ categorías, OBO Foundry)
- **Qué hacer**:
  - Mapear nuestras 16 categorías internas a IDs de FoodOn
  - Agregar columna `foodon_id` a la tabla `categories`
  - Endpoint `GET /categories` incluye `foodon_id` para interoperabilidad
  - Futuro: consultas SPARQL contra knowledge graphs de alimentos
- **Dependencias**: Ninguna
- **Riesgo**: Mapeo manual inicial requerido

#### 2.6 Slow Food Ark of Taste [✅ COMPLETADO]
- **Fuente**: slowfood.com/ark-of-taste
- **Implementado**: Ingesta curada de conservas y fermentos patrimoniales tradicionales + insignia distintiva `🏛️ Arca del Gusto` y filtro por fuente en la interfaz.

#### 2.7 Open Brewery DB
- **Fuente**: openbrewerydb.org (11,745+ cervecerías, API gratuita)
- **Qué hacer**:
  - Endpoint `GET /breweries?country=...&lat=...&lng=...` que consulte la API
  - Mostrar cervecerías cercanas en el mapa geográfico
  - Vincular con productos de categorías de cerveza
- **Dependencias**: Ninguna
- **Riesgo**: Ninguno (API gratuita)

#### 2.8 Open Wine Map
- **Fuente**: github.com/devloed-com/open-wine-map (GeoJSON de regiones vinícolas)
- **Qué hacer**:
  - Descargar GeoJSON de regiones vinícolas europeas
  - Overlay en el mapa Leaflet
  - Click en región → productos de esa zona
- **Dependencias**: Ninguna
- **Riesgo**: Datos solo de Europa; faltan Americas/Asia/África

#### 2.9 Etimología de alimentos [✅ COMPLETADO]
- **Fuentes**: GASTEREA (latín), etymology-db (3.8M entradas), whatamieating.com (67,413 términos)
- **Qué hacer**:
  - Tabla `etymology` (ingredient_id, term, language, origin, period, notes)
  - Poblar desde etymology-db (dataset abierto en GitHub)
  - Mostrar origen etimológico en el detalle de ingredientes
  - "Did you know?" section: "La palabra 'sauerkraut' viene del alemán 'sauer' (ácido) + 'Kraut' (repollo)"
- **Dependencias**: Ninguna
- **Riesgo**: etymology-db es un dataset grande (~500MB), requiere filtrado por alimentos

#### 2.10 Timeline histórico de fermentación [✅ COMPLETADO]
- **Fuentes**: Linda Hall Library, PMC, Wikipedia
- **Implementado**: 25 hitos globales desde 13.000 a.C. con endpoint `/timeline` y sección bilingüe en frontend.

#### 2.11 Imágenes de productos [✅ COMPLETADO]
- **Fuentes**: Wikimedia Commons (API), Open Food Facts, Wikipedia, Wikidata
- **Implementado**: Pipeline automatizado `ingest/images.py` con miniatura visual en API, cards y exportación.

#### 2.12 Pairing granular con FlavorDB
- **Fuente**: FlavorDB (720 compuestos de sabor, 690 alimentos, descargable)
- **Qué hacer**:
  - Descargar dataset de flavor compounds por ingrediente
  - Tabla `flavor_compounds` (ingredient_id, compound, concentration, fooddb_id)
  - Mejorar el modelo de similitud de 3.3: no solo Jaccard de ingredientes, sino compuestos compartidos
  - Endpoint `GET /ingredients/{id}/compounds`
- **Dependencias**: Ninguna (CSV open)
- **Riesgo**: Matching ingredientes canónicos ↔ FlavorDB requiere curar ~193 mapeos

#### 2.13 Lácteos fermentados (FDF-DB + MetaCheeseDB) — gap de categoría [✅ COMPLETADO]
- **Fuentes**: FDF-DB (1,852 lácteos fermentados, CC BY 4.0), MetaCheeseDB (1,593 metagenomas de queso)
- **Qué hacer**:
  - Descargar suplemento ZIP de FDF-DB (doi.org/10.3390/nu14214581)
  - Tabla `dairy_ferments` (name, country, region, milk_type, treatment, ripening, microbiota_json, geographical_indication)
  - Matching con nuestros productos lácteos existentes; añadir los nuevos
  - Enriquecer con MetaCheeseDB: subtipos de queso con metagenomas asociados (para 2.2)
  - Badge "Indicación geográfica" (Parmigiano Reggiano, Roquefort, etc.)
- **Dependencias**: Ninguna
- **Riesgo**: El DB vivo (quintadb.pro) requiere login (FDF-DB/intimic); usar el ZIP del suplemento en su lugar

#### 2.14 Gap regional: África y Medio Oriente [✅ COMPLETADO]
- **Fuentes**: African foodways data (GitHub, open), INFOODS Middle East (Irán Fars, Bahrain, Egipto), Nigerian fermented foods (npj, 16 fermentados)
- **Qué hacer**:
  - Revisar nuestra cobertura actual por continente y listar huecos en África/MO
  - Importar fermentos africanos (ogi, injera, iru/dawa-dawa, ogiri, mbuja, ting) y de Oriente Medio (kashk, jameed, torshi, dibis, murtol)
  - Tabla `regional_sources` (source, region, coverage_count)
  - Dashboard de cobertura: "X de Y países africanos representados"
- **Dependencias**: Ninguna
- **Riesgo**: Bajo; requiere validación manual de nombres locales

#### 2.15 Shelf-life con FSIS FoodKeeper [✅ COMPLETADO]
- **Fuente**: catalog.data.gov/dataset/fsis-foodkeeper-data (JSON oficial USDA EN/ES/PT, actualizado 2025)
- **Qué hacer**:
  - Descargar JSON oficial (alternativa: repo jelera/food-shelflife-db ya lo parsea)
  - Tabla `shelf_life` (ingredient_id, food_category, storage_method, fridge_days, freezer_days, pantry_days)
  - Endpoint `GET /ingredients/{id}/shelf-life`
  - Frontend: "Cuánto dura en nevera/congelador" en detalle de ingrediente
- **Dependencias**: Ninguna
- **Riesgo**: El URL directo de USDA está tras Akamai (403); usar data.gov o el dump del repo de terceros

#### 2.16 LanguaL: faceta de fermentación y multilingüe
- **Fuente**: langual.org (40,000+ alimentos indexados, 9 idiomas, facetas de conservación)
- **Qué hacer**:
  - Usar las facetas de LanguaL para "método de conservación: fermentado" como vocabulario controlado
  - Mapear nuestras 16 categorías internas a códigos LanguaL (además de FoodOn en 2.5)
  - Extraer términos multilingües de ingredientes para enriquecer aliases (extiende 1.8/4.8)
- **Dependencias**: Ninguna
- **Riesgo**: Datasets grandes; descargar solo las facetas de fermentación/conservación

---

### FASE 3 — Features de Producto (1-2 semanas)

#### 3.1 Batch tracking server-side [✅ COMPLETADO]
- **Inspiración**: Fermentor, Fermenta, FermentBuddy, BrineLog
- **Hecho**:
  - Tabla `batches` (id, user_id, name, substrate, method, start_date, target_days, temp_c, ph, notes, status, created_at, updated_at)
  - Tabla `batch_checkpoints` (batch_id, day, temp_c, ph, notes, created_at)
  - Endpoints REST: `GET/POST/PUT/DELETE /me/batches` y `GET/POST /me/batches/{id}/checkpoints` (registro diario), todos protegidos por usuario
  - Frontend: al iniciar sesión, los "Mis Fermentos" (antes solo en localStorage) se sincronizan con la cuenta y persisten entre dispositivos; modo invitado mantiene el almacenamiento local offline
  - Botón "✓ Marcar listo" en frascos que completan su tiempo (cambia status → done en la cuenta) + contador de activos + aviso "☁️ sincronizado con tu cuenta"
  - Registro diario: modal "📓" por frasco con tabla por día (timeline) y formulario para añadir pH/temperatura/notas
  - Tests de CRUD, checkpoints, aislamiento entre usuarios y validación
- **Pendiente futura**: subida de fotos en los checkpoints

#### 3.2 Calculadoras avanzadas [✅ COMPLETADO]
- **Inspiración**: preserve-calc, BrineLog, Larder, Curing Calculator
- **Qué hacer**:
  - **Calculadora de pH de salmuera**: dado el pH de cada ingrediente, calcular pH resultante de la mezcla
  - **Ajuste por altitud**: tiempos de procesamiento ajustados a altitud del usuario
  - **Calculadora de curado**: sal/azúcar/nitrito para carnes, tiempo estimado
  - **Conversor de salinidad**: % ↔ g/L ↔ oz/gal
  - **Calculadora de vinagre**: ratio vinagre/agua para diferentes vegetales
  - Nuevo endpoint `POST /calculators/pH`, `POST /calculators/altitude`, etc.
- **Dependencias**: Ninguna
- **Riesgo**: Cálculos requieren validación científica

#### 3.3 Pairing de sabores [✅ COMPLETADO]
- **Inspiración**: Flavor Genome Project (1B+ puntos de datos)
- **Qué hacer**:
  - Modelo de similitud basado en ingredientes canónicos compartidos
  - Dado un producto, calcular similitud con todos los demás (Jaccard o coseno)
  - Sugerir complementos: fermentos que comparten 1-2 ingredientes pero tienen contrastes
  - Endpoint `GET /products/{id}/pairings`
  - Frontend: "Combina bien con..." en detalle de producto
  - Futuro: usar FlavorDB para compoundes de sabor más granulares
- **Dependencias**: scikit-learn (opcional, para similitud de coseno) o cálculo manual
- **Riesgo**: Similitud basada solo en ingredientes es simplista; mejora con datos de FlavorDB

#### 3.4 Guías paso a paso interactivas [✅ COMPLETADO]
- **Inspiración**: Ferment (30 recetas), Fermenta, FermentBuddy
- **Qué hacer**:
  - Tabla `guides` (product_id, title, steps_json, tips_json, equipment_json, difficulty, total_time_hours)
  - Steps JSON: [{step: 1, title: "Preparar", description: "...", duration_hours: 0.5, image_url: "..."}]
  - Nuevo endpoint `GET /products/{id}/guide`
  - Frontend: wizard guiado paso a paso con checkboxes
  - Auto-iniciar temporizador al completar un paso
  - Dificultad: principiante/intermedio/avanzado
- **Dependencias**: Ninguna
- **Riesgo**: Requiere crear contenido para los 4,736 productos (empezar por los 50 más populares)

#### 3.5 Búsqueda semántica [✅ COMPLETADO]
- **Inspiración**: Fermentor.org
- **Qué hacer**:
  - Generar embeddings de texto para nombre + descripción de cada producto
  - Usar sentence-transformers (all-MiniLM-L6-v2, ~80MB)
  - Endpoint `GET /search/semantic?q=algo picante fermentado` → kimchi, gochujang, etc.
  - Indexar embeddings con FAISS o numpy cosine similarity
  - Frontend: sugerencias semánticas mientras el usuario escribe
- **Dependencias**: sentence-transformers, faiss-cpu (o numpy)
- **Riesgo**: Modelo de 80MB agrega peso al deploy; alternativa: usar API externa

#### 3.6 Mapa de sabores del mundo [✅ COMPLETADO]
- **Inspiración**: TasteAtlas, Flavor Genome Project
- **Qué hacer**:
  - Clasificar productos por perfil de sabor: picante, ácido, umami, dulce, salado, amargo, fermentado
  - Nuevo endpoint `GET /flavor-map?continent=...&category=...`
  - Frontend: visualización D3.js tipo radar chart o heatmap por región
  - Filtros por eje de sabor
- **Dependencias**: D3.js (CDN)
- **Riesgo**: Clasificación de sabores requiere kuraduría manual o ML

#### 3.7 Fermentor.org integration
- **Fuente**: fermentor.org (open source)
- **Qué hacer**:
  - Importar recetas y knowledge base de Fermentor (si los datos son abiertos)
  - Exportar batch data a formato compatible con Fermentor
  - Sync bidireccional (futuro)
- **Dependencias**: Verificar licencia de datos de Fermentor
- **Riesgo**: Fermentor puede no tener API pública aún

#### 3.8 Temporizadores ajustados por temperatura [✅ COMPLETADO]
- **Inspiración**: FermentBuddy (timers por temperatura), TEMPURA (T min/ópt/max por cepa)
- **Qué hacer**:
  - Los temporizadores F1/F2 actuales son fijos; añadir ajuste por temperatura ambiente
  - Tabla `fermentation_profiles` (product_id, temp_opt_c, days_at_opt, multiplier_per_degree)
  - Endpoint `GET /timers/{product_id}?temp_c=21` devuelve días estimados ajustados
  - Frontend: input de temperatura en el temporizador ("estoy a 18°C, ¿cuántos días?")
- **Dependencias**: Ninguna
- **Riesgo**: Modelo Q10 simplificado (cada +10°C duplica la velocidad); validar con literatura

#### 3.9 Public API abierta + API keys [✅ COMPLETADO]
- **Inspiración**: Open Brewery DB (sin key), USDA FDC
- **Qué hacer**:
  - Endpoint raíz `GET /api` con documentación de uso
  - Versionado `GET /api/v1/products`
  - Limitación de rate (slowapi o propio) con headers X-RateLimit-*
  - API keys opcionales por email para límites mayores (tabla `api_keys`)
  - Documentación OpenAPI (ya la genera FastAPI) accesible en `/docs`
- **Dependencias**: slowapi (opcional)
- **Riesgo**: Ninguno; expone trabajo ya hecho y permite que otros proyectos nos consuman (ecosistema 2-way)

#### 3.10 Integración MCP (Model Context Protocol) [✅ COMPLETADO]
- **Inspiración**: Fermentr (MCP/Claude), mcp-opennutrition (199★, servidor MCP sobre OpenNutrition con barcode lookup), Brewing MCP, tendencia 2025-2026
- **Qué hacer**:
  - Servidor MCP Python que exponga búsqueda de productos, detalle, ingredientes, temporizadores
  - Herramientas: `search_products`, `get_product`, `get_ingredients`, `get_timer`
  - Añadir herramienta `lookup_barcode` (vía Open Food Facts) — inspirado en mcp-opennutrition
  - Configurar en `mcp/` separado del app principal
  - Permite que Claude/Cursor/agentes consulten la BD de conservas
- **Dependencias**: `mcp` (pip), FastMCP
- **Riesgo**: Bajo; proyecto nuevo separado, no toca el core
- **Valor**: posiciona el dataset como recurso usable por IA, no solo por humanos

---

### FASE 4 — Comunidad y Platform (1-3 meses)

#### 4.1 Auth + usuarios [✅ COMPLETADO]
- **Qué hacer**:
  - Tabla `users` (id, email, username, password_hash, created_at, preferences_json)
  - JWT auth con refresh tokens
  - Registro/login/logout
  - Endpoint `POST /auth/register`, `POST /auth/login`, `GET /auth/me`
  - Guardar preferencias de idioma, región, despensa en server-side
- **Dependencias**: python-jose, passlib, bcrypt (ya disponibles en el ecosistema)
- **Riesgo**: Seguridad: rate limiting en registro, validación de email

#### 4.2 Reviews/reseñas [✅ COMPLETADO]
- **Qué hacer**:
  - Tabla `reviews` (id, user_id, product_id, rating 1-5, text, photos_json, created_at, updated_at)
  - Endpoints: `GET/POST/PUT/DELETE /products/{id}/reviews`
  - Promedio de ratings visible en cards de productos
  - Moderación: flag de contenido reportado
  - Frontend: sección de reviews en detalle de producto
- **Dependencias**: Auth (4.1)
- **Riesgo**: Moderación de contenido, spam

#### 4.3 Recetas comunitarias [✅ COMPLETADO]
- **Qué hacer**:
  - Tabla `recipes` (id, user_id, product_id, title, description, steps_json, ingredients_json, difficulty, prep_time, photos_json, votes, created_at)
  - Endpoints: `GET/POST/PUT/DELETE /recipes`, `POST /recipes/{id}/vote`
  - Feed de recetas recientes
  - Búsqueda y filtrado por dificultad, tiempo, categoría
  - Vinculación con productos existentes
- **Dependencias**: Auth (4.1), Reviews (4.2)
- **Riesgo**: Calidad del contenido, spam

#### 4.4 Course/educación [✅ COMPLETADO]
- **Inspiración**: Harvard Food Fermentation, Startercultures.eu
- **Qué hacer**:
  - Tabla `courses` (id, title, description, modules_json, difficulty, estimated_hours)
  - Tabla `course_modules` (id, course_id, title, content_markdown, order, quiz_json)
  - Módulos: Historia de la fermentación, Ciencia básica, Tipos de fermentación, Seguridad, Recetas prácticas
  - Frontend: player de curso con progreso
  - Certificado de completación (PDF)
- **Dependencias**: Auth (4.1), markdown parser
- **Riesgo**: Creación de contenido educativo de calidad

#### 4.5 Podcast/audio integration [✅ COMPLETADO]
- **Fuentes**: FermUp, Ferment Radio (40+ episodios)
- **Qué hacer**:
  - Indexar episodios de FermUp y Ferment Radio
  - Endpoint `GET /podcast?topic=...&ferment=...`
  - Reproductor de audio integrado en el frontend
  - Vincular episodios con productos relacionados
- **Dependencias**: Verificar APIs/RSS de estos podcasts
- **Riesgo**: Derechos de autor del contenido de audio

#### 4.6 Networking de productores
- **Inspiración**: Slow Food, Ark of Taste
- **Qué hacer**:
  - Tabla `producers` (id, name, country, products_json, website, contact_email, lat, lng)
  - Mapa de productores artesanales
  - Filtro por tipo de producto, región
  - Formulario de registro de productores
  - Futuro: marketplace simple
- **Dependencias**: Auth (4.1), Mapa (2.1)
- **Riesgo**: Verificación de productores, spam

#### 4.7 App móvil (PWA mejorada o React Native)
- **Qué hacer**:
  - PWA mejorada: cámara para fotos de lotes, GPS para productores cercanos, notificaciones push
  - Service worker actualizado con cache de imágenes
  - Bottom navigation para móvil
  - Gestos swipe para navegar productos
  - Futuro: React Native para features nativas (cámara, GPS, notificaciones)
- **Dependencias**: Push API, Camera API, Geolocation API
- **Riesgo**: Testing en múltiples dispositivos

#### 4.8 i18n UI multi-idioma completo
- **Qué hacer**:
  - Hoy la UI es ES/EN pero los datos ya tienen aliases en FR/DE/IT/PT/CZ/FI/TR/AR/JA
  - Migrar strings a un sistema de traducciones (ficheros JSON + `intl` o i18next ligero)
  - Prioridad: FR, DE, PT, IT (mercados fermentadores) luego JA, KO, TR
  - URL por idioma (`/fr/producto/x`) para SEO internacional
- **Dependencias**: i18next (o propio ~2KB), ya hay sistema de traducción parcial
- **Riesgo**: Coste de traducción de ~500 strings; usar plantillas y revisar con nativos

#### 4.9 SEO y structured data
- **Qué hacer**:
  - Sitemap.xml + robots.txt (los productos son ~4,700 páginas indexables)
  - Meta tags Open Graph/Twitter por producto (imagen, título, descripción)
  - Schema.org: `Product`/`Recipe`/`FoodEstablishment` JSON-LD en detalle
  - SSR o prerender del detalle de producto para crawlers (hoy es SPA)
  - Canonical URLs por producto
- **Dependencias**: Ninguna; prerender puede requerir cambiar a render server-side del detalle
- **Riesgo**: SPA + SEO requiere prerender (Preact/astro ligero o mantener página server-rendered)

#### 4.10 Accesibilidad (a11y)
- **Qué hacer**:
  - Auditoría con axe-core / Lighthouse
  - Contraste (relacionado con 1.3 dark mode), focus states, landmarks ARIA
  - Navegación por teclado completa, skip-links
  - Alt text en imágenes (combinado con 2.11), tablas semánticas en stats
  - WCAG 2.1 AA como objetivo
- **Dependencias**: axe-core (dev)
- **Riesgo**: Bajo; requiere revisión de templates HTML

---

### FASE 5 — Infraestructura y mantenimiento (transversal, continuo)

> Fundamento necesario conforme crecen datos (Fase 2) y usuarios (Fase 3-4). Sin esto, cada nueva feature incrementa el riesgo técnico.

#### 5.1 Migraciones de BD (Alembic)
- **Qué hacer**:
  - Integrar Alembic con SQLAlchemy (hoy la BD se crea desde cero en cada build)
  - Flujo: `alembic revision --autogenerate` + migración en CI
  - El pipeline de ingesta no debe crear tablas directamente; usa migraciones
- **Dependencias**: alembic (~500KB)
- **Riesgo**: Reestructurar `ingest/loader.py` para separar schema de datos

#### 5.2 Refresh programado de fuentes (pipeline pull)
- **Qué hacer**:
  - Hoy el pipeline es push-only (se ejecuta a mano). Añadir scheduler:
    - Open Food Facts: re-fetch mensual de productos existentes (nombres, fotos, barcodes cambian)
    - FermDB/Wikidata: semestral
  - Tabla `source_versions` (source, fetched_at, records, checksum) para rastrear qué versión se ingirió
  - GitHub Actions cron job (o Celery beat en Render)
- **Dependencias**: ninguna (GitHub Actions cron gratis)
- **Riesgo**: Bajo; requiere idempotencia del loader (upserts por key natural)

#### 5.3 Caché de respuestas
- **Qué hacer**:
  - Endpoints calientes (búsqueda, detalle, stats, ingredientes) con caché:
    - SQLite/Redis: caché de resultados de FTS y conteos
    - HTTP caching: ETag/Last-Modified en respuestas de productos
  - `Cache-Control` en respuestas estáticas y de detalle
- **Dependencias**: Redis opcional; empezar con caché en memoria (dict TTL)
- **Riesgo**: Invalidadción cuando se refresh las fuentes (limpiar caché por version)

#### 5.4 Monitoreo y logs
- **Qué hacer**:
  - Logging estructurado (JSON) con request id
  - Métricas: p95 latency, errores 5xx, nº búsquedas, top queries fallidas
  - Sentry (gratis para open source) para errores del backend
  - Healthcheck endpoint `GET /health` (ya útil para Render)
- **Dependencias**: sentry-sdk (opcional)
- **Riesgo**: Bajo

#### 5.5 Tests y calidad continua
- **Qué hacer**:
  - Extender suite (hoy 74 tests) con: tests de Fase 2 (imágenes, safety data), Fase 3 (timers, API v1)
  - Tests de datos: no perder cobertura de ingredientes (hoy 99.98%), total de productos, integridad de FKs
  - Mutación básica o coverage report en CI (umbral > 85%)
- **Dependencias**: pytest-cov
- **Riesgo**: Bajo

---

## Orden de Implementación Recomendado

```
FASE 1 (Quick Wins)          → 1-2 semanas
  1.1 Nutrición USDA         → Día 1-2
  1.2 ruff + mypy + CI       → Día 3
  1.3 Dark mode              → Día 4
  1.4 Autocomplete           → Día 5
  1.5 Calendario estacional   → Día 6-7
  1.6 Export PDF/CSV          → Día 8
  1.7 Etiquetas dieta/alérg.  → Día 9
  1.8 Glosario               → Día 10

FASE 2 (Data Integrations)   → 3-4 semanas
  2.11 Imágenes (PRIORIDAD)  → Semana 2   ← nuevo, alto impacto
  2.1 Mapa geográfico        → Semana 2
  2.13 Lácteos FDF-DB        → Semana 2-3 ← nuevo, gap de categoría
  2.3 pH/seguridad           → Semana 2-3
  2.15 Shelf-life FoodKeeper → Semana 3   ← nuevo
  2.10 Timeline histórico     → Semana 3
  2.7 Open Brewery DB        → Semana 3
  2.14 Gap África/MO         → Semana 3-4 ← nuevo
  2.9 Etimología              → Semana 3-4
  2.8 Open Wine Map          → Semana 4
  2.6 Slow Food Ark          → Semana 4
  2.12 Pairing FlavorDB      → Semana 4-5   ← nuevo
  2.16 LanguaL               → Semana 5   ← nuevo
  2.2 Microbioma profundo     → Semana 5-6 (paralelo)
  2.4 Péptidos bioactivos     → Semana 5-6 (paralelo)
  2.5 Ontología FoodOn        → Semana 6

FASE 3 (Features)            → 4-6 semanas
  3.4 Guías paso a paso      → Semana 7-8
  3.2 Calculadoras avanzadas  → Semana 8-9
  3.8 Timers por temperatura  → Semana 9    ← nuevo
  3.3 Pairing de sabores      → Semana 9-10
  3.1 Batch tracking          → Semana 10-12 (requiere auth)
  3.9 Public API + API keys  → Semana 11   ← nuevo, desbloquea ecosistema
  3.6 Mapa de sabores         → Semana 12-13
  3.10 Integración MCP        → Semana 13   ← nuevo
  3.5 Búsqueda semántica       → Semana 13-14

FASE 4 (Comunidad)           → 2-3 meses
  4.1 Auth + usuarios         → Mes 4
  4.2 Reviews                 → Mes 4-5
  4.3 Recetas comunitarias     → Mes 5
  4.4 Course/educación         → Mes 5-6
  4.9 SEO + structured data   → Mes 5      ← nuevo
  4.8 i18n multi-idioma       → Mes 6      ← nuevo
  4.10 Accesibilidad a11y     → Mes 6      ← nuevo
  4.5 Podcast                  → Mes 6
  4.6 Productores              → Mes 6
  4.7 App móvil                → Mes 6+

FASE 5 (Infra, transversal)  → continuo
  5.1 Alembic migraciones     → antes de Fase 2 (imágenes añade columnas)
  5.2 Refresh programado      → junto a 2.11 (fotos cambian)
  5.3 Caché                  → después de 3.9 (API pública la exige)
  5.4 Monitoreo              → cuando haya usuarios (Fase 4)
  5.5 Tests/calidad          → junto a cada fase
```

---

## Stack Técnico Actual vs Necesario

### Ya tenemos
- Python 3.11+, FastAPI, SQLAlchemy, SQLite (FTS5)
- httpx, pandas, pycountry, lxml, pydantic
- Vanilla JS, Chart.js, PWA service worker
- Docker, Render, GitHub Actions CI

### Necesitamos agregar

#### FASE 1
| Dependencia | Para qué | Tamaño |
|---|---|---|
| ruff | Linting | ~5MB |
| mypy | Type checking | ~15MB |

#### FASE 2
| Dependencia | Para qué | Tamaño |
|---|---|---|
| (Leaflet.js) | Mapa (CDN, no pip) | ~40KB |
| (Leaflet.markercluster) | Clustering (CDN) | ~5KB |
| (webp / sharp) | Optimización de imágenes 2.11 | opcional |

#### FASE 3
| Dependencia | Para qué | Tamaño |
|---|---|---|
| python-multipart | File uploads | ~100KB |
| sentence-transformers | Búsqueda semántica (opcional) | ~80MB |
| scikit-learn | Similitud de sabores (opcional) | ~15MB |
| weasyprint | PDF generation (opcional) | ~50MB |
| slowapi | Rate limiting para Public API (opcional) | ~200KB |
| mcp (FastMCP) | Servidor MCP 3.10 | ~1MB |

#### FASE 4
| Dependencia | Para qué | Tamaño |
|---|---|---|
| python-jose | JWT auth | ~50KB |
| passlib | Password hashing | ~100KB |
| bcrypt | Password hashing backend | ~200KB |
| (i18next) | i18n multi-idioma (CDN) | ~10KB |
| (axe-core) | a11y testing (dev) | ~500KB |

#### FASE 5
| Dependencia | Para qué | Tamaño |
|---|---|---|
| alembic | Migraciones de BD | ~500KB |
| sentry-sdk | Monitoreo de errores (opcional) | ~1MB |
| pytest-cov | Coverage en CI | ~100KB |
| (Redis) | Caché (opcional) | externo |

---

## APIs y Fuentes de Datos Disponibles (Resumen)

### Gratuitas / Open Data
- **USDA FoodData Central**: API REST, CC0, 1,000 req/h sin key
- **Open Food Facts**: API v3, ODbL, ya integrado (también fotos de productos)
- **Open Brewery DB**: API REST, gratuita, 11,745+ cervecerías
- **FermDB**: TSV descargable, CC BY 4.0, ya integrado
- **cFMD**: Datasets en Zenodo, académico
- **FoodMicroDB**: GitHub, MIT
- **etymology-db**: GitHub, dataset de Wiktionary
- **preserve-calc**: npm package, open source
- **Open Wine Map**: GeoJSON, open source
- **Wikimedia Commons**: API de imágenes gratuita, licencias libres
- **FlavorDB**: CSV descargable de compuestos de sabor, open
- **TheMealDB**: API de recetas gratuita sin key
- **Fruityvice**: API de frutas gratuita sin key
- **FDF-DB**: Suplemento ZIP open access (CC BY 4.0)
- **LanguaL**: Datasets indexados descargables
- **FoodAtlas**: API + descargas (UC Davis)
- **FSIS FoodKeeper**: JSON oficial USDA vía data.gov (shelf-life)
- **Flavor Network dataset**: Zenodo 829KB (CC BY-NC-SA)

### Requieren contacto/API key
- **Flavor Genome Project**: 1B+ datos de sabores (contactar)
- **ComBase**: Curvas de crecimiento (registro gratuito)
- **Slow Food Ark of Taste**: 5,000+ alimentos (contactar para datos)
- **FoodKG**: SPARQL endpoint (académico)

### Licencias a considerar
- **CC0** (USDA, Wikidata): Sin restricciones
- **CC BY 4.0** (FermDB, cFMD, FDF-DB): Requiere atribución
- **CC BY-SA 4.0** (Wikipedia, DBpedia): Requiere atribución + share-alike
- **ODbL** (Open Food Facts): Requiere atribución + open data
- **CC BY-NC-SA 4.0** (FooDI-ML, Flavor Network dataset): No comercial, requiere atribución + share-alike
- **CC BY-NC-ND 4.0** (FermFooDb): Requiere atribución, no comercial, sin derivados
- **MIT** (proyecto actual): Sin restricciones
- **Unlicense** (open-recipe): Sin restricciones

---

## Preguntas para Decidir

1. **¿Priorizar data o features?** — Más datos enriquecidos (Fase 2) vs. más interactividad (Fase 3)
2. **¿Auth primero o después?** — Batch tracking (3.1) requiere auth; ¿lo hacemos antes o después de las guías (3.4)?
3. **¿Contenido manual o automatizado?** — Las guías paso a paso (3.4) requieren contenido; ¿crear 50 guías manuales o intentar generar con IA?
4. **¿Búsqueda semántica local o API externa?** — sentence-transformers agrega 80MB; ¿mejor usar una API como Cohere/OpenAI?
5. **¿Mobile-first o desktop-first?** — El mapa (2.1) y batch tracking (3.1) son más útiles en móvil; ¿rediseñar el frontend para móvil?
6. **¿Comunidad open o moderada?** — Reviews (4.2) y recetas (4.3) pueden generar spam; ¿moderación manual, automática, o no moderar?
7. **¿Imágenes primero?** — 2.11 (Wikimedia Commons) es el cambio de mayor impacto visual pero añade ~100-200MB; ¿bloquea su almacenamiento en Render/plan de hosting?
8. **¿Licencia de los datos?** — Hoy el dataset mezcla CC BY-SA (Wikipedia), ODbL (OFF), CC BY (FermDB). ¿Publicar el dataset como ODbL o CC BY-SA, o mantener mezcla con atribución?
9. **¿API pública como producto?** — 3.9 la hace accesible sin key; ¿queremos monetizar (premium keys) o mantener 100% open como Open Brewery DB?
10. **¿Prioridad de idiomas en 4.8?** — ¿FR/DE primero (fermentadores europeos) o JA/KO (mercado asiático fermentador)?
11. **¿Lácteos como prioridad?** — FDF-DB (2.13) cubre 1,852 lácteos y cierra un gap de categoría grande; ¿lo subimos a Fase 1 o lo dejamos en Fase 2?
12. **¿Datos no-comerciales?** — FooDI-ML (imágenes) y Flavor Network dataset son CC BY-NC-SA; ¿aceptamos contenido que prohíba uso comercial o lo excluimos?
