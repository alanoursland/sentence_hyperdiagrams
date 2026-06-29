"""Build the Reed-Kellogg POS vocabulary from tokenized datasets.

Extracts unique tokens, auto-classifies closed classes and applies
suffix heuristics, then writes ontology/reed_kellogg_pos.yaml.
"""

from collections import Counter
from pathlib import Path

from parts_of_thought.diagram import parse_tokens_file

TOKENIZED_DIR = Path("diagrams/tokenized")
OUTPUT_PATH = Path("ontology/reed_kellogg_pos.yaml")

SOURCES = [
    "mcguffey_primer",
    "mcguffey_first_reader",
    "beacon_second_reader",
    "fifty_famous_stories",
]

# ---- Closed-class dictionaries ----

PUNCT_TOKENS = {".", ",", "!", "?", ";", ":"}

ARTICLES = {"the", "a", "an"}

CONJUNCTIONS = {
    "and", "but", "or", "nor", "than",
    "because", "although", "though", "unless", "whether",
    "if", "when", "while", "whereas",
}

PREPOSITIONS = {
    "of", "to", "in", "on", "at", "by", "from", "with",
    "into", "upon", "through", "between", "among", "above",
    "under", "below", "behind", "beside", "besides", "across",
    "along", "around", "against", "toward", "towards",
    "within", "without", "except", "until", "during",
    "near", "past", "beyond",
}

PRONOUNS = {
    # Personal subject
    "i", "you", "he", "she", "it", "we", "they",
    # Personal object
    "me", "him", "her", "us", "them",
    # Possessive (pronoun form)
    "mine", "yours", "his", "hers", "ours", "theirs",
    # Possessive (adjective form -- Reed-Kellogg treats as pronoun)
    "my", "your", "our", "their", "its",
    # Demonstrative
    "this", "these", "those",
    # Relative / interrogative
    "who", "whom", "whose", "which",
    # Reflexive
    "myself", "yourself", "himself", "herself", "itself",
    "ourselves", "themselves",
    # Indefinite
    "everybody", "nobody", "somebody", "anybody",
    "everyone", "someone", "anyone", "no one",
    "everything", "something", "anything", "nothing",
    "whoever", "whatever",
    "each", "other", "another",
    "none", "both",
}

ADVERBS = {
    "not", "never", "always", "ever", "often",
    "now", "then", "soon", "already", "still", "yet",
    "here", "there", "where", "everywhere", "nowhere",
    "very", "too", "quite", "almost", "rather", "just",
    "also", "again", "away", "back",
    "how", "why",
    "ago", "sometimes", "forth", "else", "forward",
    "somewhere", "yesterday", "tomorrow", "tonight",
    "outdoors", "outside", "inside", "halfway",
    "thus", "outright", "afterward",
}

INTERJECTIONS = {
    "oh", "ah", "alas", "hurrah", "lo", "hark",
    "hush", "pooh", "bravo", "please",
}

# ---- Open-class dictionaries ----
# These cover words from our datasets that aren't caught by
# closed classes, suffix heuristics, or proper noun detection.

