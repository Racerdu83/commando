import discord
import asyncio
import os
from discord.ext import commands

TOKEN = os.getenv("TOKEN")
CATEGORY_ID = int(os.getenv("CATEGORY_ID", "0"))
CHANNEL_ID = int(os.getenv("CHANNEL_ID", "0"))
USER_ID = int(os.getenv("USER_ID", "0"))

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True
intents.guild_messages = True
intents.dm_messages = True

bot = commands.Bot(command_prefix="!", intents=intents)

ticket_messages = {}

class TicketView(discord.ui.View):
    def __init__(self, ticket_channel):
        super().__init__(timeout=None)
        self.ticket_channel = ticket_channel

    @discord.ui.button(label="Prendre en charge", style=discord.ButtonStyle.success, custom_id="take_ticket")
    async def take_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.ticket_channel.send(f"✅ {interaction.user.mention} a pris en charge ce ticket.")
        await interaction.response.defer()

    @discord.ui.button(label="Mettre en attente", style=discord.ButtonStyle.danger, custom_id="hold_ticket")
    async def hold_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.ticket_channel.send(f"⏳ {interaction.user.mention} a mis ce ticket en attente.")
        await interaction.response.defer()

    @discord.ui.button(label="Fermer le ticket", style=discord.ButtonStyle.secondary, custom_id="close_ticket")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.ticket_channel.send(f"❌ {interaction.user.mention} a fermé ce ticket.")
        await interaction.response.defer()
        await self.ticket_channel.delete(reason=f"Ticket fermé par {interaction.user}")

async def send_keep_alive_message():
    """Envoie un MP toutes les 3 minutes pour garder le bot actif."""
    await bot.wait_until_ready()
    user = await bot.fetch_user(USER_ID)

    while not bot.is_closed():
        try:
            await user.send("🔄 Ping ! Ceci est un message automatique pour garder le bot actif.")
            print("✅ Message de keep-alive envoyé.")
        except Exception as e:
            print(f"⚠️ Impossible d'envoyer un message à {USER_ID}: {e}")

        await asyncio.sleep(5)

@bot.event
async def on_ready():
    print(f"✅ {bot.user.name} est connecté et surveille les tickets en temps réel !")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="les tickets de Racer83"))
    
    bot.loop.create_task(send_keep_alive_message())

async def update_ticket_log(ticket_channel, author, message_content):
    log_channel = bot.get_channel(CHANNEL_ID)
    if not log_channel:
        return

    ticket_id = ticket_channel.id
    message_entry = f"**{author}:** {message_content}"

    if ticket_id in ticket_messages:
        msg_id, messages_list = ticket_messages[ticket_id]
        messages_list.append(message_entry)
        if len(messages_list) > 10:
            messages_list.pop(0)

        embed = discord.Embed(
            title=f"📩 Suivi du ticket {ticket_channel.name}",
            description="\n".join(messages_list),
            color=discord.Color.blue()
        )
        embed.set_footer(text=f"Salon: {ticket_channel.name} | ID: {ticket_id}")

        view = TicketView(ticket_channel)
        view.add_item(discord.ui.Button(label="Aller au ticket", style=discord.ButtonStyle.link, url=ticket_channel.jump_url))

        try:
            msg = await log_channel.fetch_message(msg_id)
            await msg.edit(embed=embed, view=view)
        except discord.NotFound:
            new_msg = await log_channel.send(embed=embed, view=view)
            ticket_messages[ticket_id] = (new_msg.id, messages_list)
    else:
        embed = discord.Embed(
            title=f"📩 Suivi du ticket {ticket_channel.name}",
            description=message_entry,
            color=discord.Color.blue()
        )
        embed.set_footer(text=f"Salon: {ticket_channel.name} | ID: {ticket_id}")

        view = TicketView(ticket_channel)
        view.add_item(discord.ui.Button(label="Aller au ticket", style=discord.ButtonStyle.link, url=ticket_channel.jump_url))

        new_msg = await log_channel.send(embed=embed, view=view)
        ticket_messages[ticket_id] = (new_msg.id, [message_entry])

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if message.channel.category and message.channel.category.id == CATEGORY_ID:
        await update_ticket_log(message.channel, message.author, message.content)

@bot.event
async def on_guild_channel_create(channel):
    if channel.category and channel.category.id == CATEGORY_ID:
        log_channel = bot.get_channel(CHANNEL_ID)
        if log_channel:
            embed = discord.Embed(
                title="🆕 Nouveau ticket ouvert",
                description=f"**Nom du ticket:** {channel.name}",
                color=discord.Color.green()
            )
            embed.set_footer(text=f"ID du salon: {channel.id}")

            view = TicketView(channel)
            view.add_item(discord.ui.Button(label="Aller au ticket", style=discord.ButtonStyle.link, url=f"https://discord.com/channels/{channel.guild.id}/{channel.id}"))

            msg = await log_channel.send(embed=embed, view=view)
            ticket_messages[channel.id] = (msg.id, [])

bot.run(TOKEN)
