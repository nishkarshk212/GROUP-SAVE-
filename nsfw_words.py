# NSFW Word List Database
# This file contains categories of inappropriate words for detection

# Leet speak character mapping (numbers/symbols to letters)
LEET_SPEAK_MAP = {
    '0': 'o', '1': 'i', '2': 'z', '3': 'e', '4': 'a', 
    '5': 's', '6': 'g', '7': 't', '8': 'b', '9': 'g',
    '@': 'a', '$': 's', '!': 'i', '*': 'x', '+': 't',
    '<': 'c', '>': 'c', '(': 'c', '|': 'l'
}

# Regex patterns for NSFW detection
NSFW_PATTERNS = [
    r"\bsex\b",
    r"\bporn\b",
    r"\bnude\b",
    r"\bxxx\b",
    r"\bfuck\b",
    r"\bshit\b",
    r"\bbitch\b",
    r"\basshole\b",
    r"\brape\b",
    r"\bkidnapp\b",
    r"\bmolest\b",
    r"\bpedophil\b",
    r"\bchild\s*porn\b",
    r"\bchild\s*seller\b",
    r"\bsell\s*child(ren)?\b",
    r"\bselling\s*child(ren)?\b"
]

# Additional leet speak NSFW words
LEET_NSFW_WORDS = {
    "s3x", "p0rn", "n00d", "d1ck", "pu55y",
    "fuck", "sh1t", "b1tch", "a55", "x_x_x",
    "naked", "nude", "escort", "prostitute"
}

NSFW_WORDS = {
    # Sexual content
    'sexual': [
        'porn', 'sex', 'xxx', 'nude', 'nudity', 'escort', 'prostitute',
        'hooker', 'whore', 'slut', 'cock', 'pussy', 'dick', 'vagina',
        'intercourse', 'orgasm', 'ejaculation', 'semen', 'erection',
        'masturbation', 'fetish', 'kink', 'bdsm', 'bondage', 'incest',
        'pedophile', 'loli', 'shota', 'hentai', 'tentacle', 'ahegao'
    ],
    
    # Child safety (zero tolerance)
    'child_safety': [
        'child', 'minor', 'underage', 'juvenile', 'teen', 'young',
        'boy', 'girl', 'kids', 'children', 'youth', 'adolescent',
        'school', 'elementary', 'kindergarten', 'daycare', 'nursery',
        'childporn', 'childseller', 'sellchild', 'sellingchild',
        'seller', 'sell', 'selling', 'sale', 'buying', 'purchase'
    ],
    
    # Offensive language
    'offensive': [
        'bitch', 'bastard', 'asshole', 'ass', 'fuck', 'shit', 'damn',
        'hell', 'crap', 'piss', 'turd', 'douche', 'prick', 'slut',
        'whore', 'tramp', 'skank', 'hoe', 'cunt', 'bollocks', 'wanker'
    ],
    
    # Drug-related
    'drugs': [
        'weed', 'marijuana', 'cannabis', 'coke', 'cocaine', 'heroin',
        'meth', 'crystal', 'ecstasy', 'mdma', 'lsd', 'acid', 'mushrooms',
        'psychedelic', 'opioid', 'fentanyl', 'crack', 'amphetamine',
        'pill', 'tablet', 'high', 'stoned', 'drug', 'dealer', 'pusher'
    ],
    
    # Violence and harm
    'violence': [
        'kill', 'murder', 'death', 'die', 'suicide', 'self-harm',
        'cutting', 'blood', 'gore', 'torture', 'abuse', 'rape',
        'assault', 'attack', 'beat', 'stab', 'shoot', 'hang',
        'execute', 'massacre', 'slaughter', 'genocide', 'terrorist'
    ],
    
    # Hate speech
    'hate': [
        'nazi', 'hitler', 'ss', 'swastika', 'kkk', 'supremacist',
        'racist', 'white power', 'black power', 'skinhead', 'neo-nazi',
        'aryan', 'segregation', 'apartheid', 'discrimination'
    ],
    
    # Scams and suspicious activity
    'scam': [
        'crypto', 'bitcoin', 'investment', 'pyramid', 'ponzi', 'mlm',
        'forex', 'trading', 'signal', 'pump', 'dump', 'moon', 'lambo',
        'giveaway', 'free', 'winner', 'claim', 'verify', 'hack',
        'exploit', 'cheat', 'glitch', 'unlimited', 'generator'
    ]
}

# Combined list for quick lookup
ALL_NSFW_WORDS = set()
for category_words in NSFW_WORDS.values():
    ALL_NSFW_WORDS.update(word.lower() for word in category_words)

# Add leet speak words
ALL_NSFW_WORDS.update(word.lower() for word in LEET_NSFW_WORDS)

# Words that should trigger immediate action (zero tolerance)
CRITICAL_WORDS = {
    'rape', 'pedophile', 'loli', 'shota', 'incest', 'child', 'minor',
    'suicide', 'self-harm', 'cutting', 'kill', 'murder', 'terrorist',
    'nazi', 'hitler', 'swastika', 'kkk', 'underage', 'children',
    'childporn', 'child porn', 'cp', 'csam', 'molest', 'kidnap',
    'childseller', 'child seller', 'sell child', 'selling child',
    'seller', 'sell', 'selling'
}
