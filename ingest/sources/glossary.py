"""Glosario curado de términos de fermentación y conservación (bilingüe es/en).

Cada entrada define `term` en ambos idiomas, su definición y un producto
relacionado opcional (se resuelve por nombre al sembrar). Se genera una fila
por idioma en la tabla `glossary`.
"""

GLOSSARY = [
    # --- Ciencia de la fermentación ---
    {
        "term_es": "fermentación",
        "term_en": "fermentation",
        "definition_es": (
            "Proceso metabólico en el que microorganismos (bacterias, levaduras u hongos) "
            "transforman carbohidratos en ácidos, alcohol o gas, conservando y transformando los alimentos."
        ),
        "definition_en": (
            "Metabolic process in which microorganisms (bacteria, yeasts or fungi) convert "
            "carbohydrates into acids, alcohol or gas, preserving and transforming food."
        ),
    },
    {
        "term_es": "fermentación láctica",
        "term_en": "lactic acid fermentation",
        "definition_es": (
            "Fermentación protagonizada por bacterias del ácido láctico (LAB), que producen "
            "ácido láctico a partir de azúcares. Es la base de chucrut, kimchi, pepinillos y encurtidos."
        ),
        "definition_en": (
            "Fermentation driven by lactic acid bacteria (LAB), which produce lactic acid from "
            "sugars. The basis of sauerkraut, kimchi, pickles and fermented vegetables."
        ),
        "related": "Sauerkraut",
    },
    {
        "term_es": "fermentación alcohólica",
        "term_en": "alcoholic fermentation",
        "definition_es": (
            "Proceso en el que levaduras como Saccharomyces cerevisiae convierten azúcares en "
            "etanol y dióxido de carbono. Es la base del vino, la cerveza y la sidra."
        ),
        "definition_en": (
            "Process in which yeasts such as Saccharomyces cerevisiae convert sugars into ethanol "
            "and carbon dioxide. The basis of wine, beer and cider."
        ),
    },
    {
        "term_es": "fermentación acética",
        "term_en": "acetic fermentation",
        "definition_es": (
            "Segunda fermentación en la que bacterias Acetobacter oxidan el etanol convirtiéndolo "
            "en ácido acético. Produce vinagre a partir de vino, sidra o cerveza."
        ),
        "definition_en": (
            "Secondary fermentation in which Acetobacter bacteria oxidise ethanol into acetic acid. "
            "Produces vinegar from wine, cider or beer."
        ),
        "related": "Vinegar",
    },
    {
        "term_es": "fermentación en salmuera",
        "term_en": "brine fermentation",
        "definition_es": (
            "Fermentación de vegetales sumergidos en una solución de agua con sal (salmuera), que "
            "favorece las bacterias lácticas y frena las putrefactivas. Base de pepinillos y aceitunas."
        ),
        "definition_en": (
            "Fermentation of vegetables submerged in a water-salt solution (brine), which favours "
            "lactic bacteria and inhibits putrefactive ones. The basis of pickles and olives."
        ),
    },
    {
        "term_es": "fermentación en seco",
        "term_en": "dry salt fermentation",
        "definition_es": (
            "Técnica en la que se mezclan vegetales directamente con sal en seco; la sal extrae el "
            "agua celular y forma su propia salmuera. Se usa en chucrut y kimchi."
        ),
        "definition_en": (
            "Technique in which vegetables are mixed directly with dry salt; the salt draws out cell "
            "water forming its own brine. Used for sauerkraut and kimchi."
        ),
        "related": "Sauerkraut",
    },
    {
        "term_es": "fermentación silvestre",
        "term_en": "wild fermentation",
        "definition_es": (
            "Fermentación que se produce con los microorganismos presentes de forma natural en el "
            "alimento y el ambiente, sin añadir un cultivo iniciador."
        ),
        "definition_en": (
            "Fermentation carried out by microorganisms naturally present on the food and in the "
            "environment, without adding a starter culture."
        ),
    },
    {
        "term_es": "inoculación",
        "term_en": "inoculation",
        "definition_es": "Introducción de microorganismos (cultivo iniciador) en un alimento para iniciar la fermentación.",
        "definition_en": "Introduction of microorganisms (starter culture) into a food to start fermentation.",
    },
    {
        "term_es": "cultivo iniciador",
        "term_en": "starter culture",
        "definition_es": (
            "Preparado de microorganismos vivos que se añade para dirigir la fermentación, como el "
            "suero del kéfir, el SCOBY o el koji."
        ),
        "definition_en": (
            "Preparation of live microorganisms added to steer fermentation, such as kefir grains, "
            "the SCOBY or koji."
        ),
    },
    {
        "term_es": "resiembra / backslopping",
        "term_en": "backslopping",
        "definition_es": (
            "Uso de una pequeña porción de un lote fermentado anterior como cultivo iniciador del "
            "siguiente lote. Método tradicional de conservar el cultivo."
        ),
        "definition_en": (
            "Using a small portion of a previous fermented batch as the starter for the next one. "
            "A traditional way to keep a culture alive."
        ),
    },
    {
        "term_es": "anaerobiosis",
        "term_en": "anaerobiosis",
        "definition_es": (
            "Ausencia de oxígeno. Muchas fermentaciones, como la láctica, requieren condiciones "
            "anaeróbicas para evitar mohos y oxidación."
        ),
        "definition_en": (
            "Absence of oxygen. Many fermentations, such as lactic, require anaerobic conditions to "
            "prevent mould and oxidation."
        ),
    },
    {
        "term_es": "ambiente anaeróbico",
        "term_en": "anaerobic environment",
        "definition_es": (
            "Entorno sin oxígeno, típico de fermentaciones sumergidas en salmuera o bajo cierre "
            "hidráulico (airlock), que favorece a bacterias y levaduras frente a mohos."
        ),
        "definition_en": (
            "Oxygen-free environment, typical of brine-submerged fermentations or under an airlock, "
            "that favours bacteria and yeasts over moulds."
        ),
    },
    {
        "term_es": "metabolismo",
        "term_en": "metabolism",
        "definition_es": "Conjunto de reacciones químicas que los organismos usan para obtener energía y materia.",
        "definition_en": "The set of chemical reactions organisms use to obtain energy and matter.",
    },
    {
        "term_es": "enzima",
        "term_en": "enzyme",
        "definition_es": (
            "Proteína que acelera reacciones químicas. En la fermentación descomponen proteínas "
            "(proteasas), almidones (amilasas) y grasas (lipasas)."
        ),
        "definition_en": (
            "Protein that speeds up chemical reactions. In fermentation they break down proteins "
            "(proteases), starches (amylases) and fats (lipases)."
        ),
    },
    {
        "term_es": "amilasa",
        "term_en": "amylase",
        "definition_es": "Enzima que descompone el almidón en azúcares fermentables. Clave en koji y malteado.",
        "definition_en": "Enzyme that breaks starch down into fermentable sugars. Key in koji and malting.",
    },
    {
        "term_es": "proteasa",
        "term_en": "protease",
        "definition_es": "Enzima que rompe proteínas en aminoácidos y péptidos, aportando umami y textura.",
        "definition_en": "Enzyme that breaks proteins into amino acids and peptides, adding umami and texture.",
    },
    {
        "term_es": "glucosa",
        "term_en": "glucose",
        "definition_es": "Azúcar simple (monosacárido) y fuente de energía principal de la mayoría de fermentaciones.",
        "definition_en": "Simple sugar (monosaccharide) and the main energy source of most fermentations.",
    },
    {
        "term_es": "sacarosa",
        "term_en": "sucrose",
        "definition_es": "Azúcar de mesa (disacárido de glucosa y fructosa) que las levaduras dividen antes de fermentar.",
        "definition_en": "Table sugar (a glucose-fructose disaccharide) that yeasts split before fermenting.",
    },
    {
        "term_es": "lactosa",
        "term_en": "lactose",
        "definition_es": "Azúcar de la leche, fermentado por bacterias lácticas en yogur y kéfir.",
        "definition_en": "Milk sugar, fermented by lactic bacteria in yogurt and kefir.",
    },
    {
        "term_es": "pH",
        "term_en": "pH",
        "definition_es": (
            "Medida de acidez (0-14). En fermentación, el descenso de pH por debajo de 4,6 inhibe "
            "patógenos como Clostridium botulinum."
        ),
        "definition_en": (
            "Measure of acidity (0-14). In fermentation, a drop below pH 4.6 inhibits pathogens such "
            "as Clostridium botulinum."
        ),
    },
    {
        "term_es": "acidez",
        "term_en": "acidity",
        "definition_es": "Concentración de ácidos (láctico, acético) producida durante la fermentación; responsable del sabor y la conservación.",
        "definition_en": "Concentration of acids (lactic, acetic) produced during fermentation; responsible for flavour and preservation.",
    },
    {
        "term_es": "ácido láctico",
        "term_en": "lactic acid",
        "definition_es": "Ácido orgánico producido por bacterias lácticas; confiere sabor ácido y baja el pH.",
        "definition_en": "Organic acid produced by lactic acid bacteria; gives a sour flavour and lowers pH.",
    },
    {
        "term_es": "ácido acético",
        "term_en": "acetic acid",
        "definition_es": "Ácido principal del vinagre (3-5%), producido por Acetobacter a partir del etanol.",
        "definition_en": "The main acid of vinegar (3-5%), produced by Acetobacter from ethanol.",
        "related": "Vinegar",
    },
    {
        "term_es": "ácido propiónico",
        "term_en": "propionic acid",
        "definition_es": "Ácido que da el sabor característico al queso suizo, producido por bacterias propiónicas.",
        "definition_en": "Acid that gives Swiss cheese its characteristic flavour, produced by propionic bacteria.",
    },
    {
        "term_es": "etanol",
        "term_en": "ethanol",
        "definition_es": "Alcohol producido por levaduras en fermentación alcohólica; se evapora o se transforma en fermentaciones posteriores.",
        "definition_en": "Alcohol produced by yeasts during alcoholic fermentation; evaporates or is transformed in later fermentations.",
    },
    {
        "term_es": "dióxido de carbono",
        "term_en": "carbon dioxide",
        "definition_es": "Gas producido por levaduras y bacterias; carbonata kombucha y cerveza y crea atmósfera protectora.",
        "definition_en": "Gas produced by yeasts and bacteria; carbonates kombucha and beer and creates a protective atmosphere.",
    },
    {
        "term_es": "hidrólisis",
        "term_en": "hydrolysis",
        "definition_es": "Rotura de moléculas grandes con agua, catalizada por enzimas; libera azúcares, aminoácidos y ácidos grasos.",
        "definition_en": "Breakdown of large molecules with water, catalysed by enzymes; releases sugars, amino acids and fatty acids.",
    },
    {
        "term_es": "aminoácidos",
        "term_en": "amino acids",
        "definition_es": "Unidades de las proteínas liberadas por las proteasas; fuente principal del sabor umami.",
        "definition_en": "Building blocks of proteins released by proteases; the main source of umami flavour.",
    },
    {
        "term_es": "glutamato",
        "term_en": "glutamate",
        "definition_es": "Aminoácido responsable del sabor umami; abundante en miso, soja fermentada y quesos maduros.",
        "definition_en": "Amino acid responsible for umami flavour; abundant in miso, fermented soy and aged cheeses.",
    },
    {
        "term_es": "umami",
        "term_en": "umami",
        "definition_es": "El quinto sabor básico, un gusto salado-sabroso aportado por glutamatos y nucleótidos de las fermentaciones.",
        "definition_en": "The fifth basic taste, a savoury flavour provided by glutamates and nucleotides from fermentation.",
    },
    {
        "term_es": "probióticos",
        "term_en": "probiotics",
        "definition_es": "Microorganismos vivos que, ingeridos en cantidad suficiente, aportan beneficios a la salud intestinal.",
        "definition_en": "Live microorganisms that, consumed in sufficient amounts, provide benefits to gut health.",
    },
    {
        "term_es": "prebióticos",
        "term_en": "prebiotics",
        "definition_es": "Fibras y compuestos no digeribles que alimentan a las bacterias beneficiosas del intestino.",
        "definition_en": "Non-digestible fibres and compounds that feed beneficial gut bacteria.",
    },
    # --- Microorganismos ---
    {
        "term_es": "bacterias del ácido láctico (BAL)",
        "term_en": "lactic acid bacteria (LAB)",
        "definition_es": (
            "Grupo de bacterias (Lactobacillus, Leuconostoc, Pediococcus...) que fermentan azúcares "
            "produciendo ácido láctico. Conservan y dan sabor a vegetales y lácteos."
        ),
        "definition_en": (
            "Group of bacteria (Lactobacillus, Leuconostoc, Pediococcus...) that ferment sugars into "
            "lactic acid. They preserve and flavour vegetables and dairy."
        ),
    },
    {
        "term_es": "Lactobacillus",
        "term_en": "Lactobacillus",
        "definition_es": (
            "Género clave de bacterias lácticas presentes en yogur, chucrut, kimchi y kéfir; "
            "productoras de ácido láctico y probióticos."
        ),
        "definition_en": (
            "Key genus of lactic bacteria found in yogurt, sauerkraut, kimchi and kefir; producers of "
            "lactic acid and probiotics."
        ),
    },
    {
        "term_es": "Leuconostoc",
        "term_en": "Leuconostoc",
        "definition_es": (
            "Bacteria láctica que inicia la fermentación de muchos vegetales en salmuera, "
            "produciendo ácido láctico, acético y dióxido de carbono."
        ),
        "definition_en": (
            "Lactic bacterium that starts the fermentation of many brined vegetables, producing "
            "lactic and acetic acid and carbon dioxide."
        ),
    },
    {
        "term_es": "Pediococcus",
        "term_en": "Pediococcus",
        "definition_es": "Bacteria láctica que aparece en fases avanzadas de la fermentación de vegetales; tolera bien la sal y el ácido.",
        "definition_en": "Lactic bacterium found in later stages of vegetable fermentation; tolerates salt and acid well.",
    },
    {
        "term_es": "levadura",
        "term_en": "yeast",
        "definition_es": "Hongos unicelulares que fermentan azúcares en alcohol y CO₂. Clave en pan, vino, cerveza, kombucha y kéfir.",
        "definition_en": "Single-celled fungi that ferment sugars into alcohol and CO₂. Key in bread, wine, beer, kombucha and kefir.",
    },
    {
        "term_es": "Saccharomyces cerevisiae",
        "term_en": "Saccharomyces cerevisiae",
        "definition_es": "Levadura de la cerveza y el pan; el microorganismo fermentador más utilizado por el ser humano.",
        "definition_en": "The brewer's and baker's yeast; the most widely used fermenting microorganism by humans.",
    },
    {
        "term_es": "levadura kahm",
        "term_en": "kahm yeast",
        "definition_es": (
            "Pellícula blanca y arrugada que a veces aparece en la superficie de fermentaciones "
            "expuestas al aire. Inofensiva pero con sabor desagradable; se retira."
        ),
        "definition_en": (
            "White, wrinkled film that sometimes appears on the surface of fermentations exposed to "
            "air. Harmless but off-flavoured; it is skimmed off."
        ),
    },
    {
        "term_es": "Brettanomyces",
        "term_en": "Brettanomyces",
        "definition_es": "Levadura salvaje que aporta notas terrosas, especiadas y de cuadra en cervezas y vinos de fermentación espontánea.",
        "definition_en": "Wild yeast contributing earthy, spicy and barnyard notes in spontaneously fermented beers and wines.",
    },
    {
        "term_es": "moho",
        "term_en": "mould",
        "definition_es": "Hongos filamentosos que crecen en superficies aeróbicas. Algunos son deseables (koji, quesos), otros son signo de deterioro.",
        "definition_en": "Filamentous fungi growing on aerobic surfaces. Some are desirable (koji, cheeses), others signal spoilage.",
    },
    {
        "term_es": "Aspergillus oryzae (koji)",
        "term_en": "Aspergillus oryzae (koji)",
        "definition_es": (
            "Hongo domesticado de Japón que inocula arroz, cebada o soja para producir enzimas. "
            "Base del miso, el shoyu y el sake."
        ),
        "definition_en": (
            "Domesticated fungus from Japan that inoculates rice, barley or soy to produce enzymes. "
            "The basis of miso, shoyu and sake."
        ),
        "related": "Koji",
    },
    {
        "term_es": "Penicillium",
        "term_en": "Penicillium",
        "definition_es": "Género de mohos usados en la maduración de quesos azules y en la producción de antibióticos.",
        "definition_en": "Genus of moulds used in the ripening of blue cheeses and the production of antibiotics.",
    },
    {
        "term_es": "Acetobacter",
        "term_en": "Acetobacter",
        "definition_es": "Bacteria que oxida el alcohol a ácido acético; responsable del vinagre y de la madre del vinagre.",
        "definition_en": "Bacterium that oxidises alcohol into acetic acid; responsible for vinegar and the vinegar mother.",
        "related": "Vinegar",
    },
    {
        "term_es": "propionibacterias",
        "term_en": "propionic bacteria",
        "definition_es": "Bacterias que fermentan el ácido láctico en ácido propiónico y CO₂; crean los ojos del queso suizo.",
        "definition_en": "Bacteria that ferment lactic acid into propionic acid and CO₂; create the eyes of Swiss cheese.",
    },
    {
        "term_es": "SCOBY",
        "term_en": "SCOBY",
        "definition_es": (
            "Simbiosis de bacterias y levaduras que forma una membrana gelatinosa; cultivo iniciador "
            "de la kombucha y el tibicos."
        ),
        "definition_en": (
            "Symbiotic culture of bacteria and yeasts forming a gelatinous membrane; the starter "
            "culture for kombucha and water kefir."
        ),
        "related": "Kombucha",
    },
    {
        "term_es": "tibicos",
        "term_en": "water kefir",
        "definition_es": (
            "Gránulos translúcidos de bacterias y levaduras que fermentan agua azucarada (con higos o "
            "limón) en una bebida ligeramente ácida y efervescente."
        ),
        "definition_en": (
            "Translucent granules of bacteria and yeasts that ferment sugared water (with figs or "
            "lemon) into a mildly sour, effervescent drink."
        ),
        "related": "Water kefir",
    },
    {
        "term_es": "kéfir",
        "term_en": "kefir",
        "definition_es": (
            "Leche fermentada por gránulos de bacterias y levaduras; bebida ácida, efervescente y "
            "muy rica en probióticos."
        ),
        "definition_en": (
            "Milk fermented by granules of bacteria and yeasts; a sour, effervescent drink rich in "
            "probiotics."
        ),
        "related": "Kefir",
    },
    {
        "term_es": "Clostridium botulinum",
        "term_en": "Clostridium botulinum",
        "definition_es": (
            "Bacteria anaerobia que produce la toxina botulínica. Se inhibe con pH < 4,6, altas "
            "temperaturas o sal en conservas."
        ),
        "definition_en": (
            "Anaerobic bacterium producing botulinum toxin. Inhibited by pH < 4.6, high "
            "temperatures or salt in preserves."
        ),
    },
    {
        "term_es": "Escherichia coli",
        "term_en": "Escherichia coli",
        "definition_es": "Bacteria intestinal que en ciertas cepas es patógena; controlada por la acidez de la fermentación.",
        "definition_en": "Gut bacterium, pathogenic in certain strains; controlled by fermentation acidity.",
    },
    {
        "term_es": "bacterias acéticas",
        "term_en": "acetic acid bacteria",
        "definition_es": "Microorganismos aerobios que transforman alcohol en ácido acético; producen vinagre y kombucha.",
        "definition_en": "Aerobic microorganisms that turn alcohol into acetic acid; produce vinegar and kombucha.",
    },
    {
        "term_es": "hongo",
        "term_en": "fungus",
        "definition_es": "Organismo eucariota que incluye levaduras y mohos; esencial en pan, vino, queso y koji.",
        "definition_en": "Eukaryotic organism including yeasts and moulds; essential in bread, wine, cheese and koji.",
    },
    # --- Técnicas y equipamiento ---
    {
        "term_es": "salmuera",
        "term_en": "brine",
        "definition_es": "Solución de agua y sal en la que se fermentan vegetales; normalmente entre 2% y 5% de sal.",
        "definition_en": "Water and salt solution in which vegetables are fermented; typically 2% to 5% salt.",
    },
    {
        "term_es": "porcentaje de sal",
        "term_en": "salt percentage",
        "definition_es": (
            "Proporción de sal respecto al peso total (agua + vegetales). El 2-3% favorece la "
            "fermentación láctica; más sal la frena."
        ),
        "definition_en": (
            "Ratio of salt to total weight (water + vegetables). 2-3% favours lactic fermentation; "
            "more salt slows it down."
        ),
    },
    {
        "term_es": "peso de fermentación",
        "term_en": "fermentation weight",
        "definition_es": "Objeto pesado que mantiene los vegetales sumergidos bajo la salmuera, fuera del contacto con el aire.",
        "definition_en": "Heavy object that keeps vegetables submerged below the brine, away from air contact.",
    },
    {
        "term_es": "cierre hidráulico / airlock",
        "term_en": "airlock",
        "definition_es": "Dispositivo que deja escapar el CO₂ e impide la entrada de oxígeno durante la fermentación.",
        "definition_en": "Device that lets CO₂ escape while preventing oxygen from entering during fermentation.",
    },
    {
        "term_es": "bote con válvula / bote de fermentación",
        "term_en": "fermentation crock",
        "definition_es": "Recipiente, tradicionalmente de cerámica, con tapa y aro de agua que sella la fermentación sin presión.",
        "definition_en": "Vessel, traditionally ceramic, with a lid and water ring that seals fermentation without pressure.",
    },
    {
        "term_es": "tarro tipo Fido / Weck",
        "term_en": "Fido / Weck jar",
        "definition_es": "Tarro de cierre hermético con junta de goma que permite la salida de gas y evita la entrada de aire.",
        "definition_en": "Hermetic-seal jar with a rubber gasket that lets gas out while preventing air from entering.",
    },
    {
        "term_es": "desgasificado",
        "term_en": "burping",
        "definition_es": "Abrir periódicamente el recipiente de fermentación para liberar el CO₂ acumulado y evitar presión excesiva.",
        "definition_en": "Periodically opening the fermentation vessel to release accumulated CO₂ and avoid excess pressure.",
    },
    {
        "term_es": "fermentación primaria",
        "term_en": "primary fermentation",
        "definition_es": "Fase principal y activa en la que los microorganismos transforman los azúcares; la mayor producción de gas y sabor.",
        "definition_en": "The main, active phase in which microorganisms transform sugars; the greatest gas and flavour production.",
    },
    {
        "term_es": "fermentación secundaria",
        "term_en": "secondary fermentation",
        "definition_es": "Fase posterior de afinado y carbonatación (p. ej. F2 en kombucha), a menudo embotellada y con más azúcar.",
        "definition_en": "Later conditioning and carbonation phase (e.g. F2 in kombucha), often bottled with extra sugar.",
    },
    {
        "term_es": "maduración",
        "term_en": "aging / maturation",
        "definition_es": "Periodo de reposo tras la fermentación activa en el que se desarrollan aromas, textura y complejidad.",
        "definition_en": "Rest period after active fermentation during which aromas, texture and complexity develop.",
    },
    {
        "term_es": "pasteurización",
        "term_en": "pasteurisation",
        "definition_es": "Tratamiento térmico suave (p. ej. 72 °C) que elimina patógenos sin destruir del todo el alimento.",
        "definition_en": "Gentle heat treatment (e.g. 72 °C) that eliminates pathogens without fully destroying the food.",
    },
    {
        "term_es": "esterilización",
        "term_en": "sterilisation",
        "definition_es": "Eliminación de todos los microorganismos mediante calor, presión o productos químicos; esencial en el envasado.",
        "definition_en": "Elimination of all microorganisms through heat, pressure or chemicals; essential in packaging.",
    },
    {
        "term_es": "baño María",
        "term_en": "water bath canning",
        "definition_es": "Método de conserva en el que los tarros sellados se sumergen en agua hirviendo; válido solo para alimentos ácidos.",
        "definition_en": "Canning method in which sealed jars are submerged in boiling water; only valid for acidic foods.",
    },
    {
        "term_es": "envasado a presión",
        "term_en": "pressure canning",
        "definition_es": "Conservación con autoclave a alta temperatura y presión; necesaria para alimentos de baja acidez.",
        "definition_en": "Preservation with an autoclave at high temperature and pressure; required for low-acid foods.",
    },
    {
        "term_es": "escabeche",
        "term_en": "pickling",
        "definition_es": "Conservación en vinagre (a menudo con especias y aceite), con o sin fermentación previa.",
        "definition_en": "Preservation in vinegar (often with spices and oil), with or without prior fermentation.",
    },
    {
        "term_es": "encurtido",
        "term_en": "pickle",
        "definition_es": "Alimento, generalmente vegetal, conservado en salmuera fermentada o en vinagre.",
        "definition_en": "Food, usually a vegetable, preserved in fermented brine or in vinegar.",
    },
    {
        "term_es": "pepinillo",
        "term_en": "cucumber pickle / gherkin",
        "definition_es": "Pepino conservado en salmuera fermentada o en vinagre, a menudo con eneldo y ajo.",
        "definition_en": "Cucumber preserved in fermented brine or vinegar, often with dill and garlic.",
    },
    {
        "term_es": "fermento",
        "term_en": "ferment / culture",
        "definition_es": "Nombre coloquial de un alimento o bebida fermentada, y del cultivo microbiano que lo produce.",
        "definition_en": "Colloquial name for a fermented food or drink, and for the microbial culture that produces it.",
    },
    {
        "term_es": "madre del vinagre",
        "term_en": "vinegar mother",
        "definition_es": "Masa gelatinosa de bacterias acéticas que se forma en vinagres sin pasteurizar; permite iniciar nuevas fermentaciones.",
        "definition_en": "Gelatinous mass of acetic bacteria formed in unpasteurised vinegars; can start new fermentations.",
        "related": "Vinegar",
    },
    {
        "term_es": "confitado",
        "term_en": "confit",
        "definition_es": "Técnica de conservación cociendo el alimento lentamente en grasa a baja temperatura.",
        "definition_en": "Preservation technique of slowly cooking food in fat at low temperature.",
    },
    {
        "term_es": "ahumado",
        "term_en": "smoking",
        "definition_es": "Conservación y aromatización de alimentos mediante humo de madera, que además seca la superficie.",
        "definition_en": "Preservation and flavouring of food with wood smoke, which also dries the surface.",
    },
    {
        "term_es": "salazón",
        "term_en": "salting / salt-curing",
        "definition_es": "Conservación con sal seca o en salmuera concentrada, que deshidrata y frena microorganismos.",
        "definition_en": "Preservation with dry salt or concentrated brine, which dehydrates and inhibits microorganisms.",
    },
    {
        "term_es": "curado",
        "term_en": "curing",
        "definition_es": "Tratamiento con sal, nitritos, azúcar y/o humo para conservar carnes y pescados y darles sabor y color.",
        "definition_en": "Treatment with salt, nitrites, sugar and/or smoke to preserve meats and fish and give flavour and colour.",
    },
    {
        "term_es": "deshidratación",
        "term_en": "dehydration",
        "definition_es": "Eliminación de agua para impedir el crecimiento microbiano; método de conservación milenario.",
        "definition_en": "Removal of water to prevent microbial growth; an ancient preservation method.",
    },
    {
        "term_es": "lactofermentación",
        "term_en": "lacto-fermentation",
        "definition_es": "Fermentación de vegetales, frutas o salsas por bacterias lácticas, sin vinagre ni calor.",
        "definition_en": "Fermentation of vegetables, fruit or sauces by lactic bacteria, without vinegar or heat.",
    },
    {
        "term_es": "fermentación en dos fases",
        "term_en": "two-stage fermentation",
        "definition_es": "Proceso con una primera fase principal y una segunda de afinado/carbonatación, típico de kombucha y kvas.",
        "definition_en": "Process with a first main phase and a second conditioning/carbonation phase, typical of kombucha and kvas.",
    },
    {
        "term_es": "cultivo madre",
        "term_en": "mother culture",
        "definition_es": "Cultivo persistente que se mantiene vivo entre lotes, como los gránulos de kéfir o el SCOBY.",
        "definition_en": "Culture kept alive between batches, such as kefir grains or the SCOBY.",
    },
    {
        "term_es": "sello hermético",
        "term_en": "hermetic seal",
        "definition_es": "Cierre que impide la entrada de aire y microorganismos; clave para conservar y para la fermentación anaeróbica.",
        "definition_en": "Seal preventing air and microorganisms from entering; key for preserving and anaerobic fermentation.",
    },
    # --- Ingredientes y productos ---
    {
        "term_es": "koji",
        "term_en": "koji",
        "definition_es": (
            "Arroz, cebada o soja inoculados con Aspergillus oryzae. Produce las enzimas que "
            "convierten almidón y proteína en azúcar y aminoácidos."
        ),
        "definition_en": (
            "Rice, barley or soy inoculated with Aspergillus oryzae. Produces the enzymes that turn "
            "starch and protein into sugar and amino acids."
        ),
        "related": "Koji",
    },
    {
        "term_es": "shio koji",
        "term_en": "shio koji",
        "definition_es": "Koji de arroz fermentado con sal y agua; adobo y marinado umami de la cocina japonesa.",
        "definition_en": "Rice koji fermented with salt and water; an umami marinade of Japanese cuisine.",
        "related": "Shio koji",
    },
    {
        "term_es": "miso",
        "term_en": "miso",
        "definition_es": (
            "Pasta japonesa de soja fermentada con koji y sal. Variedades: blanco (shiro), rojo "
            "(aka) y mixto (awase)."
        ),
        "definition_en": (
            "Japanese paste of soy fermented with koji and salt. Varieties: white (shiro), red (aka) "
            "and mixed (awase)."
        ),
        "related": "Miso",
    },
    {
        "term_es": "shoyu",
        "term_en": "shoyu / soy sauce",
        "definition_es": "Salsa de soja japonesa fermentada con koji, trigo, soja y sal durante meses o años.",
        "definition_en": "Japanese soy sauce fermented with koji, wheat, soy and salt over months or years.",
        "related": "Shoyu",
    },
    {
        "term_es": "tamari",
        "term_en": "tamari",
        "definition_es": "Salsa de soja espesa, originalmente el líquido sobrante del miso; hoy se hace solo con soja.",
        "definition_en": "Thick soy sauce, originally the liquid drained from miso; now made from soy alone.",
        "related": "Tamari",
    },
    {
        "term_es": "amazake",
        "term_en": "amazake",
        "definition_es": "Bebida japonesa dulce de arroz fermentado con koji; naturalmente dulce y sin alcohol (o muy poco).",
        "definition_en": "Sweet Japanese drink of rice fermented with koji; naturally sweet and alcohol-free (or nearly).",
        "related": "Amazake",
    },
    {
        "term_es": "tempeh",
        "term_en": "tempeh",
        "definition_es": "Pastel indonesio de soja cocida inoculada con el hongo Rhizopus; proteína firme y con sabor a frutos secos.",
        "definition_en": "Indonesian cake of cooked soy inoculated with the fungus Rhizopus; firm, nutty protein.",
        "related": "Tempeh",
    },
    {
        "term_es": "kimchi",
        "term_en": "kimchi",
        "definition_es": "Encurtido fermentado coreano, tradicionalmente de col napa con ajo, jengibre, gochugaru y sal.",
        "definition_en": "Korean fermented pickle, traditionally of napa cabbage with garlic, ginger, gochugaru and salt.",
        "related": "Kimchi",
    },
    {
        "term_es": "chucrut",
        "term_en": "sauerkraut",
        "definition_es": "Col blanca fermentada en seco con sal; fermentación láctica clásica de Europa central.",
        "definition_en": "White cabbage dry-fermented with salt; the classic lactic fermentation of central Europe.",
        "related": "Sauerkraut",
    },
    {
        "term_es": "col napa",
        "term_en": "napa cabbage",
        "definition_es": "Col asiática de hojas tiernas, base del kimchi tradicional coreano.",
        "definition_en": "Asian cabbage with tender leaves, the base of traditional Korean kimchi.",
        "related": "Kimchi",
    },
    {
        "term_es": "gochugaru",
        "term_en": "gochugaru",
        "definition_es": "Pimiento rojo coreano en escamas, ingrediente distintivo del kimchi.",
        "definition_en": "Korean red chilli flakes, the signature ingredient of kimchi.",
        "related": "Kimchi",
    },
    {
        "term_es": "kombucha",
        "term_en": "kombucha",
        "definition_es": "Té dulce fermentado con SCOBY; bebida ácida, ligeramente efervescente y probiótica.",
        "definition_en": "Sweet tea fermented with a SCOBY; a sour, lightly effervescent, probiotic drink.",
        "related": "Kombucha",
    },
    {
        "term_es": "vino de kombucha",
        "term_en": "kombucha wine",
        "definition_es": "Kombucha fermentada más tiempo y con más azúcar, con mayor contenido alcohólico.",
        "definition_en": "Kombucha fermented longer with more sugar, yielding higher alcohol content.",
        "related": "Kombucha",
    },
    {
        "term_es": "yogur",
        "term_en": "yogurt",
        "definition_es": "Leche fermentada por Lactobacillus y Streptococcus; ácida, cremosa y con proteína.",
        "definition_en": "Milk fermented by Lactobacillus and Streptococcus; sour, creamy and protein-rich.",
        "related": "Yogurt",
    },
    {
        "term_es": "queso",
        "term_en": "cheese",
        "definition_es": "Producto lácteo obtenido por coagulación de la caseína y posterior fermentación y maduración.",
        "definition_en": "Dairy product obtained by coagulating casein and subsequent fermentation and ripening.",
        "related": "Cheese",
    },
    {
        "term_es": "cuajo",
        "term_en": "rennet",
        "definition_es": "Enzimas que coagulan la leche separando la cuajada del suero; esencial en la elaboración de queso.",
        "definition_en": "Enzymes that coagulate milk separating curds from whey; essential in cheesemaking.",
        "related": "Cheese",
    },
    {
        "term_es": "cuajada",
        "term_en": "curd",
        "definition_es": "Sólido proteico que se forma al coagular la leche; base del queso.",
        "definition_en": "Protein solid formed when milk coagulates; the basis of cheese.",
    },
    {
        "term_es": "suero de leche",
        "term_en": "whey",
        "definition_es": "Líquido verdoso que se separa de la cuajada; rico en lactosa y proteínas séricas.",
        "definition_en": "Greenish liquid that separates from the curd; rich in lactose and whey proteins.",
    },
    {
        "term_es": "crema agria",
        "term_en": "sour cream",
        "definition_es": "Crema de leche fermentada por bacterias lácticas; espesa, ácida y usada como acompañamiento.",
        "definition_en": "Cream fermented by lactic bacteria; thick, sour and used as a topping.",
    },
    {
        "term_es": "crème fraîche",
        "term_en": "crème fraîche",
        "definition_es": "Crema francesa ligeramente fermentada; más espesa y menos ácida que la crema agria.",
        "definition_en": "French cream, lightly fermented; thicker and less sour than sour cream.",
    },
    {
        "term_es": "vinagre",
        "term_en": "vinegar",
        "definition_es": "Líquido ácido de alcohol fermentado por bacterias acéticas; condimento y conservante universal.",
        "definition_en": "Sour liquid of alcohol fermented by acetic bacteria; a universal condiment and preservative.",
        "related": "Vinegar",
    },
    {
        "term_es": "pan de masa madre",
        "term_en": "sourdough bread",
        "definition_es": "Pan fermentado con masa madre (agua + harina fermentadas), sin levadura comercial; sabor ácido y buena miga.",
        "definition_en": "Bread fermented with a sourdough starter (fermented flour and water), without commercial yeast; tangy flavour and good crumb.",
        "related": "Sourdough",
    },
    {
        "term_es": "masa madre",
        "term_en": "sourdough starter",
        "definition_es": "Cultivo vivo de harina y agua con levaduras y bacterias salvajes que leudan el pan.",
        "definition_en": "Live culture of flour and water with wild yeasts and bacteria that leaven bread.",
        "related": "Sourdough",
    },
    {
        "term_es": "cerveza",
        "term_en": "beer",
        "definition_es": "Bebida fermentada de granos malteados (cebada, trigo) aromatizada con lúpulo.",
        "definition_en": "Fermented drink of malted grains (barley, wheat) flavoured with hops.",
        "related": "Beer",
    },
    {
        "term_es": "vino",
        "term_en": "wine",
        "definition_es": "Bebida alcohólica de uva fermentada por levaduras; una de las fermentaciones más antiguas.",
        "definition_en": "Alcoholic drink of grapes fermented by yeasts; one of the oldest fermentations.",
        "related": "Wine",
    },
    {
        "term_es": "sidra",
        "term_en": "cider",
        "definition_es": "Bebida fermentada de manzana; seca o dulce, con o sin gas.",
        "definition_en": "Fermented apple drink; dry or sweet, still or sparkling.",
        "related": "Cider",
    },
    {
        "term_es": "hidromiel",
        "term_en": "mead",
        "definition_es": "Bebida alcohólica de miel y agua fermentadas; una de las bebidas más antiguas del mundo.",
        "definition_en": "Alcoholic drink of fermented honey and water; one of the world's oldest beverages.",
        "related": "Mead",
    },
    {
        "term_es": "kvas",
        "term_en": "kvas",
        "definition_es": "Bebida eslava ligeramente fermentada, tradicionalmente de pan de centeno con azúcar y a veces fruta o menta.",
        "definition_en": "Slavic lightly fermented drink, traditionally of rye bread with sugar and sometimes fruit or mint.",
        "related": "Kvas",
    },
    {
        "term_es": "salsa de pescado",
        "term_en": "fish sauce",
        "definition_es": "Condimento líquido de pescado fermentado en salmuera; base del garum y del nam pla.",
        "definition_en": "Liquid condiment of fish fermented in brine; the basis of garum and nam pla.",
        "related": "Fish sauce",
    },
    {
        "term_es": "garum",
        "term_en": "garum",
        "definition_es": "Salsa de pescado fermentado de la Antigua Roma; ancestro de las salsas de pescado asiáticas.",
        "definition_en": "Fermented fish sauce of Ancient Rome; ancestor of Asian fish sauces.",
        "related": "Fish sauce",
    },
    {
        "term_es": "nuoc mam",
        "term_en": "nuoc mam",
        "definition_es": "Salsa de pescado vietnamita fermentada en barriles de sal durante meses.",
        "definition_en": "Vietnamese fish sauce fermented in salt barrels over months.",
        "related": "Fish sauce",
    },
    {
        "term_es": "anchoas en salazón",
        "term_en": "salted anchovies",
        "definition_es": "Boquerones curados en sal y madurados; sabor intenso y umami.",
        "definition_en": "Anchovies salt-cured and aged; intense, umami flavour.",
        "related": "Anchovy",
    },
    {
        "term_es": "aceitunas",
        "term_en": "olives",
        "definition_es": "Fruto del olivo tratado en salmuera fermentada para quitar su amargor natural.",
        "definition_en": "Olive fruit processed in fermented brine to remove its natural bitterness.",
        "related": "Olives",
    },
    {
        "term_es": "pepinillos de eneldo",
        "term_en": "dill pickles",
        "definition_es": "Pepinos fermentados en salmuera con eneldo, ajo y especias; clásicos de Nueva York.",
        "definition_en": "Cucumbers fermented in brine with dill, garlic and spices; New York classics.",
    },
    {
        "term_es": "kimchi de col napa",
        "term_en": "baechu kimchi",
        "definition_es": "La variante más famosa de kimchi, hecha con col napa y condimentos picantes.",
        "definition_en": "The most famous kimchi variety, made with napa cabbage and spicy seasonings.",
        "related": "Kimchi",
    },
    {
        "term_es": "kombucha de jengibre",
        "term_en": "ginger kombucha",
        "definition_es": "Kombucha saborizada con jengibre en la segunda fermentación, típicamente efervescente.",
        "definition_en": "Kombucha flavoured with ginger in the second fermentation, typically effervescent.",
        "related": "Kombucha",
    },
    {
        "term_es": "sake",
        "term_en": "sake",
        "definition_es": "Vino de arroz japonés fermentado con koji y levadura en un proceso paralelo único.",
        "definition_en": "Japanese rice wine fermented with koji and yeast in a unique parallel process.",
        "related": "Sake",
    },
    {
        "term_es": "mirin",
        "term_en": "mirin",
        "definition_es": "Condimento dulce japonés de arroz fermentado, usado para glasear y suavizar sabores.",
        "definition_en": "Sweet Japanese rice-fermented seasoning used to glaze and soften flavours.",
    },
    {
        "term_es": "gochujang",
        "term_en": "gochujang",
        "definition_es": "Pasta coreana de chile, arroz glutinoso y soja fermentada; picante, dulce y umami.",
        "definition_en": "Korean paste of chilli, glutinous rice and fermented soy; spicy, sweet and umami.",
        "related": "Gochujang",
    },
    {
        "term_es": "doenjang",
        "term_en": "doenjang",
        "definition_es": "Pasta coreana de soja fermentada, similar al miso pero más rústica y potente.",
        "definition_en": "Korean fermented soy paste, similar to miso but more rustic and pungent.",
        "related": "Doenjang",
    },
    {
        "term_es": "doubanjiang",
        "term_en": "doubanjiang",
        "definition_es": "Pasta fermentada china de habas y chile; base del mapo tofu de Sichuan.",
        "definition_en": "Chinese fermented broad bean and chilli paste; the base of Sichuan mapo tofu.",
    },
    {
        "term_es": "nattō",
        "term_en": "nattō",
        "definition_es": "Soja fermentada japonesa con Bacillus subtilis; pegajosa, con aroma intenso y muy nutritiva.",
        "definition_en": "Japanese soy fermented with Bacillus subtilis; sticky, intensely aromatic and very nutritious.",
        "related": "Natto",
    },
    {
        "term_es": "Bacillus subtilis",
        "term_en": "Bacillus subtilis",
        "definition_es": "Bacteria que fermenta la soja del nattō, produciendo las hebras pegajosas características.",
        "definition_en": "Bacterium that ferments nattō soy, producing its characteristic sticky strands.",
        "related": "Natto",
    },
    {
        "term_es": "surströmming",
        "term_en": "surströmming",
        "definition_es": "Arenque del Báltico fermentado en lata, de aroma extremadamente intenso; especialidad sueca.",
        "definition_en": "Baltic herring fermented in tins, with an extremely intense aroma; a Swedish speciality.",
    },
    {
        "term_es": "hákarl",
        "term_en": "hákarl",
        "definition_es": "Tiburón de Groenlandia fermentado y curado, especialidad islandesa de sabor muy fuerte.",
        "definition_en": "Fermented and cured Greenland shark, an Icelandic speciality with a very strong taste.",
    },
    {
        "term_es": "injera",
        "term_en": "injera",
        "definition_es": "Pan plano etíope fermentado con teff; esponjoso, ligeramente ácido y base de la mesa.",
        "definition_en": "Ethiopian flatbread fermented from teff; spongy, mildly sour and the base of the meal.",
        "related": "Injera",
    },
    {
        "term_es": "idli",
        "term_en": "idli",
        "definition_es": "Pastelito al vapor del sur de la India, de arroz y lentejas fermentados.",
        "definition_en": "South Indian steamed cake of fermented rice and lentils.",
    },
    {
        "term_es": "dosa",
        "term_en": "dosa",
        "definition_es": "Crepe crujiente del sur de la India, hecha con masa fermentada de arroz y lentejas.",
        "definition_en": "Crispy South Indian crepe made from fermented rice and lentil batter.",
    },
    {
        "term_es": "gari",
        "term_en": "gari",
        "definition_es": "Jengibre joven encurtido en vinagre dulce, servido con sushi.",
        "definition_en": "Young ginger pickled in sweet vinegar, served with sushi.",
    },
    {
        "term_es": "tsukemono",
        "term_en": "tsukemono",
        "definition_es": "Encurtidos japoneses variados, fermentados en sal, salvado de arroz (nukazuke) o vinagre.",
        "definition_en": "Assorted Japanese pickles, fermented in salt, rice bran (nukazuke) or vinegar.",
    },
    {
        "term_es": "nukazuke",
        "term_en": "nukazuke",
        "definition_es": "Vegetales fermentados en salvado de arroz (nuka); técnica tradicional japonesa con sabor único.",
        "definition_en": "Vegetables fermented in rice bran (nuka); a traditional Japanese technique with a unique flavour.",
    },
    {
        "term_es": "kimchee (variante)",
        "term_en": "kimchee (variant)",
        "definition_es": "Transcripción alternativa de kimchi, habitual en el sudeste asiático.",
        "definition_en": "Alternative transcription of kimchi, common in Southeast Asia.",
        "related": "Kimchi",
    },
    {
        "term_es": "salsa de chile fermentada",
        "term_en": "fermented chilli sauce",
        "definition_es": "Salsa picante obtenida por fermentación láctica de chiles con sal (p. ej. tabasco, sriracha).",
        "definition_en": "Spicy sauce made by lactic fermentation of chillies with salt (e.g. tabasco, sriracha).",
    },
    {
        "term_es": "sriracha",
        "term_en": "sriracha",
        "definition_es": "Salsa picante tailandesa de chiles rojos, ajo, azúcar y vinagre, con un toque fermentado.",
        "definition_en": "Thai hot sauce of red chillies, garlic, sugar and vinegar, with a fermented edge.",
    },
    # --- Conservación y seguridad ---
    {
        "term_es": "conserva",
        "term_en": "preserve / canned food",
        "definition_es": "Alimento tratado y sellado para su conservación a largo plazo mediante calor, ácido, sal o azúcar.",
        "definition_en": "Food treated and sealed for long-term preservation through heat, acid, salt or sugar.",
    },
    {
        "term_es": "enlatado",
        "term_en": "canning",
        "definition_es": "Método de conservación en envase sellado con calor; puede ser en baño María o a presión.",
        "definition_en": "Preservation method in a sealed container with heat; either water bath or pressure canning.",
    },
    {
        "term_es": "conservas de baja acidez",
        "term_en": "low-acid foods",
        "definition_es": "Alimentos con pH > 4,6 (carnes, verduras, legumbres) que exigen envasado a presión.",
        "definition_en": "Foods with pH > 4.6 (meats, vegetables, legumes) that require pressure canning.",
    },
    {
        "term_es": "alimentos ácidos",
        "term_en": "acid foods",
        "definition_es": "Alimentos con pH < 4,6 (frutas, tomates, encurtidos) que pueden conservarse en baño María.",
        "definition_en": "Foods with pH < 4.6 (fruits, tomatoes, pickles) that can be preserved in a water bath.",
    },
    {
        "term_es": "botulismo",
        "term_en": "botulism",
        "definition_es": "Intoxicación grave por la toxina de Clostridium botulinum, relacionada con conservas mal procesadas.",
        "definition_en": "Severe poisoning by Clostridium botulinum toxin, linked to improperly processed canned food.",
    },
    {
        "term_es": "deterioro",
        "term_en": "spoilage",
        "definition_es": "Alteración de un alimento por microorganismos no deseados, con malos olores, gases o cambios de color.",
        "definition_en": "Alteration of food by unwanted microorganisms, with off-odours, gas or colour changes.",
    },
    {
        "term_es": "fermento arruinado",
        "term_en": "failed ferment",
        "definition_es": "Fermentación en la que dominan mohos o bacterias putrefactivas, detectable por olor, color o textura.",
        "definition_en": "Fermentation in which moulds or putrefactive bacteria dominate, detectable by smell, colour or texture.",
    },
    {
        "term_es": "vida útil",
        "term_en": "shelf life",
        "definition_es": "Periodo durante el cual un alimento conserva sus cualidades de seguridad y sabor.",
        "definition_en": "Period during which a food retains its safety and flavour qualities.",
    },
    {
        "term_es": "caducidad",
        "term_en": "expiry date",
        "definition_es": "Fecha límite de consumo seguro de un producto.",
        "definition_en": "Deadline for the safe consumption of a product.",
    },
    {
        "term_es": "refrigeración",
        "term_en": "refrigeration",
        "definition_es": "Conservación a temperaturas bajas (2-8 °C) que ralentiza el crecimiento microbiano.",
        "definition_en": "Preservation at low temperatures (2-8 °C) that slows microbial growth.",
    },
    {
        "term_es": "congelación",
        "term_en": "freezing",
        "definition_es": "Conservación por debajo de 0 °C, que detiene casi por completo la actividad microbiana.",
        "definition_en": "Preservation below 0 °C, which almost completely halts microbial activity.",
    },
    {
        "term_es": "esterilización comercial",
        "term_en": "commercial sterilisation",
        "definition_es": "Tratamiento térmico que elimina microorganismos capaces de reproducirse en el envase a temperatura ambiente.",
        "definition_en": "Heat treatment that eliminates microorganisms capable of growing in the container at room temperature.",
    },
    {
        "term_es": "sello al vacío",
        "term_en": "vacuum seal",
        "definition_es": "Extracción del aire del envase para reducir oxidación y crecimiento aerobio.",
        "definition_en": "Removal of air from the container to reduce oxidation and aerobic growth.",
    },
    {
        "term_es": "fermentación bajo atmósfera inerte",
        "term_en": "inert atmosphere fermentation",
        "definition_es": "Fermentación protegida del oxígeno con gas neutro, evitando mohos y oxidación.",
        "definition_en": "Fermentation shielded from oxygen with neutral gas, avoiding mould and oxidation.",
    },
    {
        "term_es": "sal gema / sal marina",
        "term_en": "rock salt / sea salt",
        "definition_es": "Sales no refinadas usadas en salmueras; deben evitarse las sales con yodo o aditivos anticompactantes.",
        "definition_en": "Unrefined salts used in brines; iodised or anti-caking salts should be avoided.",
    },
    {
        "term_es": "sal sin yodo",
        "term_en": "non-iodised salt",
        "definition_es": "Sal de mesa sin yodo, preferida para fermentaciones porque el yodo puede enturbiar y manchar.",
        "definition_en": "Table salt without iodine, preferred for fermentation as iodine can cloud and discolour.",
    },
    {
        "term_es": "azúcar",
        "term_en": "sugar",
        "definition_es": "Edulcorante que también funciona como conservante en alta concentración (mermeladas, confituras).",
        "definition_en": "Sweetener that also works as a preservative at high concentration (jams, preserves).",
    },
    {
        "term_es": "miel",
        "term_en": "honey",
        "definition_es": "Edulcorante natural antimicrobiano por su baja actividad de agua; base del hidromiel.",
        "definition_en": "Natural sweetener, antimicrobial due to its low water activity; the basis of mead.",
    },
    {
        "term_es": "actividad de agua (aw)",
        "term_en": "water activity (aw)",
        "definition_es": "Medida del agua disponible para los microorganismos; valores bajos frenan el crecimiento microbiano.",
        "definition_en": "Measure of water available to microorganisms; low values inhibit microbial growth.",
    },
    {
        "term_es": "osmosis",
        "term_en": "osmosis",
        "definition_es": "Paso de agua a través de una membrana; la sal y el azúcar la explotan para deshidratar y conservar.",
        "definition_en": "Movement of water across a membrane; salt and sugar exploit it to dehydrate and preserve.",
    },
    {
        "term_es": "deshidratación osmótica",
        "term_en": "osmotic dehydration",
        "definition_es": "Eliminación de agua del alimento sumergiéndolo en soluciones concentradas de sal o azúcar.",
        "definition_en": "Removal of water from food by immersion in concentrated salt or sugar solutions.",
    },
    {
        "term_es": "sorbato / conservantes",
        "term_en": "sorbate / preservatives",
        "definition_es": "Aditivos que impiden el crecimiento de mohos y levaduras en alimentos procesados.",
        "definition_en": "Additives that prevent mould and yeast growth in processed foods.",
    },
    {
        "term_es": "escabechado con especias",
        "term_en": "spiced pickling",
        "definition_es": "Encurtido aromatizado con especias como eneldo, mostaza, pimienta o laurel.",
        "definition_en": "Pickling flavoured with spices such as dill, mustard, pepper or bay leaf.",
    },
    {
        "term_es": "fermento de sal",
        "term_en": "salt ferment",
        "definition_es": "Cualquier alimento fermentado cuyo principal conservante es la sal.",
        "definition_en": "Any food fermented whose main preservative is salt.",
    },
    # --- Términos culturales ---
    {
        "term_es": "gastronomía de fermentación",
        "term_en": "fermentation gastronomy",
        "definition_es": "Cocina que usa deliberadamente la fermentación como técnica central de sabor, conservación y salud.",
        "definition_en": "Cuisine that deliberately uses fermentation as a central technique of flavour, preservation and health.",
    },
    {
        "term_es": "terroir microbiano",
        "term_en": "microbial terroir",
        "definition_es": "Conjunto de microorganismos propios de un lugar que dan carácter único a sus fermentaciones.",
        "definition_en": "The set of microorganisms native to a place that give its fermentations a unique character.",
    },
    {
        "term_es": "fermentación tradicional",
        "term_en": "traditional fermentation",
        "definition_es": "Prácticas de fermentación transmitidas culturalmente, sin cultivos comerciales ni aditivos modernos.",
        "definition_en": "Fermentation practices passed down through culture, without commercial cultures or modern additives.",
    },
    {
        "term_es": "conservas de la abuela",
        "term_en": "grandma's preserves",
        "definition_es": "Técnicas domésticas de conservación transmitidas de generación en generación.",
        "definition_en": "Home preservation techniques passed down through generations.",
    },
    {
        "term_es": "fermento de autor",
        "term_en": "chef ferment",
        "definition_es": "Fermentaciones experimentales de cocineros modernos que exploran texturas y sabores nuevos.",
        "definition_en": "Experimental fermentations by modern chefs exploring new textures and flavours.",
    },
]


