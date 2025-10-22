"""
Keyword Expansions for Party Planning

Comprehensive keyword lists with variations and synonyms for:
- Themes
- Event types
- Venue types
- Agent categories
- Party elements

Used by InputAnalyzer and SmartInputRouter for better classification.
"""

from typing import Dict, List


# ===== THEME KEYWORDS =====

THEME_KEYWORDS = {
    # Princess & Fairy Tale
    'princess': ['princess', 'cinderella', 'belle', 'royal', 'crown', 'tiara', 'fairy tale',
                 'castle', 'prince', 'enchanted', 'ballgown', 'disney princess'],

    # Superhero
    'superhero': ['superhero', 'super hero', 'batman', 'spiderman', 'superman', 'avengers',
                  'marvel', 'dc comics', 'captain america', 'wonder woman', 'hulk', 'thor',
                  'iron man', 'black panther', 'hero', 'powers', 'cape'],

    # Unicorn & Rainbow
    'unicorn': ['unicorn', 'magical unicorn', 'rainbow unicorn', 'unicorn horn', 'unicorn party',
                'unicorns', 'magical', 'enchanted', 'pastel unicorn'],

    'rainbow': ['rainbow', 'rainbows', 'colorful', 'multi-color', 'pride', 'rainbow themed',
                'color', 'colours', 'vibrant'],

    # Dinosaur
    'dinosaur': ['dinosaur', 'dino', 'dinosaurs', 't-rex', 'triceratops', 'stegosaurus',
                 'jurassic', 'prehistoric', 'dino party', 'fossils', 'paleontology'],

    # Space & Science
    'space': ['space', 'astronaut', 'rocket', 'planets', 'galaxy', 'stars', 'moon',
              'solar system', 'nasa', 'outer space', 'cosmic', 'nebula', 'astronomy'],

    'science': ['science', 'scientist', 'lab', 'laboratory', 'experiment', 'chemistry',
                'physics', 'stem', 'mad scientist', 'beaker', 'microscope'],

    # Pirate
    'pirate': ['pirate', 'pirates', 'treasure', 'ship', 'captain', 'skull and crossbones',
               'treasure map', 'ahoy', 'buccaneer', 'nautical', 'sea', 'ocean'],

    # Jungle & Safari
    'jungle': ['jungle', 'safari', 'rainforest', 'tropical', 'wild', 'wilderness',
               'jungle animals', 'vines', 'trees', 'forest'],

    'safari': ['safari', 'zoo', 'wild animals', 'lion', 'elephant', 'giraffe', 'zebra',
               'africa', 'animal', 'wildlife', 'animal kingdom'],

    # Ocean & Beach
    'ocean': ['ocean', 'sea', 'marine', 'underwater', 'mermaid', 'fish', 'whale', 'dolphin',
              'coral reef', 'nautical', 'maritime', 'aquatic'],

    'beach': ['beach', 'seaside', 'coastal', 'sand', 'surf', 'waves', 'summer', 'tropical beach',
              'palm trees', 'luau', 'hawaiian'],

    'mermaid': ['mermaid', 'under the sea', 'little mermaid', 'ariel', 'ocean princess',
                'sea creature', 'fins', 'tail', 'shell'],

    # Farm & Barnyard
    'farm': ['farm', 'barnyard', 'farmyard', 'barn', 'tractor', 'farmhouse', 'country',
             'animals', 'cow', 'pig', 'chicken', 'horse', 'agriculture', 'rural'],

    # Sports
    'sports': ['sports', 'football', 'soccer', 'basketball', 'baseball', 'tennis',
               'athlete', 'team', 'championship', 'game', 'play ball', 'sporting'],

    # Art & Creativity
    'art': ['art', 'painting', 'creative', 'craft', 'artist', 'paint', 'canvas', 'color',
            'artsy', 'crafty', 'artistic', 'painter', 'drawing', 'sculpture'],

    # Music & Dance
    'music': ['music', 'musical', 'concert', 'band', 'rock', 'pop', 'singer', 'karaoke',
              'instruments', 'notes', 'melody', 'musician'],

    'dance': ['dance', 'dancing', 'ballet', 'hip hop', 'ballerina', 'dancer', 'choreography',
              'disco', 'ballroom', 'performance'],

    # Vintage & Elegant
    'vintage': ['vintage', 'retro', 'antique', 'classic', 'old fashioned', 'nostalgic',
                'rustic', 'shabby chic', 'victorian', 'art deco'],

    'elegant': ['elegant', 'sophisticated', 'classy', 'formal', 'upscale', 'refined',
                'luxurious', 'glamorous', 'chic', 'stylish'],

    # Garden & Floral
    'garden': ['garden', 'floral', 'botanical', 'flowers', 'blooms', 'nature', 'outdoor',
               'greenhouse', 'butterfly', 'spring', 'enchanted garden'],

    'tea party': ['tea party', 'tea', 'afternoon tea', 'high tea', 'teacup', 'teapot',
                  'british', 'crumpets', 'scones', 'garden party'],

    # Holiday Themes
    'winter wonderland': ['winter', 'snow', 'snowflake', 'frozen', 'ice', 'winter wonderland',
                         'christmas', 'holiday', 'frosty', 'icicle', 'snowman'],

    # Character Themes
    'paw patrol': ['paw patrol', 'chase', 'marshall', 'skye', 'rubble', 'pups'],

    'peppa pig': ['peppa pig', 'peppa', 'pig', 'muddy puddles', 'george'],

    'frozen': ['frozen', 'elsa', 'anna', 'olaf', 'let it go', 'ice queen', 'arendelle'],

    'mickey mouse': ['mickey', 'minnie', 'mickey mouse', 'clubhouse', 'disney'],

    # Other Popular Themes
    'carnival': ['carnival', 'circus', 'fair', 'festival', 'big top', 'clown', 'acrobat',
                 'carnival games', 'ferris wheel', 'popcorn', 'cotton candy'],

    'construction': ['construction', 'builder', 'tools', 'hard hat', 'digger', 'excavator',
                     'truck', 'building', 'crane', 'worker'],

    'camping': ['camping', 'outdoor', 'tent', 'campfire', 'smores', 'hiking', 'nature',
                'wilderness', 'adventure', 'forest', 'camp out'],
}


