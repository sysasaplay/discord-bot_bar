import sqlite3

class IzakayaDB:
    def __init__(self, db_name="izakaya.db"):
        self.db_name = db_name
        # Lista degli ID con privilegi speciali (Tu e Ally)
        self.GOD_MODES = [876853397746225162, 1363915831091921098]

    def _connect(self):
        return sqlite3.connect(self.db_name)

    def setup(self):
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    balance INTEGER DEFAULT 500
                )
            """)
            conn.commit()

    async def get_balance(self, user_id: int) -> int:
        # Se sei tu o Ally, avete sempre 1.000.000+ Yen fissi
        if user_id in self.GOD_MODES:
            return 9999999
            
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
            row = cursor.fetchone()
            if row is None:
                cursor.execute("INSERT INTO users (user_id, balance) VALUES (?, 500)", (user_id,))
                conn.commit()
                return 500
            return row[0]

    async def add_coins(self, user_id: int, amount: int):
        # Inutile aggiungere monete a chi ha già fondi infiniti
        if user_id in self.GOD_MODES:
            return
            
        await self.get_balance(user_id)
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (amount, user_id))
            conn.commit()

    async def buy_item(self, user_id: int, price: int) -> bool:
        # Se sei tu o Ally, l'acquisto va a buon fine all'istante senza scalare nulla
        if user_id in self.GOD_MODES:
            return True
            
        current_balance = await self.get_balance(user_id)
        if current_balance < price:
            return False
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET balance = balance - ? WHERE user_id = ?", (price, user_id))
            conn.commit()
            return True