VERBS = {
    # Be-forms
    "am", "is", "are", "was", "were", "be", "been",
    # Have-forms
    "have", "has", "had",
    # Do-forms
    "do", "did", "does", "done",
    # Modals
    "can", "could", "will", "would", "shall", "should",
    "may", "might", "must", "ought", "cannot", "dare",
    # Common irregular verbs (past tense / past participle)
    "came", "went", "ran", "saw", "knew", "began", "took", "told",
    "heard", "stood", "sat", "gave", "fell", "grew", "spoke", "kept",
    "held", "got", "said", "blew", "flew", "rode", "sprang", "hid",
    "forgot", "met", "threw", "felt", "awoke", "bought", "caught",
    "shook", "arose", "slept", "struck", "became", "drew", "crept",
    "swam", "bent", "spun", "stole", "drove", "sang", "rang", "swung",
    "froze", "woke", "wrote", "won", "sank", "laid", "hung", "fed",
    "let", "put", "cut", "set", "shut", "hit", "hurt", "spread",
    "sent", "spent", "meant", "built", "shot", "fought", "sought",
    "taught", "spat", "wept", "swept", "fled", "clung",
    "gone", "seen", "taken", "given", "fallen", "broken", "grown",
    "blown", "flown", "worn", "driven", "beaten", "chosen", "stolen",
    "frozen", "written", "spoken", "hidden", "bidden",
    "overtook", "foretold", "bade",
    # Common base verbs (short, no suffix heuristic)
    "see", "come", "get", "go", "think", "take", "make", "hear",
    "find", "tell", "know", "say", "eat", "send", "die", "join",
    "wait", "speak", "read", "cry", "stop", "want", "buy",
    "shout", "drown", "obey", "reach", "try",
    "rob", "laugh", "skip", "trot", "hoist", "spoil", "thank",
    "shake", "chew", "guess", "learn", "choose", "fail",
    "punish", "raise", "belong", "roar", "burn", "roast", "teach",
    "hate", "warn", "drop", "beat", "sell", "sail", "earn",
    "change", "feel", "grow", "seek", "stir", "leap",
    "deal", "treat", "droop", "drown", "sew", "throw", "kiss",
    "buzz", "kill", "pull", "sit", "peep", "stay", "dares",
    "lose", "leave", "move", "spin", "save", "ask", "swim",
    "hunt", "hang", "pay", "blow", "dig",
    "draw", "ride", "walk", "call", "drink", "catch", "keep",
    "hold", "fly", "sleep", "give", "run", "play",
    "listen", "hope", "wish", "help", "look", "watch",
    "carry", "talk", "fight", "show", "dance", "touch",
    "turn", "pass", "cook", "use", "rise", "start",
    "spare", "lie", "disobey", "blend", "break",
    "arrange", "escape", "sink", "manage", "persuade",
    "believe", "understand", "marry", "frighten", "march",
    "sprinkle", "strike", "fasten", "obey", "cross",
    "whistle", "forget", "become", "climb",
    # Verb forms (3rd person -s, not caught by suffix rules)
    "sees", "comes", "goes", "does", "sits", "gives", "holds",
    "likes", "stands", "reads", "feels", "says", "makes",
    "seems", "follows", "precedes", "combines", "contains",
    "keeps", "takes", "looks", "calls", "tells", "asks",
    "walks", "drives", "rides", "shines", "wears",
    "thinks", "draws", "hangs", "sleeps", "rests",
    "dares", "knows", "owns", "loves", "fails",
    "jumps", "drops", "belongs", "trembles", "quivers",
    "whistles", "strikes", "starves",
    # Misc verb forms found in corpus
    "sup", "hoe",
    # Additional irregular pasts / participles missed above
    "made", "found", "brought", "sold", "shone", "eaten", "stung",
    "lay",
    # Additional base verbs
    "jump", "stand", "fall", "lead", "meet", "return", "wake",
    "tremble", "wear", "seem", "whisk", "flap", "coil", "gain",
    "roll", "mount", "cheat", "stray", "waste", "occur",
    "pat", "aim",
    # Additional 3rd person forms
    "flies", "cries", "shouts", "sounds",
}

