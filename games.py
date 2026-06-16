import discord
from discord import app_commands
from discord.ext import commands
import random

# ── Logica Blackjack ──────────────────────────────────────────────────────────
SUITS = {"♠": "♠️", "♥": "♥️", "♦": "♦️", "♣": "♣️"}
RANKS = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
CARD_VALUES = {"A": 11, "2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7, "8": 8, "9": 9, "10": 10, "J": 10, "Q": 10, "K": 10}

def new_deck():
    deck = [(rank, suit) for suit in SUITS for rank in RANKS]
    random.shuffle(deck)
    return deck

def hand_value(hand):
    total = sum(CARD_VALUES[rank] for rank, _ in hand)
    aces = sum(1 for rank, _ in hand if rank == "A")
    while total > 21 and aces:
        total -= 10
        aces -= 1
    return total

def card_str(card): return f"`{card[0]}{SUITS[card[1]]}`"

def hand_str(hand, hide_second=False):
    cards = [card_str(hand[0])]
    if hide_second and len(hand) > 1: cards.append("`🂠`")
    else: cards += [card_str(c) for c in hand[1:]]
    return " ".join(cards)

# ── Classe Blackjack ──────────────────────────────────────────────────────────
class BlackjackGame:
    def __init__(self, bot, player, bet):
        self.bot, self.player_id, self.bet = bot, player.id, bet
        self.player_name = player.display_name
        self.deck = new_deck()
        self.player_hand, self.dealer_hand = [self.deck.pop(), self.deck.pop()], [self.deck.pop(), self.deck.pop()]

    def build_embed(self, game_over=False, result=""):
        embed = discord.Embed(title="🃏 Blackjack — Izakaya Casino", color=0x3498DB if not result else 0x2ECC71)
        dealer_val = hand_value(self.dealer_hand)
        dealer_display = hand_str(self.dealer_hand, not game_over)
        dealer_label = f"**{dealer_val}**" if game_over else f"**{hand_value(self.dealer_hand[:1])}** + ?"
        
        embed.add_field(name=f"🏮 Dealer — {dealer_label}", value=dealer_display, inline=False)
        embed.add_field(name=f"👤 {self.player_name} — {hand_value(self.player_hand)}", value=hand_str(self.player_hand), inline=False)
        embed.add_field(name="💴 Puntata", value=f"**{self.bet:,} ¥**", inline=True)
        
        if result:
            msg = {"win": "✅ Hai vinto!", "loss": "❌ Hai perso.", "push": "🤝 Pareggio.", "bust": "💥 Sballato!"}
            embed.add_field(name="📋 Esito", value=msg.get(result, ""), inline=True)
        return embed

# ── View Blackjack ──────────────────────────────────────────────────────────
class BlackjackView(discord.ui.View):
    def __init__(self, game):
        super().__init__(timeout=60)
        self.game = game

    @discord.ui.button(label="🃏 Carta", style=discord.ButtonStyle.primary)
    async def hit(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.game.player_hand.append(self.game.deck.pop())
        if hand_value(self.game.player_hand) > 21:
            await self.finish_game(interaction, "bust")
        else:
            await interaction.response.edit_message(embed=self.game.build_embed(False), view=self)

    @discord.ui.button(label="✋ Stai", style=discord.ButtonStyle.secondary)
    async def stand(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.finish_game(interaction, "stand")

    @discord.ui.button(label="⚡ Doppio", style=discord.ButtonStyle.success)
    async def double_down(self, interaction: discord.Interaction, button: discord.ui.Button):
        if len(self.game.player_hand) != 2: return await interaction.response.send_message("❌ Solo con 2 carte!", ephemeral=True)
        if await self.game.bot.db.buy_item(self.game.player_id, self.game.bet):
            self.game.bet *= 2
            self.game.player_hand.append(self.game.deck.pop())
            await self.finish_game(interaction, "stand")
        else: await interaction.response.send_message("❌ Saldo insufficiente!", ephemeral=True)

    async def finish_game(self, interaction, action):
        result, payout = "loss", 0
        if action != "bust" and hand_value(self.game.player_hand) <= 21:
            while hand_value(self.game.dealer_hand) < 17: self.game.dealer_hand.append(self.game.deck.pop())
            p, d = hand_value(self.game.player_hand), hand_value(self.game.dealer_hand)
            if d > 21 or p > d: result, payout = "win", self.game.bet * 2
            elif p == d: result, payout = "push", self.game.bet
        if payout > 0: await self.game.bot.db.update_balance(self.game.player_id, payout)
        await interaction.response.edit_message(embed=self.game.build_embed(True, result), view=None)
        self.stop()

# ── Cog Games ───────────────────────────────────────────────────────────────
class Games(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_games = {}

    @app_commands.command(name="blackjack", description="🃏 Sfida il banco a Blackjack!")
    async def blackjack(self, interaction: discord.Interaction, puntata: int):
        if self.active_games.get(interaction.user.id): return await interaction.response.send_message("⚠️ Partita già in corso!", ephemeral=True)
        if not await self.bot.db.buy_item(interaction.user.id, puntata): return await interaction.response.send_message("❌ Saldo insufficiente!", ephemeral=True)
        
        self.active_games[interaction.user.id] = True
        try:
            game = BlackjackGame(self.bot, interaction.user, puntata)
            view = BlackjackView(game)
            await interaction.response.send_message(embed=game.build_embed(), view=view)
            await view.wait()
        finally:
            self.active_games[interaction.user.id] = False

    @app_commands.command(name="coinflip", description="🪙 Lancia la moneta")
    @app_commands.choices(scelta=[app_commands.Choice(name="Testa", value="testa"), app_commands.Choice(name="Croce", value="croce")])
    async def coinflip(self, interaction: discord.Interaction, puntata: int, scelta: str):
        saldo = await self.bot.db.get_balance(interaction.user.id)
        if puntata > saldo: return await interaction.response.send_message("❌ Saldo insufficiente!", ephemeral=True)
        risultato = random.choice(["testa", "croce"])
        if risultato == scelta:
            await self.bot.db.update_balance(interaction.user.id, puntata)
            await interaction.response.send_message(f"🪙 È uscito **{risultato.upper()}**! Hai vinto {puntata} ¥!")
        else:
            await self.bot.db.update_balance(interaction.user.id, -puntata)
            await interaction.response.send_message(f"🪙 È uscito **{risultato.upper()}**. Hai perso {puntata} ¥.")

async def setup(bot): await bot.add_cog(Games(bot))