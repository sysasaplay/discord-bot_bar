import aiosqlite

class Database:
    def __init__(self, db_path="izakaya.db"):
        self.db_path = db_path

    async def setup_tables(self):
        """Inizializza le tabelle del database."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS economy (
                    user_id INTEGER PRIMARY KEY,
                    yen INTEGER DEFAULT 0
                )
            """)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS cooldowns (
                    user_id INTEGER PRIMARY KEY,
                    last_daily TIMESTAMP
                )
            """)
            await db.commit()
            print(f"✅ Tabelle database inizializzate su: {self.db_path}")

    # ── Metodi Economia ───────────────────────────────────────────────────────

    async def get_or_create_user(self, user_id, name):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("INSERT OR IGNORE INTO economy (user_id, yen) VALUES (?, 0)", (user_id,))
            await db.commit()

    async def buy_item(self, user_id, amount):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT yen FROM economy WHERE user_id = ?", (user_id,)) as cursor:
                row = await cursor.fetchone()
                if row and row[0] >= amount:
                    await db.execute("UPDATE economy SET yen = yen - ? WHERE user_id = ?", (amount, user_id))
                    await db.commit()
                    return True
        return False

    async def update_balance(self, user_id, amount):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("UPDATE economy SET yen = yen + ? WHERE user_id = ?", (amount, user_id))
            await db.commit()

    async def get_balance(self, user_id):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT yen FROM economy WHERE user_id = ?", (user_id,)) as cursor:
                row = await cursor.fetchone()
                return row[0] if row else 0

    # ── Metodi Cooldown (Daily) ────────────────────────────────────────────────

    async def get_last_daily(self, user_id):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT last_daily FROM cooldowns WHERE user_id = ?", (user_id,)) as cursor:
                row = await cursor.fetchone()
                return row[0] if row else None

    async def update_daily_time(self, user_id, timestamp):
        # Questo print ti confermerà se il comando /daily sta davvero chiamando questa funzione
        print(f"DEBUG: Scrittura in DB per {user_id} -> {timestamp}")
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("INSERT OR REPLACE INTO cooldowns (user_id, last_daily) VALUES (?, ?)", (user_id, timestamp))
            await db.commit()
            print("DEBUG: Commit avvenuto con successo.")