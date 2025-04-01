import discord
import os
from discord.ext import commands

TOKEN = os.getenv("Token")
CATEGORY_ID = None  # ID de la catégorie des tickets (modifiable via /config)
CHANNEL_ID = None  # ID du salon de gestion des tickets (modifiable via /config)

# Activer les intents pour suivre les messages et les salons
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True
intents.guild_messages = True
intents.members = True

bot = commands.Bot(command_prefix="/", intents=intents)

# Stocker les messages pour chaque ticket
ticket_messages = {}  # {ticket_id: (message_id, messages_list)}


@bot.slash_command(name="config", description="Configurer le bot")
async def config(ctx, category_id: int, channel_id: int):
    global CATEGORY_ID, CHANNEL_ID
    CATEGORY_ID = category_id
    CHANNEL_ID = channel_id
    await ctx.respond(f"✅ Configuration mise à jour !\nCatégorie des tickets : `{CATEGORY_ID}`\nSalon de gestion : `{CHANNEL_ID}`")


class TicketView(discord.ui.View):
    def __init__(self, ticket_channel):
        super().__init__()
        self.ticket_channel = ticket_channel

    @discord.ui.button(label="Prendre en charge", style=discord.ButtonStyle.success)
    async def take_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.ticket_channel.send(f"✅ {interaction.user.mention} a pris en charge ce ticket.")
        await interaction.response.defer()

    @discord.ui.button(label="Mettre en attente", style=discord.ButtonStyle.danger)
    async def hold_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.ticket_channel.send(f"⏳ {interaction.user.mention} a mis ce ticket en attente.")
        await interaction.response.defer()

    @discord.ui.button(label="Fermer le ticket", style=discord.ButtonStyle.secondary)
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.ticket_channel.send(f"❌ {interaction.user.mention} a fermé ce ticket.")
        await interaction.response.defer()
        await self.ticket_channel.delete(reason=f"Ticket fermé par {interaction.user}")


@bot.event
async def on_ready():
    print(f"✅ {bot.user.name} est connecté et surveille les tickets en temps réel !")


@bot.slash_command(name="mute", description="Rendre un membre muet")
async def mute(ctx, member: discord.Member, reason: str = "Aucune raison spécifiée"):
    await member.edit(mute=True)
    await ctx.respond(f"🔇 {member.mention} a été rendu muet. Raison : {reason}")


@bot.slash_command(name="unmute", description="Rendre la parole à un membre")
async def unmute(ctx, member: discord.Member):
    await member.edit(mute=False)
    await ctx.respond(f"🔊 {member.mention} peut maintenant parler à nouveau.")


@bot.slash_command(name="warn", description="Avertir un membre")
async def warn(ctx, member: discord.Member, *, reason: str = "Aucune raison spécifiée"):
    await ctx.respond(f"⚠️ {member.mention} a été averti. Raison : {reason}")


@bot.slash_command(name="slowmode", description="Définir un slowmode sur un salon")
async def slowmode(ctx, seconds: int):
    await ctx.channel.edit(slowmode_delay=seconds)
    await ctx.respond(f"🐢 Slowmode défini sur {seconds} secondes.")


@bot.slash_command(name="lock", description="Verrouiller un salon")
async def lock(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)
    await ctx.respond("🔒 Ce salon a été verrouillé.")


@bot.slash_command(name="unlock", description="Déverrouiller un salon")
async def unlock(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=True)
    await ctx.respond("🔓 Ce salon a été déverrouillé.")


@bot.slash_command(name="nick", description="Changer le pseudo d'un membre")
async def nick(ctx, member: discord.Member, *, nickname: str):
    await member.edit(nick=nickname)
    await ctx.respond(f"📝 Le pseudo de {member.mention} a été changé en {nickname}.")


@bot.slash_command(name="purge", description="Supprimer un grand nombre de messages")
async def purge(ctx, amount: int):
    await ctx.channel.purge(limit=amount + 1)
    await ctx.respond(f"🧹 {amount} messages supprimés.", ephemeral=True)


bot.run(TOKEN)
