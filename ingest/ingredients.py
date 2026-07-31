import re
import unicodedata

# Ingredientes canonicos (EN) con alias multilingue (EN/ES/FR + typos conocidos).
# El matcher extrae de un texto libre los ingredientes canonicos con max-munch:
# ante solapamientos, gana el alias mas largo (p.ej. "coconut milk" > "coconut" + "milk").

CANONICAL_INGREDIENTS = [
    # --- Vegetales ---
    {"name": "cabbage", "category": "vegetal", "aliases": [
        "cabbage", "repollo", "chou", "col", "coles", "white cabbage", "red cabbage",
        "napa cabbage", "chinese cabbage", "brassica", "green cabbage",
    ]},
    {"name": "cucumber", "category": "vegetal", "aliases": [
        "cucumber", "cucumbers", "pepino", "concombre", "gherkin", "cornichon",
        "cumber", "cucumis sativus",
    ]},
    {"name": "carrot", "category": "vegetal", "aliases": [
        "carrot", "carrots", "zanahoria", "carotte", "black carrot", "carottes",
    ]},
    {"name": "radish", "category": "vegetal", "aliases": [
        "radish", "radishes", "radish root", "radish roots", "rabano", "radis",
        "daikon", "white radish", "mooli", "radish leaves",
    ]},
    {"name": "garlic", "category": "vegetal", "aliases": [
        "garlic", "ajo", "ail", "garlic cloves", "garlic and spices",
    ]},
    {"name": "onion", "category": "vegetal", "aliases": [
        "onion", "onions", "cebolla", "oignon", "red onion", "spring onion",
    ]},
    {"name": "shallot", "category": "vegetal", "aliases": [
        "shallot", "shallots", "chalote", "echalote", "chalota",
    ]},
    {"name": "ginger", "category": "vegetal", "aliases": [
        "ginger", "jengibre", "gingembre", "ginger root", "rhizome of ginger",
    ]},
    {"name": "chili", "category": "vegetal", "aliases": [
        "chili", "chilli", "chile", "chiles", "chilis", "chillies", "chili pepper",
        "red pepper", "bird pepper", "bird's eye chili", "cayenne", "aji",
        "chili powder", "chilli powder", "pimenton", "piment rouge", "chile pepper",
        "hot pepper", "chilli pepper",
    ]},
    {"name": "pepper", "category": "vegetal", "aliases": [
        "bell pepper", "sweet pepper", "sweet red bell pepper", "sweet green bell pepper",
        "green pepper", "red bell pepper", "pimiento", "poivron", "capsicum",
        "piment doux", "peppers", "bell peppers",
    ]},
    {"name": "eggplant", "category": "vegetal", "aliases": [
        "eggplant", "aubergine", "berenjena", "eggplants", "brinjal",
    ]},
    {"name": "okra", "category": "vegetal", "aliases": [
        "okra", "okras", "gombo", "gumbo", "quimbombo", "bamia",
    ]},
    {"name": "tomato", "category": "vegetal", "aliases": [
        "tomato", "tomatoes", "tomate", "tomates", "tomato puree",
    ]},
    {"name": "pumpkin", "category": "vegetal", "aliases": [
        "pumpkin", "pumpkins", "calabaza", "citrouille", "squash", "winter squash",
        "butternut squash", "courge", "pumpkin flowers",
    ]},
    {"name": "leek", "category": "vegetal", "aliases": [
        "leek", "leeks", "puerro", "poireau", "porro",
    ]},
    {"name": "cauliflower", "category": "vegetal", "aliases": [
        "cauliflower", "coliflor", "chou-fleur", "choufleur", "cauliflower flower",
    ]},
    {"name": "beet", "category": "vegetal", "aliases": [
        "beet", "beets", "beetroot", "remolacha", "betterave", "beet roots",
        "red beet", "beta vulgaris",
    ]},
    {"name": "turnip", "category": "vegetal", "aliases": [
        "turnip", "turnips", "nabo", "navet", "turnip root", "mustard tuber",
        "brassica rapa",
    ]},
    {"name": "mustard", "category": "vegetal", "aliases": [
        "mustard", "mostaza", "moutarde", "mustard leaves", "mustard greens",
        "mustard cabbage", "leaf mustard", "chinese mustard", "mustard tuber",
        "mustard oil",
    ]},
    {"name": "bamboo shoot", "category": "vegetal", "aliases": [
        "bamboo shoot", "bamboo shoots", "bamboo shoot tips", "bambu", "bambou",
        "bamboo plant", "bamboo sap",
    ]},
    {"name": "olive", "category": "vegetal", "aliases": [
        "olive", "olives", "aceituna", "oliva", "olivas", "black olives", "green olives",
    ]},
    {"name": "artichoke", "category": "vegetal", "aliases": [
        "artichoke", "artichokes", "alcachofa", "artichaut", "globe artichoke",
    ]},
    {"name": "caper", "category": "vegetal", "aliases": [
        "caper", "capers", "alcaparra", "alcaparras", "câpre", "câpres",
        "capper", "cappers", "alcaparrones",
    ]},
    {"name": "spinach", "category": "vegetal", "aliases": [
        "spinach", "espinaca", "epinard", "spinach leaves", "red spinach",
    ]},
    {"name": "celery", "category": "vegetal", "aliases": [
        "celery", "apio", "celeri", "celeriac",
    ]},
    {"name": "mushroom", "category": "hongo", "aliases": [
        "mushroom", "mushrooms", "champignon", "champignons", "seta", "setas",
        "champinon", "shiitake", "oyster mushroom", "enoki", "fungus", "hongos",
        "wild mushroom",
    ]},
    {"name": "vegetables", "category": "vegetal", "aliases": [
        "vegetables", "vegetable", "verduras", "verdura", "hortalizas",
        "legumes crus", "légumes", "legume", "mixed vegetables", "assorted vegetables",
        "various vegetables", "leafy greens", "greens", "green leafy vegetables",
    ]},
    {"name": "watercress", "category": "vegetal", "aliases": [
        "watercress", "berro", "cresson",
    ]},
    {"name": "lettuce", "category": "vegetal", "aliases": [
        "lettuce", "lechuga", "laitue",
    ]},

    # --- Frutas ---
    {"name": "apple", "category": "fruta", "aliases": [
        "apple", "apples", "manzana", "pomme", "crab apple", "apple cider",
    ]},
    {"name": "grape", "category": "fruta", "aliases": [
        "grape", "grapes", "uva", "uvas", "raisin", "raisins", "white grape",
        "red grapes", "white or red grapes", "grapes", "muscadine",
    ]},
    {"name": "plum", "category": "fruta", "aliases": [
        "plum", "plums", "ciruela", "prune", "prunes", "pruneau",
    ]},
    {"name": "mango", "category": "fruta", "aliases": ["mango", "mangoes", "mangos", "mangue"]},
    {"name": "papaya", "category": "fruta", "aliases": [
        "papaya", "pawpaw", "paw paw", "fruta bomba",
    ]},
    {"name": "pineapple", "category": "fruta", "aliases": [
        "pineapple", "pineapples", "pina", "ananas", "ananás",
    ]},
    {"name": "banana", "category": "fruta", "aliases": [
        "banana", "bananas", "plátano", "platano", "banane", "bananes",
    ]},
    {"name": "plantain", "category": "fruta", "aliases": [
        "plantain", "plantains", "plátano macho", "platano macho", "banane plantain",
        "plaintain", "cooking banana",
    ]},
    {"name": "breadfruit", "category": "fruta", "aliases": [
        "breadfruit", "fruit a pain", "fruta de pan", "ulu", "breadfruit tree",
    ]},
    {"name": "lemon", "category": "fruta", "aliases": [
        "lemon", "lemons", "limon", "citron", "lemon juice", "citron vert",
    ]},
    {"name": "lime", "category": "fruta", "aliases": [
        "lime", "limes", "lima", "key lime", "lime juice",
    ]},
    {"name": "orange", "category": "fruta", "aliases": [
        "orange", "oranges", "naranja", "orange peel", "bitter orange",
    ]},
    {"name": "date", "category": "fruta", "aliases": [
        "date", "dates", "datil", "datte", "dattes", "phoenix dactylifera",
    ]},
    {"name": "fig", "category": "fruta", "aliases": [
        "fig", "figs", "higo", "higos", "figue", "figues",
    ]},
    {"name": "coconut", "category": "fruta", "aliases": [
        "coconut", "coco", "noix de coco", "coconuts", "desiccated coconut",
        "coconut flesh", "coconut pulp",
    ]},
    {"name": "coconut milk", "category": "bebida", "substrate": False, "aliases": [
        "coconut milk", "leche de coco", "lait de coco",
    ]},
    {"name": "durian", "category": "fruta", "aliases": [
        "durian", "durio", "durian fruit", "cempedak",
    ]},
    {"name": "berries", "category": "fruta", "aliases": [
        "berries", "berry", "baya", "bayas", "wild berries", "wild berry juice",
        "mixed berries", "red berries",
    ]},
    {"name": "strawberry", "category": "fruta", "aliases": [
        "strawberry", "strawberries", "fresa", "fresas", "fraise", "fraises",
    ]},
    {"name": "raspberry", "category": "fruta", "aliases": [
        "raspberry", "raspberries", "frambuesa", "framboise",
    ]},
    {"name": "blueberry", "category": "fruta", "aliases": [
        "blueberry", "blueberries", "arandano", "myrtille",
    ]},
    {"name": "blackberry", "category": "fruta", "aliases": [
        "blackberry", "blackberries", "mora", "mure", "zarzamora",
    ]},
    {"name": "gooseberry", "category": "fruta", "aliases": [
        "gooseberry", "gooseberries", "grosella", "groseille",
    ]},
    {"name": "elderberry", "category": "fruta", "aliases": [
        "elderberry", "elderberries", "sauco", "sureau", "elderflower",
    ]},
    {"name": "juniper berry", "category": "fruta", "aliases": [
        "juniper berry", "juniper berries", "enebro", "genevre",
    ]},
    {"name": "pomegranate", "category": "fruta", "aliases": [
        "pomegranate", "granada", "grenade", "pomegranates",
    ]},
    {"name": "persimmon", "category": "fruta", "aliases": [
        "persimmon", "kaki", "caqui", "kaki fruit", "sharon fruit",
    ]},
    {"name": "peach", "category": "fruta", "aliases": [
        "peach", "peaches", "melocoton", "durazno", "peche", "peach flower",
    ]},
    {"name": "apricot", "category": "fruta", "aliases": [
        "apricot", "apricots", "albaricoque", "damasco", "abricot",
    ]},
    {"name": "cherry", "category": "fruta", "aliases": [
        "cherry", "cherries", "cereza", "cerise", "sour cherry",
    ]},
    {"name": "pear", "category": "fruta", "aliases": [
        "pear", "pears", "pera", "poire",
    ]},
    {"name": "jackfruit", "category": "fruta", "aliases": [
        "jackfruit", "jack fruit", "yaca", "jaca", "jacquier",
    ]},
    {"name": "lychee", "category": "fruta", "aliases": [
        "lychee", "lychees", "lichi", "litchi", "litchi chinensis",
    ]},
    {"name": "cashew", "category": "fruta", "aliases": [
        "cashew", "cashew apple", "caju", "maranon", "marañón", "cashew fruit",
    ]},
    {"name": "tamarind", "category": "fruta", "aliases": [
        "tamarind", "tamarindo", "tamarind pulp",
    ]},
    {"name": "baobab", "category": "fruta", "aliases": [
        "baobab", "baobab fruit", "baobab pulp", "african baobab", "baobab seed",
    ]},
    {"name": "roselle", "category": "fruta", "aliases": [
        "roselle", "hibiscus", "jamaica flower", "roselle calyces", "hibiscus sabdariffa",
    ]},
    {"name": "rhododendron", "category": "fruta", "aliases": [
        "rhododendron", "petals of rhododendron", "rhododendron flowers",
    ]},
    {"name": "fruits", "category": "fruta", "aliases": [
        "fruits", "fruit", "frutas", "fruta", "various fruits", "mixed fruit",
        "assorted fruits", "wild fruit", "fruits rouges",
    ]},

    # --- Cereales ---
    {"name": "rice", "category": "cereal", "aliases": [
        "rice", "arroz", "riz", "glutinous rice", "sticky rice", "sweet rice",
        "red rice", "black rice", "rice flour", "rice grits", "rice water",
        "rice-wheat flour-milk", "cooked rice", "steamed glutinous rice",
        "polished glutinous rice", "roasted rice", "paddy rice", "wild rice",
        "non-glutinous rice", "purple rice", "oryza sativa",
    ]},
    {"name": "wheat", "category": "cereal", "aliases": [
        "wheat", "trigo", "ble", "froment", "wheat flour", "wheat berries",
        "durum wheat", "semolina", "wheat bran", "wheat grains", "wheat gluten",
        "gluten", "triticum", "bulgur", "burghul", "cracked wheat",
    ]},
    {"name": "barley", "category": "cereal", "aliases": [
        "barley", "cebada", "orge", "barley malt", "pearl barley", "malted barley",
        "barley flour", "hordeum",
    ]},
    {"name": "oat", "category": "cereal", "aliases": [
        "oat", "oats", "avena", "avoine", "oatmeal", "oat flour", "rolled oats",
        "oat bran",
    ]},
    {"name": "rye", "category": "cereal", "aliases": [
        "rye", "centeno", "seigle", "rye flour", "rye bread", "stale rye bread",
        "rye malt", "rye and barley malt",
    ]},
    {"name": "millet", "category": "cereal", "aliases": [
        "millet", "mijo", "mil", "finger millet", "pearl millet", "foxtail millet",
        "ragi", "millet seed", "millet flour", "great millet",
    ]},
    {"name": "sorghum", "category": "cereal", "aliases": [
        "sorghum", "sorgo", "sorghum bicolor", "sorghum vulgare", "kaffircorn",
        "jowar", "red sorghum", "sorghum flour",
    ]},
    {"name": "corn", "category": "cereal", "aliases": [
        "corn", "maize", "maiz", "mais", "sweet corn", "corn flour", "cornmeal",
        "maize meal", "hominy", "corn kernels", "sweetcorn", "zea mays",
        "corn starch", "maize flour",
    ]},
    {"name": "buckwheat", "category": "cereal", "aliases": [
        "buckwheat", "trigo sarraceno", "sarrasin", "buckwheat flour", "buckwheat groats",
    ]},
    {"name": "teff", "category": "cereal", "aliases": [
        "teff", "tef", "teff flour", "teff and other cereals",
    ]},
    {"name": "fonio", "category": "cereal", "aliases": [
        "fonio", "acha", "hungry rice",
    ]},
    {"name": "ensete", "category": "cereal", "aliases": [
        "ensete", "enset", "false banana", "kocho",
    ]},
    {"name": "bread", "category": "cereal", "aliases": [
        "bread", "pan", "pain", "rye bread", "wheat bread", "breadcrumbs",
        "stale bread", "bread slices",
    ]},
    {"name": "flour", "category": "cereal", "aliases": [
        "flour", "harina", "farine", "all-purpose flour", "plain flour", "maida",
    ]},
    {"name": "grains", "category": "cereal", "aliases": [
        "grains", "grain", "cereal grains", "whole grains", "grain mash",
        "milled grain", "cooked grains",
    ]},
    {"name": "malt", "category": "cereal", "aliases": [
        "malt", "malta", "malte", "malt extract", "grain malt", "malted grains",
    ]},
    {"name": "sourdough", "category": "cereal", "substrate": False, "aliases": [
        "sourdough", "masa madre", "levain", "sourdough starter",
    ]},

    # --- Legumbres ---
    {"name": "soybean", "category": "legumbre", "aliases": [
        "soybean", "soybeans", "soy bean", "soy beans", "soya bean", "soya beans",
        "soya", "soja", "soy", "edamame", "black soybean", "black soybeans",
        "yellow soybean", "whole soybean", "fermented soybean", "soybeans",
        "soy flakes", "soy nuts", "soy protein",
    ]},
    {"name": "black gram", "category": "legumbre", "aliases": [
        "black gram", "black gram bean", "black gram dhal", "urad dal", "urad bean",
        "mash bean", "vigna mungo", "phaseolus mungo",
    ]},
    {"name": "mung bean", "category": "legumbre", "aliases": [
        "mung bean", "mung beans", "green gram", "moong", "vigna radiata",
    ]},
    {"name": "chickpea", "category": "legumbre", "aliases": [
        "chickpea", "chickpeas", "chick pea", "chick peas", "bengal gram",
        "garbanzo", "garbanzos", "cicer arietinum",
    ]},
    {"name": "pea", "category": "legumbre", "aliases": [
        "pea", "peas", "guisante", "pois", "green peas", "split peas", "split pea",
        "black eyed pea", "black-eyed peas", "pigeon pea",
    ]},
    {"name": "lentil", "category": "legumbre", "aliases": [
        "lentil", "lentils", "lenteja", "lentejas", "lentille", "lentilles",
        "black lentil", "black lentils", "red lentil",
    ]},
    {"name": "broad bean", "category": "legumbre", "aliases": [
        "broad bean", "broad beans", "fava bean", "fava beans", "fava", "habas",
        "haba", "vicia faba", "horse bean",
    ]},
    {"name": "horse gram", "category": "legumbre", "aliases": [
        "horse gram", "horsegram", "kulthi",
    ]},
    {"name": "cowpea", "category": "legumbre", "aliases": [
        "cowpea", "cowpeas", "black-eyed pea", "black eyed peas",
    ]},
    {"name": "peanut", "category": "legumbre", "aliases": [
        "peanut", "peanuts", "cacahuete", "cacahuate", "mani", "arachide",
        "groundnut", "peanut press cake", "peanut cake",
    ]},
    {"name": "locust bean", "category": "legumbre", "aliases": [
        "locust bean", "locust beans", "african locust bean", "parkia", "parkia biglobosa",
        "iru", "dawadawa", "soumbala", "african locust beans",
    ]},
    {"name": "oil bean", "category": "legumbre", "aliases": [
        "oil bean", "african oil bean", "ugba", "pentaclethra",
    ]},
    {"name": "okara", "category": "legumbre", "aliases": [
        "okara", "soybean curd", "soy cake", "okara soybean",
    ]},
    {"name": "tofu", "category": "legumbre", "aliases": [
        "tofu", "bean curd", "doufu", "tofu skin", "fermented tofu",
    ]},
    {"name": "miso", "category": "legumbre", "aliases": [
        "miso", "miso paste", "miso soybean", "fermented soybean paste",
    ]},
    {"name": "tempeh", "category": "legumbre", "aliases": [
        "tempeh", "tempe", "tempeh cake", "tempeh starter",
    ]},
    {"name": "natto", "category": "legumbre", "aliases": [
        "natto", "nattō", "nattou",
    ]},
    {"name": "soy sauce", "category": "legumbre", "substrate": False, "aliases": [
        "soy sauce", "soya sauce", "shoyu", "tamari", "salsa de soja",
        "sauce soja", "sauce de soja", "sos de soja", "kecap manis", "soybean paste",
    ]},
    {"name": "douchi", "category": "legumbre", "aliases": [
        "douchi", "touchi", "fermented black bean", "fermented black beans",
        "salted black beans",
    ]},
    {"name": "gochujang", "category": "vegetal", "aliases": [
        "gochujang", "gochu jang", "gochujang paste", "fermented chili paste",
    ]},
    {"name": "bean", "category": "legumbre", "aliases": [
        "bean", "beans", "frijoles", "haricots", "haricot", "dried beans",
        "common bean", "kidney bean", "kidney beans", "phaseolus",
    ]},

    # --- Raices / tuberculos ---
    {"name": "cassava", "category": "raiz", "aliases": [
        "cassava", "cassava root", "cassava roots", "cassava tuber", "cassava flour",
        "cassava starch", "yuca", "manioc", "mandioca", "tapioca", "tapioca flour",
        "manioc flour", "cassava leaves",
    ]},
    {"name": "potato", "category": "raiz", "aliases": [
        "potato", "potatoes", "papa", "patata", "pomme de terre", "potato flour",
        "new potatoes",
    ]},
    {"name": "sweet potato", "category": "raiz", "aliases": [
        "sweet potato", "sweet potatoes", "boniato", "batata", "camote", "kumara",
    ]},
    {"name": "yam", "category": "raiz", "aliases": [
        "yam", "yams", "ñame", "name", "igname", "yam root", "water yam",
        "yellow yam", "african yam",
    ]},
    {"name": "taro", "category": "raiz", "aliases": [
        "taro", "malanga", "dasheen", "taro corms", "taro root", "colocasia",
        "eddoe", "colocasia leaves",
    ]},
    {"name": "rhynchosia", "category": "raiz", "aliases": [
        "rhynchosia", "white extract of rhynchosia roots", "rhynchosia roots",
    ]},
    {"name": "turnip root", "category": "raiz", "aliases": ["turnip root"]},

    # --- Lacteos ---
    {"name": "milk", "category": "lacteo", "aliases": [
        "milk", "leche", "lait", "latte", "cow milk", "cow's milk", "cows' milk",
        "whole milk", "raw milk", "fresh milk", "skim milk", "skimmed milk",
        "semi-skimmed milk", "pasteurized milk", "unpasteurized milk", "goat milk",
        "goat's milk", "sheep milk", "sheep's milk", "ewe milk", "ewe's milk",
        "buffalo milk", "yak milk", "camel milk", "mare milk", "mare's milk",
        "reindeer milk", "dzo milk", "milk powder", "powdered milk", "dry milk",
        "condensed milk", "sour milk", "zebu milk", "buffalo or cow milk",
        "goat or cow milk", "cow or buffalo milk", "goat or sheep milk",
        "sheep and goat milk", "cow and goat milk", "raw or pasteurized cow milk",
        "pasteurized cow milk", "unpasteurized cow milk", "whole or skimmed cow milk",
        "raw cow milk", "raw sheep milk", "raw ewe milk", "raw goat milk",
        "skimmed goat or cow milk", "buffalo or mixed milk", "yak or cow milk",
        "mare milk or camel milk", "yak or dzo milk", "camel milk or goat milk",
        "goat's and sheep's milk", "sheep's milk", "reindeer milk",
    ]},
    {"name": "cheese", "category": "lacteo", "aliases": [
        "cheese", "cheeses", "fromage", "queso", "queijo", "cottage cheese",
        "cream cheese", "curd cheese", "mascarpone", "ricotta", "mozzarella",
        "feta", "parmesan", "cheddar", "chevre", "chèvre", "cheese curd",
    ]},
    {"name": "yogurt", "category": "lacteo", "aliases": [
        "yogurt", "yoghurt", "yogur", "yoghourt", "yaourt", "jogurt", "strained yogurt",
        "greek yogurt", "yogurt culture",
    ]},
    {"name": "kefir", "category": "lacteo", "aliases": [
        "kefir", "kefir milk", "kefir grains", "water kefir",
    ]},
    {"name": "buttermilk", "category": "lacteo", "aliases": [
        "buttermilk", "babeurre", "suero de mantequilla", "buffalo buttermilk",
        "cultured buttermilk",
    ]},
    {"name": "curd", "category": "lacteo", "aliases": [
        "curd", "curds", "dahi", "quark", "sour curd", "chakka",
    ]},
    {"name": "whey", "category": "lacteo", "aliases": [
        "whey", "whey powder", "suero", "lactoserum", "lactosérum", "petit lait",
        "sheep milk whey",
    ]},
    {"name": "cream", "category": "lacteo", "aliases": [
        "cream", "crème", "creme", "crema", "sour cream", "crème fraîche",
        "creme fraiche", "heavy cream", "fresh cream", "smetana",
    ]},
    {"name": "butter", "category": "lacteo", "aliases": [
        "butter", "mantequilla", "beurre", "ghee", "yak butter", "butter oil",
        "clarified butter",
    ]},

    # --- Carnes ---
    {"name": "pork", "category": "carne", "aliases": [
        "pork", "pork meat", "pork shoulder", "pork loin", "pork belly", "pork lard",
        "lard", "pork fat", "pork rind", "swine", "pig", "pig's head", "pig head",
        "cerdo", "porc", "cochon", "jamon", "jamón", "ham", "bacon", "pancetta",
        "mangalitsa", "ground pig's head", "lean and fat pork meat",
    ]},
    {"name": "beef", "category": "carne", "aliases": [
        "beef", "beef meat", "veal", "cattle", "boeuf", "res", "vacuno",
        "beef fat", "tallow", "ground beef", "cow meat", "beef or mutton meat",
        "beef tongue", "bull blood",
    ]},
    {"name": "chicken", "category": "carne", "aliases": [
        "chicken", "pollo", "poulet", "chicken meat", "hen", "chicken entrails",
    ]},
    {"name": "poultry", "category": "carne", "aliases": [
        "poultry", "aves", "volaille", "game bird", "bird meat",
    ]},
    {"name": "lamb", "category": "carne", "aliases": [
        "lamb", "cordero", "agneau", "lamb meat", "lamb testicles", "ram testicles",
    ]},
    {"name": "mutton", "category": "carne", "aliases": [
        "mutton", "carnero", "mouton", "sheep meat", "sheep's stomach",
        "unpasteurized sheep", "mutton meat",
    ]},
    {"name": "goat", "category": "carne", "aliases": [
        "goat meat", "goat", "chevon", "cabra", "cabrito", "red goat meat",
        "buffalo or chevon meat",
    ]},
    {"name": "buffalo", "category": "carne", "aliases": [
        "buffalo meat", "buffalo", "water buffalo", "bufalo", "carabao",
        "buffalo carcasses", "buffalo meat", "ground carabao meat",
    ]},
    {"name": "duck", "category": "carne", "aliases": [
        "duck", "pato", "canard", "duck meat", "duck breast",
    ]},
    {"name": "yak", "category": "carne", "aliases": [
        "yak meat", "yak", "yak or dzo",
    ]},
    {"name": "camel", "category": "carne", "aliases": [
        "camel meat", "camel", "camel hump",
    ]},
    {"name": "venison", "category": "carne", "aliases": [
        "venison", "deer", "ciervo", "caribou",
    ]},
    {"name": "wild game", "category": "carne", "aliases": [
        "wild game", "game meat", "ostrich", "emu", "kudu", "springbok",
        "gemsbok", "muttonbird", "sooty shearwater", "walrus", "seal", "little auk",
        "wild bird",
    ]},
    {"name": "meat", "category": "carne", "aliases": [
        "meat", "carne", "viande", "chopped meat", "ground meat", "minced meat",
    ]},

    # --- Pescados y mariscos ---
    {"name": "fish", "category": "pescado", "aliases": [
        "fish", "pescado", "poisson", "fishes", "fish meat", "fresh fish",
        "freshwater fish", "saltwater fish", "whole fish", "fish fillet",
        "fish flesh", "seafood", "river fish", "sea water fish", "small fish",
        "fish entrails", "fish heads",
    ]},
    {"name": "fish sauce", "category": "pescado", "substrate": False, "aliases": [
        "fish sauce", "nuoc mam", "nam pla", "garum", "salsa de pescado",
        "sauce de poisson", "sauce poisson", "fish gravy", "fish stock",
    ]},
    {"name": "anchovy", "category": "pescado", "aliases": [
        "anchovy", "anchovies", "anchoa", "anchois", "anchovy fillet",
        "anchovy paste", "ikan bilis", "fermented salted anchovies",
        "salted anchovies", "gangetic hairfin anchovy",
    ]},
    {"name": "sardine", "category": "pescado", "aliases": [
        "sardine", "sardines", "sardina", "sardinella", "sardines sardinella",
    ]},
    {"name": "herring", "category": "pescado", "aliases": [
        "herring", "arenque", "hareng", "baltic herring", "herring roe",
        "herring or capelin",
    ]},
    {"name": "salmon", "category": "pescado", "aliases": [
        "salmon", "salmon", "salmón", "saumon", "salmon heads", "salmon roe",
    ]},
    {"name": "tuna", "category": "pescado", "aliases": [
        "tuna", "atun", "thon", "skipjack tuna", "yellowfin tuna", "bonito",
        "tuna fish", "tuna roe",
    ]},
    {"name": "mackerel", "category": "pescado", "aliases": [
        "mackerel", "caballa", "maquereau", "king mackerel", "scomber",
        "kembung", "indian mackerel", "mackerel fish", "mackerel (scomber",
    ]},
    {"name": "cod", "category": "pescado", "aliases": [
        "cod", "bacalao", "morue", "codfish", "gadus",
    ]},
    {"name": "shark", "category": "pescado", "aliases": [
        "shark", "tiburon", "requin", "greenland shark", "somniosus", "dogfish",
    ]},
    {"name": "trout", "category": "pescado", "aliases": [
        "trout", "trucha", "truite", "rainbow trout", "lake trout",
    ]},
    {"name": "tilapia", "category": "pescado", "aliases": [
        "tilapia", "tilapias", "oreochromis",
    ]},
    {"name": "catfish", "category": "pescado", "aliases": [
        "catfish", "bagre", "poisson-chat", "african sea catfish", "channel catfish",
    ]},
    {"name": "mullet", "category": "pescado", "aliases": [
        "mullet", "mujol", "mulet", "mullet fish", "sea mullet", "mullet roe",
    ]},
    {"name": "shad", "category": "pescado", "aliases": [
        "shad", "gizzard shad", "nemotolosa nasus", "sablefish",
    ]},
    {"name": "carp", "category": "pescado", "aliases": [
        "carp", "carpa", "carpe", "crucian carp", "common carp", "carassius",
    ]},
    {"name": "pollock", "category": "pescado", "aliases": [
        "pollock", "abadejo", "colin", "pollack",
    ]},
    {"name": "flounder", "category": "pescado", "aliases": [
        "flounder", "platija", "fletan", "flatfish",
    ]},
    {"name": "milkfish", "category": "pescado", "aliases": [
        "milkfish", "bangus", "chanos",
    ]},
    {"name": "gourami", "category": "pescado", "aliases": [
        "gourami", "gouramy", "snakehead", "osphronemus",
    ]},
    {"name": "skate", "category": "pescado", "aliases": [
        "skate", "skate fish", "raya", "raie", "skate wings",
    ]},
    {"name": "snakehead", "category": "pescado", "aliases": [
        "snakehead", "snake head fish",
    ]},
    {"name": "stolephorus", "category": "pescado", "aliases": [
        "stolephorus", "solephorus",
    ]},
    {"name": "roe", "category": "pescado", "aliases": [
        "roe", "fish roe", "huevas", "caviar", "bottarga",
    ]},
    {"name": "shrimp", "category": "marisco", "aliases": [
        "shrimp", "shrimps", "camaron", "camarón", "gamba", "gambas", "crevette",
        "crevettes", "tiny shrimp", "dried shrimp", "small shrimp", "potted shrimp",
        "pink shrimp",
    ]},
    {"name": "prawn", "category": "marisco", "aliases": [
        "prawn", "prawns", "langostino", "langostinos", "jumbo prawn",
    ]},
    {"name": "crab", "category": "marisco", "aliases": [
        "crab", "crabs", "cangrejo", "crabe", "crablets", "soft-shell crab",
        "mud crab", "crab meat",
    ]},
    {"name": "oyster", "category": "marisco", "aliases": [
        "oyster", "oysters", "ostra", "huitre", "huître", "oyster meat",
    ]},
    {"name": "mussel", "category": "marisco", "aliases": [
        "mussel", "mussels", "mejillon", "moule", "moules", "green mussel",
    ]},
    {"name": "clam", "category": "marisco", "aliases": [
        "clam", "clams", "almeja", "palourde", "hard clam", "soft shell clam",
    ]},
    {"name": "squid", "category": "marisco", "aliases": [
        "squid", "calamar", "calamar", "calamari", "cuttlefish", "seppia",
    ]},
    {"name": "octopus", "category": "marisco", "aliases": [
        "octopus", "pulpo", "pieuvre", "poulpe",
    ]},
    {"name": "sea urchin", "category": "marisco", "aliases": [
        "sea urchin", "erizo de mar", "oursin", "uni",
    ]},
    {"name": "sea cucumber", "category": "marisco", "aliases": [
        "sea cucumber", "pepino de mar", "trepang", "holothurian",
    ]},
    {"name": "krill", "category": "marisco", "aliases": ["krill", "antarctic krill"]},
    {"name": "shellfish", "category": "marisco", "aliases": [
        "shellfish", "marisco", "mariscos", "fruits de mer", "mollusc", "molluscs",
        "bivalve",
    ]},

    # --- Bebidas / endulzantes / otros (no sustrato) ---
    {"name": "sugar", "category": "bebida", "substrate": False, "aliases": [
        "sugar", "azúcar", "azucar", "sucre", "cane sugar", "brown sugar",
        "white sugar", "granulated sugar", "jaggery", "palm sugar", "raw sugar",
    ]},
    {"name": "sugarcane", "category": "bebida", "substrate": False, "aliases": [
        "sugar cane", "sugarcane", "sugarcane juice", "cane juice", "cana de azucar",
        "sugar cane juice", "cane", "sugarcane plant",
    ]},
    {"name": "honey", "category": "bebida", "substrate": False, "aliases": [
        "honey", "miel", "miel", "raw honey",
    ]},
    {"name": "molasses", "category": "bebida", "substrate": False, "aliases": [
        "molasses", "melaza", "melasse", "treacle",
    ]},
    {"name": "palm sap", "category": "bebida", "substrate": False, "aliases": [
        "palm sap", "toddy", "neera", "palm juice", "raffia sap", "raffia",
        "sago palm sap", "palmyra sap", "coconut palm sap",
    ]},
    {"name": "coconut sap", "category": "bebida", "substrate": False, "aliases": [
        "coconut sap", "coconut nectar", "coconut toddy", "coconut water",
        "coconut palm", "coconut sap",
    ]},
    {"name": "agave", "category": "bebida", "substrate": False, "aliases": [
        "agave", "agave sap", "agave juice", "maguey", "agave nectar",
    ]},
    {"name": "tea", "category": "bebida", "substrate": False, "aliases": [
        "tea", "té", "te", "tè", "tea leaves", "green tea", "black tea",
        "camellia", "camellia sinensis", "camellia leaves", "linden blossom",
        "fermented tea", "tea leaf", "pawpaw leaf", "sodom apple leaf",
    ]},
    {"name": "coffee", "category": "bebida", "substrate": False, "aliases": [
        "coffee", "café", "cafe", "coffee grounds", "coffee beans", "coffee cherry",
    ]},
    {"name": "cocoa", "category": "bebida", "substrate": False, "aliases": [
        "cocoa", "cacao", "cocoa bean", "cocoa beans", "cocoa pod", "chocolate",
        "cacao bean", "cocoa pulp", "cocoa powder",
    ]},
    {"name": "wine", "category": "bebida", "substrate": False, "aliases": [
        "wine", "vino", "vin", "white wine", "red wine", "grappa",
    ]},
    {"name": "hops", "category": "bebida", "substrate": False, "aliases": [
        "hops", "hop", "lupulo", "lúpulo", "houblon", "humulus",
    ]},
    {"name": "vinegar", "category": "bebida", "substrate": False, "aliases": [
        "vinegar", "vinagre", "vinaigre", "aceto", "balsamic vinegar",
        "apple cider vinegar", "cider vinegar", "wine vinegar", "rice vinegar",
        "sherry vinegar", "malt vinegar", "white vinegar", "red wine vinegar",
        "white wine vinegar",
    ]},
    {"name": "juice", "category": "bebida", "substrate": False, "aliases": [
        "juice", "jugo", "jus", "fruit juice", "vegetable juice",
    ]},
    {"name": "oil", "category": "bebida", "substrate": False, "aliases": [
        "oil", "huile", "aceite", "olio", "olive oil", "palm oil", "sunflower oil",
        "vegetable oil", "sesame oil", "coconut oil", "rapeseed oil",
        "hydrogenated oil", "vanaspati", "mustard oil",
    ]},
    {"name": "salt", "category": "otro", "substrate": False, "aliases": [
        "salt", "sel", "sal", "sea salt", "rock salt", "kosher salt", "table salt",
        "curing salt", "pickling salt", "himalayan salt", "salted",
    ]},
    {"name": "water", "category": "otro", "substrate": False, "aliases": [
        "water", "agua", "eau", "mineral water", "spring water", "salt water",
        "brine", "limewater", "rice water",
    ]},
    {"name": "spices", "category": "otro", "substrate": False, "aliases": [
        "spices", "especias", "epices", "spice mix", "mixed spices", "spice blend",
        "spiced", "spice",
    ]},
    {"name": "herbs", "category": "otro", "substrate": False, "aliases": [
        "herbs", "hierbas", "herbes", "herbes de provence", "fresh herbs",
        "wild herbs", "seasonal herbs", "sometimes herbs",
    ]},
    {"name": "turmeric", "category": "otro", "substrate": False, "aliases": [
        "turmeric", "curcuma", "cúrcuma", "turmeric powder", "turmeric root",
    ]},
    {"name": "cumin", "category": "otro", "substrate": False, "aliases": [
        "cumin", "comino", "cumin seeds", "jeera",
    ]},
    {"name": "coriander", "category": "otro", "substrate": False, "aliases": [
        "coriander", "cilantro", "coriandre", "coriander seeds", "coriander leaves",
    ]},
    {"name": "fennel", "category": "otro", "substrate": False, "aliases": [
        "fennel", "hinojo", "fenouil", "fennel seeds", "fennel bulb",
    ]},
    {"name": "cinnamon", "category": "otro", "substrate": False, "aliases": [
        "cinnamon", "canela", "cannelle", "cinnamon bark", "cinnamon sticks",
    ]},
    {"name": "cloves", "category": "otro", "substrate": False, "aliases": [
        "clove", "cloves", "clavo", "clou de girofle", "clove buds",
    ]},
    {"name": "nutmeg", "category": "otro", "substrate": False, "aliases": [
        "nutmeg", "nuez moscada", "noix de muscade", "mace",
    ]},
    {"name": "black pepper", "category": "otro", "substrate": False, "aliases": [
        "black pepper", "pimienta negra", "poivre noir", "peppercorn", "peppercorns",
        "ground pepper",
    ]},
    {"name": "cardamom", "category": "otro", "substrate": False, "aliases": [
        "cardamom", "cardamomo", "cardamom pods", "elaichi",
    ]},
    {"name": "caraway", "category": "otro", "substrate": False, "aliases": [
        "caraway", "alcaravea", "caraway seeds",
    ]},
    {"name": "bay leaf", "category": "otro", "substrate": False, "aliases": [
        "bay leaf", "bay leaves", "laurel", "hoja de laurel",
    ]},
    {"name": "yeast", "category": "hongo", "substrate": False, "aliases": [
        "yeast", "levadura", "levure", "brewer's yeast", "nutritional yeast",
        "bakers yeast", "yeast extract",
    ]},
    {"name": "koji", "category": "hongo", "substrate": False, "aliases": [
        "koji", "koji rice", "koji mold", "koji starter", "aspergillus oryzae",
    ]},
    {"name": "egg", "category": "otro", "substrate": False, "aliases": [
        "egg", "eggs", "huevo", "huevos", "oeuf", "œuf", "egg yolk", "egg white",
        "duck egg", "quail egg",
    ]},
    {"name": "vegetable oil", "category": "bebida", "substrate": False, "aliases": [
        "vegetable oil", "huile végétale", "aceite vegetal",
    ]},
]