NOUNS = {
    # People
    "man", "men", "boy", "boys", "girl", "girls", "child", "children",
    "woman", "women", "baby", "people", "friend", "friends",
    "son", "daughter", "daughters", "wife", "widow",
    "mamma", "papa", "grandma", "grandpa", "parents",
    "kids", "tots", "sisters", "brothers",
    "lady", "fellow", "fellows", "lad", "maiden",
    "prince", "princess", "queen", "king", "kings",
    "lord", "captain", "sir", "beggar", "servant", "servants",
    "soldier", "soldiers", "warrior", "horsemen", "officers",
    "shepherd", "sheriff", "abbot", "bride", "slave",
    "tyrant", "rascal", "fools", "enemies", "foes",
    "crew", "crowd", "party", "guests", "robbers",
    # Animals
    "dog", "dogs", "cat", "hen", "rat", "rats", "bird", "birds",
    "pig", "horse", "horses", "goat", "goats", "cow", "cows",
    "donkey", "owl", "wolf", "fox", "duck", "ducks",
    "frog", "fish", "sheep", "lamb", "lambs", "mouse", "mice",
    "geese", "quail", "chick", "chickens", "rabbits",
    "eagle", "hawk", "lion", "dove", "doves", "worm",
    "hounds", "bees", "locusts",
    # Body parts
    "hand", "hands", "head", "heads", "eyes", "ears", "ear",
    "foot", "feet", "mouth", "mouths", "neck", "hair",
    "heart", "lips", "legs", "leg", "toes", "fingers",
    "thumb", "breast", "cheek", "cheeks", "wrist",
    "forehead", "paw", "bill", "tail", "tails",
    "wings", "feathers", "limbs",
    # Places
    "home", "homes", "house", "houses", "door", "doors",
    "room", "barn", "school", "church", "castle", "palace",
    "town", "city", "cities", "village", "country", "countries",
    "kingdom", "street", "streets", "road", "roadside",
    "farm", "farms", "yard", "garden", "gardens",
    "cabin", "cabins", "huts", "camp", "prison",
    "schoolhouse", "schoolroom", "attic", "kitchen",
    "hall", "lighthouse", "mill", "farmyard",
    "seaside", "mountain", "mountains", "valley",
    # Nature
    "sun", "moon", "sky", "air", "wind", "rain",
    "snow", "ice", "fire", "sea", "ocean",
    "pond", "brook", "stream", "beach", "shore",
    "rock", "rocks", "stone", "stones", "sand",
    "tree", "trees", "grass", "woods", "wood",
    "field", "hill", "hills", "cave",
    "forest", "forests", "swamps", "plains",
    # Objects
    "bell", "ship", "ships", "boat", "box", "hat", "cap",
    "cup", "ball", "bed", "beds", "chair", "chairs",
    "book", "books", "pen", "flag", "flags", "rope",
    "lamp", "whip", "cage", "pan", "fan", "mat",
    "doll", "dolls", "basket", "clock", "wagon", "cart",
    "bag", "bags", "key", "knife", "ax", "wheel",
    "straw", "sword", "swords", "spade", "spindle", "spindles",
    "sticks", "beams", "beam", "log", "logs",
    "thread", "needle", "needles", "rags",
    "pipe", "kite", "tub", "pole", "oar", "oars",
    "tent", "crown", "gown", "robe", "cloak",
    "skates", "shoes", "glasses", "wig",
    "table", "tables", "desk", "stove", "cradle",
    "gate", "gates", "wall", "walls", "roof",
    "stairs", "stair", "floor", "window",
    "seat", "bench", "shelf",
    "shield", "shields", "armor", "spear", "spears",
    "arrow", "arrows", "bow", "bows", "gun", "guns",
    "horn", "trap", "hook", "chain", "lock",
    "ticket", "penny", "money",
    "pail", "flask", "lantern", "carpet",
    "collar", "handkerchief", "curtain",
    "reins", "masts", "sails", "deck", "buoy",
    "ladder", "ladders", "post", "posts",
    "crib", "rings", "slates", "crackers",
    "board", "hedge",
    # Food/drink
    "bread", "meat", "milk", "eggs", "apple", "apples",
    "gold", "honey", "corn", "cakes", "flour",
    "wine", "potato", "cherry", "figs", "peas", "raisins",
    "sauce", "food", "breakfast", "feast",
    # Abstract nouns
    "day", "days", "night", "time", "times", "year", "years",
    "way", "ways", "name", "names", "word", "words",
    "story", "place", "places", "world", "life", "lives",
    "side", "sides", "line", "lines", "joy",
    "news", "course", "mind", "minds", "song",
    "noise", "sound", "voice",
    "death", "fear", "care", "love", "shame",
    "truth", "honor", "wisdom", "courage", "faith",
    "peace", "war", "battle", "battles",
    "trouble", "fright", "haste", "luck",
    "justice", "liberty", "beauty", "music",
    "age", "sport", "fun", "trick", "game",
    "art", "skill", "form", "habit",
    "sight", "picture", "shade", "spot",
    "piece", "pieces", "bit", "bits", "part", "parts",
    "gift", "jewels", "gems", "riches", "treasure", "treasures",
    "wealth", "prize", "profit",
    "deeds", "plans", "points", "letters", "figures",
    "kinds", "things", "stuff", "objects",
    "step", "steps", "minute", "minutes",
    "hour", "week", "month", "chance", "risk",
    "mark", "crack", "loss", "harm", "envy",
    "smoke", "storm", "mist", "fog",
    "breeze", "waves", "flames", "blossoms",
    "dust", "dirt", "pile", "pit",
    "voyage", "journey", "errand",
    "web", "vine", "stem", "branches", "leaves",
    "strips", "birch", "thorn",
    "moss", "bushes", "bush",
    "hives", "basin", "puddle",
    "consonants", "vowel", "vowels", "suffixes", "prefixes",
    "sayings", "cinders", "combinations",
    "families", "cattle",
    "face", "shadow", "statue", "tap",
    "front", "top", "ground", "bank",
    "band", "clubs", "list", "sets",
    "land", "lands", "bridge", "plant",
    "cares", "sake", "deal", "peril", "worth",
    "length", "midst", "wrongs",
    "promise", "use",
    "gig", "jig", "nag", "peg", "pet",
    "hearth", "sill", "washtub", "oven",
    "sunset", "beads", "globe",
    "grapevine", "tomahawks",
    "tobacco", "scarlet",
    "hatchet", "lute", "kettledrum",
    "cane", "pocket", "speck",
    "pavements", "fastenings",
    "wretch", "office", "market",
    "tale", "heir", "rule",
    "tusk", "trunk", "senses",
    "directions", "metals",
    "basin", "plenty",
    "fever", "toll",
    "cock", "barn",
    "cabin", "stir",
    "easy-chair", "stone-yard", "flag-ship",
    "horse-hairs", "ice-bergs",
    "playmates", "raindrops",
    # Proper-ish nouns (appear lowercase in corpus)
    "fairy", "fairies",
    "giant",
    # Additional nouns missed in first pass
    "army", "arms", "flowers", "birdie", "dress", "cars",
    "clothes", "puss", "train", "attack", "bark", "crash",
    "shells", "heaven", "judges", "judge", "noon", "failure",
    "creatures", "dishes", "elves", "features", "glass", "glee",
    "guards", "miles", "person", "pair", "pairs", "nut",
    "bay", "beehives", "shop", "size", "soil", "tears",
    "thousands", "tide", "wreaths", "cost", "joke", "pleasure",
    "notice", "plan", "east", "doubt", "smile", "clang",
    "pitch", "aid", "spell", "search", "thirst", "winds",
    "bakers", "vessel",
}