# Nombres de producto alternativos en la BD para términos cuyos vínculos
# no coinciden con el nombre canónico del producto.
_RELATED_ALIASES = {
    "yogurt": ["yogur"],
    "cider": ["sidra"],
    "kvas": ["Kvass"],
    "olives": ["Aceitunas"],
    "fish sauce": ["Fish Sauce", "Nam pla fish sauce", "Salsa de Pescado Tailandesa (Salsa Fish)"],
    "water kefir": ["water kefir"],
    "natto": ["Natto polvo", "Kotsubu Natto", "Natto Powder"],
    "koji": ["Koji Miso Paste", "Koji Miso pasta"],
}


def seed_glossary(session):
    """Inserta (o actualiza) las entradas del glosario bilingüe en la tabla `glossary`."""
    from app.db import models

    rows = 0
    updated = 0
    products = {
        p.name.lower(): p.id
        for p in session.query(models.Product).filter(models.Product.status != "discarded").all()
    }
    for item in GLOSSARY:
        related_id = None
        related_name = item.get("related")
        if related_name:
            candidates = [related_name.lower(), related_name.lower().replace(" ", "")]
            candidates += [a.lower() for a in _RELATED_ALIASES.get(related_name.lower(), [])]
            for key in candidates:
                if key in products:
                    related_id = products[key]
                    break
        for language in ("es", "en"):
            term = item[f"term_{language}"].strip()
            definition = item[f"definition_{language}"].strip()
            existing = (
                session.query(models.GlossaryTerm)
                .filter_by(term=term, language=language)
                .first()
            )
            if existing is None:
                session.add(
                    models.GlossaryTerm(
                        term=term,
                        definition=definition,
                        language=language,
                        related_product_id=related_id,
                    )
                )
                rows += 1
            elif existing.related_product_id != related_id:
                existing.related_product_id = related_id
                updated += 1
    session.commit()
    return rows, updated