_SUBSTRATE_PRIORITY = {
    "legumbre": 10,
    "cereal": 20,
    "raiz": 30,
    "vegetal": 40,
    "fruta": 50,
    "hongo": 60,
    "lacteo": 70,
    "pescado": 80,
    "marisco": 90,
    "carne": 100,
}


def _fold(text: str) -> str:
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    return text.lower()


def _build_patterns():
    patterns = []
    seen = set()
    for entry in CANONICAL_INGREDIENTS:
        for alias in entry["aliases"]:
            folded = _fold(alias)
            if len(folded) < 3:
                continue
            if folded in seen:
                continue
            seen.add(folded)
            patterns.append(
                (entry, re.compile(rf"(?<![a-z0-9]){re.escape(folded)}(?![a-z0-9])"))
            )
    return patterns


_PATTERNS = _build_patterns()


def match_ingredients(text: str) -> list[dict]:
    if not text:
        return []
    t = _fold(text)
    spans = []
    for entry, pattern in _PATTERNS:
        for m in pattern.finditer(t):
            spans.append((m.start(), m.end(), entry))
    if not spans:
        return []
    spans.sort(key=lambda s: (s[0], -(s[1] - s[0])))
    kept = []
    for start, end, entry in spans:
        if kept and start < kept[-1][1]:
            continue
        kept.append((start, end, entry))
    out = []
    seen = set()
    for _start, _end, entry in kept:
        if entry["name"] in seen:
            continue
        seen.add(entry["name"])
        out.append({"name": entry["name"], "category": entry["category"]})
    return out


def pick_substrate(ingredients: list[dict]) -> str | None:
    best = None
    best_priority = None
    for item in ingredients:
        priority = _SUBSTRATE_PRIORITY.get(item.get("category"))
        if priority is None:
            continue
        if best_priority is None or priority < best_priority:
            best = item["name"]
            best_priority = priority
    return best