ADJECTIVES = {
    # Common short adjectives
    "little", "great", "old", "good", "big", "new", "long",
    "poor", "black", "dear", "fine", "young", "full",
    "happy", "afraid", "wise", "brave", "pretty", "white",
    "sad", "hot", "sweet", "glad", "strong", "angry",
    "ready", "nice", "lazy", "safe", "dark", "wide", "rich",
    "blind", "dead", "merry", "short", "sure", "yellow",
    "pale", "few", "foolish", "free", "cool", "funny",
    "hungry", "tall", "small", "large", "bright", "tiny",
    "dirty", "cold", "strange", "heavy", "golden", "deep",
    "gentle", "soft", "quiet", "rainy", "wild", "cruel",
    "common", "loud", "simple", "huge", "bold", "firm",
    "scarlet", "noble", "sharp", "ill", "rough", "smooth",
    "swift", "narrow", "plain", "handsome", "single",
    "certain", "different", "distant", "pleasant",
    "easy", "busy", "proud", "polite", "sorry", "lame",
    "sick", "low", "neat", "clean", "bare", "fond",
    "idle", "sticky", "greedy", "shiny", "solid",
    "fresh", "late", "exact", "saucy", "dreary",
    "loose", "weary", "green", "gray", "blue", "brown",
    "wet", "tight", "crisp", "rusty", "whole", "wooden",
    "straight", "prudent", "fat", "asleep",
    # Additional adjectives missed in first pass
    "true", "dry", "warm", "quick", "fair", "same",
    "wealthy", "worthy", "rid", "ablaze", "ashy", "unbroken",
    "awake", "yon",
    "such", "every",
    "pure", "dusty", "stormy", "terrific",
    "thirsty", "flowery", "glassy", "shallow", "grassy",
    "unkind", "hempen", "worn-out", "far-off",
    # Ordinals
    "first", "second", "third", "sixth", "seventh",
    "twelfth", "thirteenth",
    # Numerals (function as adjectives in R-K)
    "two", "three", "four", "six", "seven", "eight",
    "twelve", "sixteen", "thirty", "thousand",
}

