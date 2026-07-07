import discord
from discord.ext import commands
from discord import app_commands
import random

class Games(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="dice", description="🎲 Scommetti i tuoi Yen al gioco tradizionale Cho-Han")
    @app_commands.describe(scommessa="La quantità di Yen da puntare", scelta="Scommetti su Pari (Cho) o Dispari (Han)")
    @app_commands.choices(scelta=[
        app_commands.Choice(name="Pari (Cho)", value="pari"),
        app_commands.Choice(name="Dispari (Han)", value="dispari")
    ])
    async def dice(self, interaction: discord.Interaction, scommessa: int, scelta: str):
        if scommessa <= 0:
            return await interaction.response.send_message("❌ La scommessa deve essere maggiore di zero!", ephemeral=True)

        balance = await self.bot.db.get_balance(interaction.user.id)
        if balance < scommessa:
            return await interaction.response.send_message("❌ Non hai abbastanza Yen per questa scommessa!", ephemeral=True)

        dado1 = random.randint(1, 6)
        dado2 = random.randint(1, 6)
        totale = dado1 + dado2
        risultato = "pari" if totale % 2 == 0 else "dispari"

        embed = discord.Embed(title="🎲 Gioco del Cho-Han", color=0x3498DB)
        embed.description = f"I dadi rotolano... escono un **{dado1}** e un **{dado2}**! Totale: **{totale}**."

        if scelta == resultado:
            await self.bot.db.add_coins(interaction.user.id, scommessa)
            embed.add_field(name="Risultato", value=f"🎉 Hai indovinato! Raddoppi la posta e vinci **{scommessa} ¥**!")
            embed.color = 0x2ECC71
        else:
            await self.bot.db.buy_item(interaction.user.id, scommessa)
            embed.add_field(name="Risultato", value=f"💀 Hai perso. Il banco si tiene i tuoi **{scommessa} ¥**.")
            embed.color = 0xE74C3C

        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Games(bot))
