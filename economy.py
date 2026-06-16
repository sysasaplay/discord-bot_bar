import discord
from discord.ext import commands
from discord import app_commands
import datetime

class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="daily", description="🎁 Riscatta il tuo bonus giornaliero (ogni 24h)")
    async def daily(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        now = datetime.datetime.now()
        
        # Recupera l'ultimo utilizzo dal database
        last_daily_str = await self.bot.db.get_last_daily(user_id)
        
        print(f"DEBUG: Controllo daily per {user_id}. Ultima data: {last_daily_str}")

        if last_daily_str:
            last_daily = datetime.datetime.fromisoformat(last_daily_str)
            differenza = now - last_daily
            
            # Se è passata meno di 24 ore
            if differenza < datetime.timedelta(hours=24):
                remaining = datetime.timedelta(hours=24) - differenza
                hours, remainder = divmod(int(remaining.total_seconds()), 3600)
                minutes, _ = divmod(remainder, 60)
                
                print(f"DEBUG: Cooldown attivo. Mancano {hours}h {minutes}m")
                return await interaction.response.send_message(
                    f"⏳ Hai già riscosso il bonus! Riprova tra **{hours} ore e {minutes} minuti**.", 
                    ephemeral=True
                )

        # Se il bonus è disponibile
        print(f"DEBUG: Bonus disponibile per {user_id}. Aggiorno DB.")
        await self.bot.db.update_balance(user_id, 500)
        await self.bot.db.update_daily_time(user_id, now.isoformat())
        
        await interaction.response.send_message("🎁 Hai ricevuto 500 Yen! Torna tra 24 ore.")

    @app_commands.command(name="balance", description="💰 Controlla il tuo saldo")
    async def balance(self, interaction: discord.Interaction):
        saldo = await self.bot.db.get_balance(interaction.user.id)
        await interaction.response.send_message(f"💰 Il tuo saldo attuale è: **{saldo} ¥**")

async def setup(bot):
    await bot.add_cog(Economy(bot))