# ---- Ambiguous words (with weights) ----

AMBIGUOUS: dict[str, list[tuple[str, float]]] = {
    "that": [("PRONOUN", 0.5), ("CONJUNCTION", 0.5)],
    "what": [("PRONOUN", 0.7), ("INTERJECTION", 0.3)],
    "for": [("PREPOSITION", 0.7), ("CONJUNCTION", 0.3)],
    "so": [("ADVERB", 0.6), ("CONJUNCTION", 0.4)],
    "as": [("ADVERB", 0.4), ("CONJUNCTION", 0.3), ("PREPOSITION", 0.3)],
    "before": [("PREPOSITION", 0.5), ("CONJUNCTION", 0.3), ("ADVERB", 0.2)],
    "after": [("PREPOSITION", 0.6), ("CONJUNCTION", 0.4)],
    "since": [("PREPOSITION", 0.4), ("CONJUNCTION", 0.4), ("ADVERB", 0.2)],
    "down": [("ADVERB", 0.6), ("PREPOSITION", 0.4)],
    "up": [("ADVERB", 0.6), ("PREPOSITION", 0.4)],
    "out": [("ADVERB", 0.6), ("PREPOSITION", 0.4)],
    "off": [("ADVERB", 0.6), ("PREPOSITION", 0.4)],
    "over": [("PREPOSITION", 0.5), ("ADVERB", 0.5)],
    "about": [("PREPOSITION", 0.6), ("ADVERB", 0.4)],
    "like": [("VERB", 0.4), ("PREPOSITION", 0.3), ("ADJECTIVE", 0.3)],
    "well": [("ADVERB", 0.5), ("INTERJECTION", 0.3), ("NOUN", 0.2)],
    "right": [("ADJECTIVE", 0.4), ("ADVERB", 0.3), ("NOUN", 0.3)],
    "no": [("ADVERB", 0.5), ("ADJECTIVE", 0.5)],
    "yes": [("INTERJECTION", 0.5), ("ADVERB", 0.5)],
    "once": [("ADVERB", 0.6), ("CONJUNCTION", 0.4)],
    "only": [("ADVERB", 0.6), ("ADJECTIVE", 0.4)],
    "even": [("ADVERB", 0.6), ("ADJECTIVE", 0.4)],
    "much": [("ADVERB", 0.5), ("ADJECTIVE", 0.5)],
    "more": [("ADVERB", 0.5), ("ADJECTIVE", 0.5)],
    "most": [("ADVERB", 0.5), ("ADJECTIVE", 0.5)],
    "all": [("ADJECTIVE", 0.5), ("PRONOUN", 0.3), ("ADVERB", 0.2)],
    "some": [("ADJECTIVE", 0.5), ("PRONOUN", 0.5)],
    "many": [("ADJECTIVE", 0.5), ("PRONOUN", 0.5)],
    "one": [("PRONOUN", 0.5), ("ADJECTIVE", 0.3), ("NOUN", 0.2)],
    # Verb/Noun ambiguity
    "work": [("NOUN", 0.5), ("VERB", 0.5)],
    "thought": [("NOUN", 0.5), ("VERB", 0.5)],
    "light": [("NOUN", 0.4), ("ADJECTIVE", 0.3), ("VERB", 0.3)],
    "rose": [("VERB", 0.5), ("NOUN", 0.5)],
    "bear": [("VERB", 0.5), ("NOUN", 0.5)],
    "left": [("VERB", 0.4), ("ADJECTIVE", 0.3), ("NOUN", 0.3)],
    "last": [("ADJECTIVE", 0.6), ("VERB", 0.2), ("ADVERB", 0.2)],
    "open": [("ADJECTIVE", 0.5), ("VERB", 0.5)],
    "own": [("ADJECTIVE", 0.5), ("VERB", 0.5)],
    "lost": [("VERB", 0.5), ("ADJECTIVE", 0.5)],
    "cross": [("VERB", 0.4), ("ADJECTIVE", 0.3), ("NOUN", 0.3)],
    "mean": [("VERB", 0.5), ("ADJECTIVE", 0.5)],
    "round": [("ADJECTIVE", 0.4), ("ADVERB", 0.3), ("PREPOSITION", 0.3)],
    "upset": [("ADJECTIVE", 0.6), ("VERB", 0.4)],
    "bound": [("ADJECTIVE", 0.5), ("VERB", 0.5)],
    "worn": [("VERB", 0.5), ("ADJECTIVE", 0.5)],
    "wrong": [("ADJECTIVE", 0.5), ("NOUN", 0.3), ("ADVERB", 0.2)],
    "close": [("ADJECTIVE", 0.4), ("VERB", 0.4), ("ADVERB", 0.2)],
    "present": [("NOUN", 0.4), ("ADJECTIVE", 0.4), ("VERB", 0.2)],
    # Adjective/Adverb ambiguity
    "fast": [("ADJECTIVE", 0.5), ("ADVERB", 0.5)],
    "far": [("ADVERB", 0.5), ("ADJECTIVE", 0.5)],
    "next": [("ADJECTIVE", 0.5), ("ADVERB", 0.5)],
    "hard": [("ADJECTIVE", 0.6), ("ADVERB", 0.4)],
    "high": [("ADJECTIVE", 0.6), ("ADVERB", 0.4)],
    "alone": [("ADJECTIVE", 0.5), ("ADVERB", 0.5)],
    "worse": [("ADJECTIVE", 0.6), ("ADVERB", 0.4)],
    "worst": [("ADJECTIVE", 0.6), ("ADVERB", 0.4)],
    "least": [("ADJECTIVE", 0.5), ("ADVERB", 0.5)],
    # Adjective/Noun ambiguity
    "any": [("ADJECTIVE", 0.5), ("PRONOUN", 0.5)],
    "half": [("NOUN", 0.5), ("ADJECTIVE", 0.5)],
    # Noun/Adjective/Verb
    "home": [("NOUN", 0.6), ("ADVERB", 0.4)],
    "gold": [("NOUN", 0.7), ("ADJECTIVE", 0.3)],
    "magic": [("NOUN", 0.5), ("ADJECTIVE", 0.5)],
    "instant": [("NOUN", 0.6), ("ADJECTIVE", 0.4)],
    "goody": [("NOUN", 0.6), ("INTERJECTION", 0.4)],
    # Contractions / special forms
    "'twould": [("VERB", 1.0)],
    "to-day": [("ADVERB", 0.5), ("NOUN", 0.5)],
    "to-night": [("ADVERB", 0.5), ("NOUN", 0.5)],
    "up-stairs": [("ADVERB", 0.6), ("NOUN", 0.4)],
    "every-where": [("ADVERB", 1.0)],
    "along-side": [("ADVERB", 0.5), ("PREPOSITION", 0.5)],
    "through-out": [("PREPOSITION", 0.5), ("ADVERB", 0.5)],
    "after-ward": [("ADVERB", 1.0)],
    "wom-an": [("NOUN", 1.0)],
    "chil-dren": [("NOUN", 1.0)],
    "war-rior": [("NOUN", 1.0)],
    "no-body--no": [("PRONOUN", 1.0)],
    "twelve--one": [("ADJECTIVE", 1.0)],
    "des-sert": [("NOUN", 1.0)],
    "your-self": [("PRONOUN", 1.0)],
    "ill-doers": [("NOUN", 1.0)],
    "'what": [("PRONOUN", 1.0)],
    # Verb/interjection
    "come": [("VERB", 0.8), ("INTERJECTION", 0.2)],
    # Misc
    "staid": [("VERB", 0.6), ("ADJECTIVE", 0.4)],
    "drill": [("NOUN", 0.5), ("VERB", 0.5)],
    "clear": [("ADJECTIVE", 0.5), ("VERB", 0.3), ("ADVERB", 0.2)],
    "kind": [("NOUN", 0.5), ("ADJECTIVE", 0.5)],
    "count": [("VERB", 0.5), ("NOUN", 0.5)],
    "act": [("NOUN", 0.5), ("VERB", 0.5)],
}