# ===== EVENT TYPE KEYWORDS =====

EVENT_TYPE_KEYWORDS = {
    'birthday': ['birthday', 'bday', 'b-day', 'birth day', 'turning', 'celebration',
                 'born day', 'natal day', 'anniversary of birth'],

    'baby shower': ['baby shower', 'shower', 'expecting', 'pregnancy', 'mom-to-be',
                    'new baby', 'baby celebration', 'expecting mother'],

    'wedding': ['wedding', 'marriage', 'nuptials', 'ceremony', 'reception', 'bride',
                'groom', 'matrimony', 'bridal', 'tying the knot'],

    'anniversary': ['anniversary', 'years together', 'milestone', 'celebration',
                    'wedding anniversary', 'years married'],

    'graduation': ['graduation', 'grad', 'graduate', 'commencement', 'diploma',
                   'degree', 'graduating', 'graduation party'],

    'retirement': ['retirement', 'retiring', 'retired', 'farewell', 'end of career',
                   'retirement party'],

    'baptism': ['baptism', 'christening', 'dedication', 'religious ceremony',
                'first communion', 'confirmation'],

    'engagement': ['engagement', 'engaged', 'proposal', 'getting married',
                   'engagement party', 'bride-to-be', 'fiancé'],

    'housewarming': ['housewarming', 'new home', 'new house', 'moving in',
                     'home celebration'],

    'reunion': ['reunion', 'family gathering', 'class reunion', 'get-together',
                'family reunion', 'gathering'],
}


# ===== VENUE TYPE KEYWORDS =====

VENUE_KEYWORDS = {
    'venue': ['venue', 'location', 'place', 'where', 'site', 'setting', 'space'],

    'park': ['park', 'outdoor', 'playground', 'public park', 'recreation area',
             'garden', 'green space', 'picnic area'],

    'home': ['home', 'house', 'backyard', 'private residence', 'my place',
             'living room', 'at home', 'indoors', 'residence'],

    'hall': ['hall', 'banquet hall', 'event space', 'function hall', 'ballroom',
             'conference room', 'reception hall', 'community center'],

    'restaurant': ['restaurant', 'cafe', 'dining', 'eatery', 'bistro', 'diner',
                   'food venue', 'private dining'],

    'hotel': ['hotel', 'resort', 'hotel venue', 'conference center', 'convention center',
              'hotel ballroom'],

    'museum': ['museum', 'gallery', 'art museum', 'science center', 'exhibit space'],

    'beach': ['beach', 'seaside', 'oceanfront', 'waterfront', 'coastal venue'],
}


# ===== AGENT CATEGORY KEYWORDS =====

AGENT_ROUTING_KEYWORDS = {
    'theme': ['theme', 'decor', 'decoration', 'decorations', 'style', 'aesthetic', 'design',
              'color scheme', 'look', 'feel', 'vibe', 'ambiance', 'atmosphere', 'motif',
              'concept', 'idea', 'inspiration'],

    'cake': ['cake', 'dessert', 'sweet', 'tier', 'frosting', 'bakery', 'birthday cake',
             'cupcake', 'cupcakes', 'pastry', 'baked goods', 'icing', 'fondant', 'buttercream',
             'layer cake', 'sheet cake', 'specialty cake', 'custom cake'],

    'venue': ['venue', 'location', 'space', 'hall', 'room', 'park', 'place', 'where',
              'site', 'setting', 'facility', 'establishment', 'grounds', 'property',
              'address', 'zip code', 'zipcode', 'area', 'city', 'town'],

    'catering': ['food', 'menu', 'catering', 'meal', 'dining', 'eat', 'lunch', 'dinner',
                 'breakfast', 'snacks', 'appetizers', 'entree', 'buffet', 'service',
                 'cuisine', 'dishes', 'refreshments', 'beverage', 'drinks'],

    'vendor': ['vendor', 'supplier', 'service', 'professional', 'balloon', 'balloons',
               'decoration', 'photographer', 'photography', 'entertainment', 'entertainer',
               'dj', 'music', 'magician', 'performer', 'face painting', 'clown', 'bouncy house',
               'inflatable', 'photo booth', 'videographer', 'florist', 'rental'],

    'budget': ['budget', 'cost', 'price', 'affordable', 'cheap', 'expensive', 'spend',
               'money', 'financial', 'dollar', '$', 'estimate', 'quote', 'pricing'],

    'guest': ['guest', 'guests', 'people', 'attendees', 'visitors', 'invites', 'invitation',
              'rsvp', 'headcount', 'number of people', 'party size', 'group size'],
}


