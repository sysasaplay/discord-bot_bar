"""
🍱 menu_data.py — Definizione del menu dell'Izakaya.

Centralizzare il menu qui permette di modificare prezzi/item in un solo posto
senza toccare la logica dei comandi.
"""

# Struttura: { "nome_chiave": {"label": str, "emoji": str, "price": int, "category": str} }
MENU: dict[str, dict] = {
    # ── Bevande ───────────────────────────────────────────────────────────────
    "sake":       {"label": "Sake",        "emoji": "🍶", "price": 150, "category": "Bevande"},
    "matcha":     {"label": "Matcha Latte","emoji": "🍵", "price": 120, "category": "Bevande"},
    "ramune":     {"label": "Ramune",      "emoji": "🍾", "price": 100, "category": "Bevande"},
    "bubbletea":  {"label": "Bubble Tea",  "emoji": "🧋", "price": 130, "category": "Bevande"},
    "whisky":     {"label": "Whisky Soda", "emoji": "🥃", "price": 200, "category": "Bevande"},
    "beer":       {"label": "Birra Asahi", "emoji": "🍺", "price": 110, "category": "Bevande"},

    # ── Cibo ──────────────────────────────────────────────────────────────────
    "ramen":      {"label": "Ramen",       "emoji": "🍜", "price": 350, "category": "Cibo"},
    "sushi":      {"label": "Sushi",       "emoji": "🍣", "price": 400, "category": "Cibo"},
    "dango":      {"label": "Dango",       "emoji": "🍡", "price": 180, "category": "Cibo"},
    "gyoza":      {"label": "Gyoza",       "emoji": "🥟", "price": 250, "category": "Cibo"},
    "takoyaki":   {"label": "Takoyaki",    "emoji": "🐙", "price": 220, "category": "Cibo"},
    "onigiri":    {"label": "Onigiri",     "emoji": "🍙", "price": 160, "category": "Cibo"},
    "karaage":    {"label": "Karaage",     "emoji": "🍗", "price": 280, "category": "Cibo"},
    "edamame":    {"label": "Edamame",     "emoji": "🫛", "price": 100, "category": "Cibo"},
}

# Colore embed per categoria
CATEGORY_COLORS = {
    "Bevande": 0x5B9BD5,   # Blu acqua
    "Cibo":    0xE07B39,   # Arancio caldo
}

# Bonus giornaliero
DAILY_REWARD = 500

# Quota fissa per /round (oltre al costo moltiplicato per i membri)
ROUND_BASE_COST_MULTIPLIER = 1.0  # prezzo × numero_membri_online


def get_item(key: str) -> dict | None:
    """Cerca un item nel menu (case-insensitive)."""
    return MENU.get(key.lower())


def all_keys() -> list[str]:
    """Lista di tutte le chiavi valide per l'autocomplete degli slash command."""
    return list(MENU.keys())