# ---- Suffix heuristics ----

SUFFIX_RULES: list[tuple[str, str]] = [
    ("ly", "ADVERB"),
    ("ing", "VERB"),
    ("ed", "VERB"),
    ("tion", "NOUN"),
    ("sion", "NOUN"),
    ("ment", "NOUN"),
    ("ness", "NOUN"),
    ("ful", "ADJECTIVE"),
    ("ous", "ADJECTIVE"),
    ("ive", "ADJECTIVE"),
    ("able", "ADJECTIVE"),
    ("ible", "ADJECTIVE"),
    ("less", "ADJECTIVE"),
    ("est", "ADJECTIVE"),
    ("er", "NOUN"),
]


def extract_tokens() -> tuple[Counter, dict[str, set[str]]]:
    """Extract all tokens from tokenized files.

    Returns (lowercase_counts, lowercase_to_forms).
    """
    counts: Counter = Counter()
    forms: dict[str, set[str]] = {}

    for source in SOURCES:
        path = TOKENIZED_DIR / f"{source}.txt"
        annotations = parse_tokens_file(path)
        for ann in annotations:
            lower = ann.token.lower()
            counts[lower] += 1
            forms.setdefault(lower, set()).add(ann.token)

    return counts, forms


def classify_token(
    word: str, word_forms: set[str], all_forms: dict[str, set[str]],
) -> list[tuple[str, float]] | None:
    """Classify a word into POS tag(s) with weights.

    Returns list of (POS, weight) tuples, or None if unclassified.
    """
    # Punctuation.
    if word in PUNCT_TOKENS:
        return [("PUNCT", 1.0)]

    # Ambiguous (checked before closed classes to override).
    if word in AMBIGUOUS:
        return AMBIGUOUS[word]

    # Closed classes.
    if word in ARTICLES:
        return [("ARTICLE", 1.0)]
    if word in CONJUNCTIONS:
        return [("CONJUNCTION", 1.0)]
    if word in PREPOSITIONS:
        return [("PREPOSITION", 1.0)]
    if word in PRONOUNS:
        return [("PRONOUN", 1.0)]
    if word in ADVERBS:
        return [("ADVERB", 1.0)]
    if word in INTERJECTIONS:
        return [("INTERJECTION", 1.0)]

    # Open classes (manually curated for our datasets).
    if word in VERBS:
        return [("VERB", 1.0)]
    if word in NOUNS:
        return [("NOUN", 1.0)]
    if word in ADJECTIVES:
        return [("ADJECTIVE", 1.0)]

    # Contractions.
    if word.endswith("n't"):
        return [("VERB", 1.0)]
    if any(word.endswith(s) for s in ("'m", "'re", "'ve", "'ll", "'d")):
        return [("VERB", 1.0)]

    # Keep possessive forms whole for now. In RK terms they remain possessive
    # nouns by form, while functioning adjectivally before the following noun.
    if word.endswith("'s") or word.endswith("s'"):
        return [("ADJECTIVE", 1.0), ("POSSESSIVE_NOUN", 1.0)]

    # Proper noun detection: only appears capitalized.
    if all(f[0].isupper() for f in word_forms) and word[0].isalpha():
        # Check it's not a common word that just happens to start sentences.
        # If a word ONLY ever appears capitalized, it's likely proper.
        return [("NOUN", 1.0)]

    # Suffix heuristics (only for longer words to avoid false positives).
    if len(word) >= 4:
        for suffix, pos in SUFFIX_RULES:
            if word.endswith(suffix):
                return [(pos, 1.0)]

    return None