# ===== AGE GROUP KEYWORDS =====

AGE_GROUP_KEYWORDS = {
    'baby': ['baby', 'infant', 'newborn', 'babies', '0-1', 'under 1'],
    'toddler': ['toddler', 'toddlers', '1-3', 'little one', 'little ones', '2 year old', '3 year old'],
    'preschool': ['preschool', 'preschooler', '3-5', 'prekindergarten', 'pre-k', 'young child'],
    'kids': ['kids', 'children', 'child', '5-12', 'elementary', 'school age'],
    'teen': ['teen', 'teenager', 'adolescent', '13-18', 'high school', 'teenage'],
    'adult': ['adult', 'grown up', '18+', 'over 18', 'mature'],
    'senior': ['senior', 'elderly', 'retired', 'golden years', '65+', 'older adult'],
}


# ===== PARTY ELEMENTS =====

PARTY_ELEMENT_KEYWORDS = {
    'decorations': ['decorations', 'decor', 'balloons', 'streamers', 'banners', 'centerpieces',
                    'table settings', 'backdrop', 'garland', 'confetti', 'flowers'],

    'entertainment': ['entertainment', 'activities', 'games', 'fun', 'performer', 'show',
                      'bounce house', 'face painting', 'magic show', 'crafts'],

    'favors': ['party favors', 'favors', 'goody bags', 'gift bags', 'take home', 'giveaways',
               'thank you gifts', 'loot bags', 'goodie bags'],

    'invitations': ['invitations', 'invite', 'invites', 'rsvp', 'save the date', 'announcement'],

    'tableware': ['plates', 'cups', 'napkins', 'utensils', 'tablecloth', 'tableware',
                  'disposable', 'party supplies', 'serving'],
}


# ===== HELPER FUNCTIONS =====

def get_all_theme_keywords() -> List[str]:
    """Get all theme keywords as a flat list"""
    all_keywords = []
    for theme, variations in THEME_KEYWORDS.items():
        all_keywords.extend(variations)
    return list(set(all_keywords))


def get_all_event_keywords() -> List[str]:
    """Get all event type keywords as a flat list"""
    all_keywords = []
    for event, variations in EVENT_TYPE_KEYWORDS.items():
        all_keywords.extend(variations)
    return list(set(all_keywords))


def get_expanded_routing_rules() -> Dict[str, List[str]]:
    """
    Get expanded routing rules for InputAnalyzer
    Combines base keywords with theme variations
    """
    return {
        'theme': AGENT_ROUTING_KEYWORDS['theme'] + get_all_theme_keywords(),
        'cake': AGENT_ROUTING_KEYWORDS['cake'],
        'venue': AGENT_ROUTING_KEYWORDS['venue'] + VENUE_KEYWORDS.get('venue', []),
        'catering': AGENT_ROUTING_KEYWORDS['catering'],
        'vendor': AGENT_ROUTING_KEYWORDS['vendor'],
        'budget': AGENT_ROUTING_KEYWORDS['budget'],
        'guest': AGENT_ROUTING_KEYWORDS['guest'],
    }


def find_matching_theme(text: str) -> List[str]:
    """
    Find all themes that match keywords in the text

    Args:
        text: Input text to search

    Returns:
        List of matching theme names
    """
    text_lower = text.lower()
    matches = []

    for theme, keywords in THEME_KEYWORDS.items():
        for keyword in keywords:
            if keyword in text_lower:
                matches.append(theme)
                break

    return matches


def find_matching_event_type(text: str) -> List[str]:
    """
    Find all event types that match keywords in the text

    Args:
        text: Input text to search

    Returns:
        List of matching event type names
    """
    text_lower = text.lower()
    matches = []

    for event_type, keywords in EVENT_TYPE_KEYWORDS.items():
        for keyword in keywords:
            if keyword in text_lower:
                matches.append(event_type)
                break

    return matches


# Export
__all__ = [
    "THEME_KEYWORDS",
    "EVENT_TYPE_KEYWORDS",
    "VENUE_KEYWORDS",
    "AGENT_ROUTING_KEYWORDS",
    "AGE_GROUP_KEYWORDS",
    "PARTY_ELEMENT_KEYWORDS",
    "get_all_theme_keywords",
    "get_all_event_keywords",
    "get_expanded_routing_rules",
    "find_matching_theme",
    "find_matching_event_type",
]
