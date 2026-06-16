import discord
from discord.ext import commands
import asyncio
import traceback
from database import Database  # Assicurati che database.py sia nella stessa cartella

# ── Configurazione ───────────────────────────────────────────────────────────
intents = discord.Intents.default()
intents.message_content = True 
intents.members = True          

bot = commands.Bot(command_prefix="!", intents=intents)

# Inizializziamo il database
bot.db = Database()

# Lista dei moduli (Cogs)
COGS = ["cogs.economy", "cogs.menu", "cogs.games"]

@bot.event
async def on_ready():
    print(f"🏮 {bot.user} è online e pronto.")
    try:
        # Sincronizza i comandi slash
        synced = await bot.tree.sync()
        print(f"✅ Sincronizzati {len(synced)} comandi slash.")
    except Exception as e:
        print(f"❌ Errore sync: {e}")

async def main():
    # Setup database
    await bot.db.setup_tables()
    
    # Caricamento Cogs
    for cog in COGS:
        try:
            await bot.load_extension(cog)
            print(f"📦 Caricato: {cog}")
        except Exception as e:
            print(f"❌ Errore caricamento {cog}: {e}")
            traceback.print_exc()
            
    # Token del bot
    TOKEN = "MTUxMzk3ODI5OTAwNzc2MjQ5Ng.G8-DsS.oWzqBdDjRvy73IkIz3wZYvLEUIAdOiqllTw5Ak"
    await bot.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(main())