def build_vocabulary() -> dict[str, list[tuple[str, float]]]:
    """Build the complete vocabulary mapping."""
    counts, forms = extract_tokens()
    vocab: dict[str, list[tuple[str, float]]] = {}

    for word in sorted(counts.keys()):
        result = classify_token(word, forms[word], forms)
        if result is not None:
            vocab[word] = result

    return vocab


def write_yaml(
    vocab: dict[str, list[tuple[str, float]]],
    counts: Counter,
    path: Path,
) -> None:
    """Write the vocabulary to YAML."""
    lines: list[str] = [
        "# Reed-Kellogg POS Vocabulary",
        "# Maps each word (lowercase) to its possible POS tags.",
        "# Ambiguous words have explicit weights (should sum to 1.0).",
        "#",
        "# Generated by scripts/build_pos_vocab.py",
        "# Edit manually to add/correct POS tags.",
        "",
    ]

    # Words that YAML interprets as booleans or other special values.
    yaml_special = PUNCT_TOKENS | {
        "on", "off", "yes", "no", "true", "false",
        "y", "n", "null",
    }

    for word, tags in sorted(vocab.items(), key=lambda kv: -counts[kv[0]]):
        needs_quoting = word in yaml_special or "'" in word or word.startswith("-")
        key = f'"{word}"' if needs_quoting else word
        lines.append(f"{key}:")
        for pos, weight in tags:
            if weight == 1.0:
                lines.append(f"  - {pos}")
            else:
                lines.append(f"  - {pos}: {weight}")

    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def print_stats(
    vocab: dict[str, list[tuple[str, float]]],
    total_unique: int,
) -> None:
    """Print classification statistics."""
    classified = len(vocab)
    ambiguous = sum(1 for tags in vocab.values() if len(tags) > 1)
    unambiguous = classified - ambiguous

    by_pos: Counter = Counter()
    for tags in vocab.values():
        for pos, _ in tags:
            by_pos[pos] += 1

    print(f"Total unique tokens: {total_unique}")
    print(f"Classified: {classified}")
    print(f"  Unambiguous: {unambiguous}")
    print(f"  Ambiguous (weighted): {ambiguous}")
    print(f"  Unclassified: {total_unique - classified}")
    print()
    print("By POS tag:")
    for pos, count in by_pos.most_common():
        print(f"  {pos}: {count}")


def main() -> None:
    counts, forms = extract_tokens()
    vocab: dict[str, list[tuple[str, float]]] = {}

    for word in sorted(counts.keys()):
        result = classify_token(word, forms[word], forms)
        if result is not None:
            vocab[word] = result

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    write_yaml(vocab, counts, OUTPUT_PATH)
    print_stats(vocab, len(counts))
    print(f"\nWrote {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
