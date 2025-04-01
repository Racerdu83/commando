import os
import discord
import asyncio
from discord.ext import commands

TOKEN = os.getenv("DISCORD_BOT_TOKEN")  # Récupérer le token depuis les variables d'environnement
CATEGORY_ID = 1346873527986552902  # ID de la catégorie des tickets
CHANNEL_ID = 1346836457633087569  # ID du salon de gestion des tickets
USER_ID = 123456789012345678  # Remplace par l'ID de l'utilisateur à notifier

# Activer les intents pour suivre les messages et les salons
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True
intents.guild_messages = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

ticket_messages = {}  # Stocker les messages pour chaque ticket

# Commandes d'administration
@bot.command()
@commands.has_permissions(administrator=True)
async def clear(ctx, amount: int):
    await ctx.channel.purge(limit=amount + 1)
    await ctx.send(f"✅ {amount} messages ont été supprimés.", delete_after=5)

@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason="Aucune raison spécifiée"):
    await member.kick(reason=reason)
    await ctx.send(f"👢 {member.mention} a été expulsé. Raison: {reason}")

@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason="Aucune raison spécifiée"):
    await member.ban(reason=reason)
    await ctx.send(f"🔨 {member.mention} a été banni. Raison: {reason}")

@bot.command()
@commands.has_permissions(ban_members=True)
async def unban(ctx, user_id: int):
    user = await bot.fetch_user(user_id)
    await ctx.guild.unban(user)
    await ctx.send(f"✅ {user.mention} a été débanni.")

@bot.command()
@commands.has_permissions(manage_roles=True)
async def mute(ctx, member: discord.Member, *, reason="Aucune raison spécifiée"):
    role = discord.utils.get(ctx.guild.roles, name="Muted")
    if not role:
        role = await ctx.guild.create_role(name="Muted")
        for channel in ctx.guild.channels:
            await channel.set_permissions(role, send_messages=False)
    await member.add_roles(role, reason=reason)
    await ctx.send(f"🔇 {member.mention} a été mute. Raison: {reason}")

@bot.command()
@commands.has_permissions(manage_roles=True)
async def unmute(ctx, member: discord.Member):
    role = discord.utils.get(ctx.guild.roles, name="Muted")
    if role in member.roles:
        await member.remove_roles(role)
        await ctx.send(f"🔊 {member.mention} a été unmute.")
    else:
        await ctx.send(f"⚠️ {member.mention} n'est pas mute.")

@bot.slash_command(name="config", description="Configurer la catégorie et le salon de contrôle du bot")
@commands.has_permissions(administrator=True)
async def config(ctx, category: discord.CategoryChannel, log_channel: discord.TextChannel):
    global CATEGORY_ID, CHANNEL_ID
    CATEGORY_ID = category.id
    CHANNEL_ID = log_channel.id
    await ctx.send(f"✅ Configuration mise à jour !\n📂 Catégorie surveillée : {category.name}\n📢 Salon de contrôle : {log_channel.mention}")

async def send_status_message():
    await bot.wait_until_ready()
    user = await bot.fetch_user(USER_ID)
    while not bot.is_closed():
        await user.send("✅ Le bot est toujours actif !")
        await asyncio.sleep(180)  # 3 minutes

@bot.event
async def on_ready():
    print(f"✅ {bot.user.name} est connecté et prêt à administrer !")
    bot.loop.create_task(send_status_message())

bot.run(TOKEN)
