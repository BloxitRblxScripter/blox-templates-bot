import discord
from discord.ext import commands
from discord.ui import Button, View
import os
from dotenv import load_dotenv

from flask import Flask
from threading import Thread
import os

app = Flask(__name__)

@app.route("/", methods=["GET", "HEAD"])
def home():
    return "Bot is alive!"

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

print(f"Token loaded: {TOKEN[:20] if TOKEN else 'None'}...")

# ========== STORE CONFIGURATION (Easy to Edit) ==========
STORE_PRODUCTS = [
    {"emoji": "❓", "name": "Guess The _____ Template", "price": "$15.00", "status": "Available"},
]

PAYMENT_METHODS = "USD, Robux"
STORE_DESCRIPTION = "Welcome to Blox Templates! Click the button below to get started."
SUPPORT_MESSAGE = "Our support team is here to help you!"

# Ticket Configuration
FOUNDER_ROLE_NAME = "Founder👑"  # Exact role name with emoji
PURCHASE_CATEGORY_NAME = "[💸] PURCHASE"  # Exact category name
THUMBNAILS_CATEGORY_NAME = "[🎨] THUMBNAILS"  # Exact category name for thumbnails
# ========================================================

# ========== FAQ CONFIGURATION (Easy to Edit) ==========
FAQ_ITEMS = [
    {
        "question": "📦 What do I receive after purchasing a template?",
        "answer": "You will receive the full game template along with instructions. Instructions are provided via a document and/or a video explaining how to use the template."
    },
    {
        "question": "📉 What does limited stock mean?",
        "answer": "If a template is marked as Sold Out, it will never be restocked again. Once it’s gone, it’s permanently unavailable."
    },
    {
        "question": "🎮 Can I use the template for multiple games?",
        "answer": "Yes. You are allowed to create unlimited games using the template you purchase."
    },
    {
        "question": "💳 What payment methods do you accept?",
        "answer": "We accept payments in USD and Robux."
    },
    {
        "question": "🧪 Is there a test product available?",
        "answer": "Yes. A test product or demo is provided when the template goes on sale so you can review it before purchasing."
    },
    {
        "question": "💰 Can I sell a game made using the template?",
        "answer": "Yes, you may sell and monetize games created using the template. However, reselling, redistributing, or leaking the raw template is strictly prohibited."
    },
    {
        "question": "🔄 Are updates included?",
        "answer": "Updates are not guaranteed. However, any bugs found in the original template will be fixed free of charge, provided the template has not been modified."
    },
    {
        "question": "🔁 Do you offer refunds?",
        "answer": "No refunds are offered. All sales are final, so please review the test product and details carefully before purchasing."
    },
]

# ========================================================

# ========== WELCOME CONFIGURATION ==========
WELCOME_CHANNEL_NAME = "🙋‍♂️welcome"
MEMBER_ROLE_NAME = "Member"
WELCOME_ENABLED = False  # Set to True to enable auto-welcome
# ===========================================

bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())

# Store active tickets per user
active_tickets = {}

class BuyButton(View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="Buy", style=discord.ButtonStyle.primary, emoji="💎")
    async def buy_button(self, interaction: discord.Interaction, button: Button):
        user = interaction.user
        guild = interaction.guild
        
        # Check if user already has an active ticket
        if user.id in active_tickets:
            await interaction.response.send_message(
                "❌ You already have an active purchase ticket! Please close your current ticket first.",
                ephemeral=True
            )
            return
        
        # Find the category
        category = discord.utils.get(guild.categories, name=PURCHASE_CATEGORY_NAME)
        if not category:
            await interaction.response.send_message(
                f"❌ Category '{PURCHASE_CATEGORY_NAME}' not found! Please contact an admin.",
                ephemeral=True
            )
            return
        
        # Find the Founder role
        founder_role = discord.utils.get(guild.roles, name=FOUNDER_ROLE_NAME)
        if not founder_role:
            await interaction.response.send_message(
                f"❌ Role '{FOUNDER_ROLE_NAME}' not found! Please contact an admin.",
                ephemeral=True
            )
            return
        
        # Create ticket channel
        channel_name = f"purchase-{user.name}".lower().replace(" ", "-")
        
        # Set permissions
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            founder_role: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        
        try:
            ticket_channel = await guild.create_text_channel(
                name=channel_name,
                category=category,
                overwrites=overwrites
            )
            
            # Store the active ticket
            active_tickets[user.id] = ticket_channel.id
            
            # Send welcome message in ticket
            welcome_embed = discord.Embed(
                title="🎫 Purchase Ticket",
                description=f"Welcome {user.mention}! A staff member will assist you shortly.\n\n**Available Products:**",
                color=0x00ff00
            )
            
            for product in STORE_PRODUCTS:
                welcome_embed.add_field(
                    name=f"{product['emoji']} {product['name']}",
                    value=f"Price: {product['price']}\nStatus: {product['status']}",
                    inline=False
                )
            
            welcome_embed.add_field(
                name="Payment Methods",
                value=PAYMENT_METHODS,
                inline=False
            )
            
            welcome_embed.set_footer(text="Please tell us which template you'd like to purchase!")
            
            # Add close button
            close_view = CloseTicketView()
            await ticket_channel.send(f"{user.mention} {founder_role.mention}", embed=welcome_embed, view=close_view)
            
            await interaction.response.send_message(
                f"✅ Ticket created! Please head to {ticket_channel.mention}",
                ephemeral=True
            )
            
        except Exception as e:
            await interaction.response.send_message(
                f"❌ Error creating ticket: {str(e)}",
                ephemeral=True
            )

class ThumbnailButton(View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="Buy", style=discord.ButtonStyle.primary, emoji="🎨")
    async def buy_button(self, interaction: discord.Interaction, button: Button):
        user = interaction.user
        guild = interaction.guild
        
        # Check if user already has an active ticket
        if user.id in active_tickets:
            await interaction.response.send_message(
                "❌ You already have an active ticket! Please close your current ticket first.",
                ephemeral=True
            )
            return
        
        # Find the category
        category = discord.utils.get(guild.categories, name=THUMBNAILS_CATEGORY_NAME)
        if not category:
            await interaction.response.send_message(
                f"❌ Category '{THUMBNAILS_CATEGORY_NAME}' not found! Please contact an admin.",
                ephemeral=True
            )
            return
        
        # Find the Founder role
        founder_role = discord.utils.get(guild.roles, name=FOUNDER_ROLE_NAME)
        if not founder_role:
            await interaction.response.send_message(
                f"❌ Role '{FOUNDER_ROLE_NAME}' not found! Please contact an admin.",
                ephemeral=True
            )
            return
        
        # Create ticket channel
        channel_name = f"thumbnail-{user.name}".lower().replace(" ", "-")
        
        # Set permissions
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            founder_role: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        
        try:
            ticket_channel = await guild.create_text_channel(
                name=channel_name,
                category=category,
                overwrites=overwrites
            )
            
            # Store the active ticket
            active_tickets[user.id] = ticket_channel.id
            
            # Send welcome message in ticket
            welcome_embed = discord.Embed(
                title="🎨 Thumbnail Ticket",
                description=f"Welcome {user.mention}! A staff member will assist you shortly with your thumbnail order.",
                color=0xFF6B9D
            )
            
            welcome_embed.set_footer(text="Please describe what kind of thumbnail you'd like!")
            
            # Add close button
            close_view = CloseTicketView()
            await ticket_channel.send(f"{user.mention} {founder_role.mention}", embed=welcome_embed, view=close_view)
            
            await interaction.response.send_message(
                f"✅ Ticket created! Please head to {ticket_channel.mention}",
                ephemeral=True
            )
            
        except Exception as e:
            await interaction.response.send_message(
                f"❌ Error creating ticket: {str(e)}",
                ephemeral=True
            )

class CloseTicketView(View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="Close Ticket", style=discord.ButtonStyle.danger, emoji="🔒")
    async def close_button(self, interaction: discord.Interaction, button: Button):
        channel = interaction.channel
        
        # Check if it's a purchase or thumbnail ticket
        if not (channel.name.startswith("purchase-") or channel.name.startswith("thumbnail-")):
            await interaction.response.send_message("❌ This is not a ticket channel!", ephemeral=True)
            return
        
        # Remove from active tickets
        for user_id, channel_id in list(active_tickets.items()):
            if channel_id == channel.id:
                del active_tickets[user_id]
                break
        
        await interaction.response.send_message("🔒 Closing ticket in 5 seconds...")
        await asyncio.sleep(5)
        await channel.delete()

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    print(f'Bot ID: {bot.user.id}')

@bot.event
async def on_member_join(member):
    if not WELCOME_ENABLED:
        return
    
    guild = member.guild
    
    # Find the Member role
    member_role = discord.utils.get(guild.roles, name=MEMBER_ROLE_NAME)
    if member_role:
        try:
            await member.add_roles(member_role)
            print(f"Assigned {MEMBER_ROLE_NAME} role to {member.name}")
        except Exception as e:
            print(f"Error assigning role: {e}")
    
    # Find the welcome channel
    welcome_channel = discord.utils.get(guild.text_channels, name=WELCOME_CHANNEL_NAME)
    if welcome_channel:
        try:
            await welcome_channel.send(f"Welcome to Blox Templates {member.mention}! 🎉")
        except Exception as e:
            print(f"Error sending welcome message: {e}")

@bot.command(name='hello')
async def hello(ctx):
    await ctx.send(f'Hey {ctx.author.name}!')

@bot.command(name='ping')
async def ping(ctx):
    await ctx.send(f'Pong! {round(bot.latency * 1000)}ms')

@bot.command(name='order')
async def order(ctx):
    embed = discord.Embed(
        title="📦Blox Templates",
        description=STORE_DESCRIPTION,
        color=0x5865F2
    )
    
    # Add products
    products_text = ""
    for product in STORE_PRODUCTS:
        products_text += f"✅ {product['emoji']} **{product['name']}** - {product['price']} ({product['status']})\n"
    
    embed.add_field(
        name="All Our Products:",
        value=products_text,
        inline=False
    )
    
    embed.add_field(
        name="Payment Methods:",
        value=PAYMENT_METHODS,
        inline=False
    )
    
    embed.add_field(
        name="",
        value="Thank you for choosing Blox Templates! Our team will assist you with your purchase and provide all necessary files and documentation.",
        inline=False
    )
    
    embed.set_footer(text=SUPPORT_MESSAGE)
    
    # Add buy button
    view = BuyButton()
    await ctx.send(embed=embed, view=view)

@bot.command(name='thumbnail')
async def thumbnail(ctx):
    embed = discord.Embed(
        title="🎨 Order Thumbnails for your game!",
        color=0xFF6B9D
    )
    
    # Add thumbnail button
    view = ThumbnailButton()
    await ctx.send(embed=embed, view=view)

@bot.command(name='faq')
async def faq(ctx):
    embed = discord.Embed(
        title="❓ Frequently Asked Questions",
        description="Here are answers to some common questions about Blox Templates!",
        color=0xFFA500
    )
    
    for item in FAQ_ITEMS:
        embed.add_field(
            name=item["question"],
            value=item["answer"],
            inline=False
        )
    
    embed.set_footer(text="Still have questions? Open a ticket and we'll be happy to help!")
    
    await ctx.send(embed=embed)

@bot.command(name='welcome')
async def welcome_toggle(ctx):
    global WELCOME_ENABLED
    
    # Check if user has admin permissions
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("❌ You need administrator permissions to use this command!")
        return
    
    WELCOME_ENABLED = not WELCOME_ENABLED
    status = "enabled" if WELCOME_ENABLED else "disabled"
    
    embed = discord.Embed(
        title="🙋‍♂️ Welcome System",
        description=f"Welcome system has been **{status}**!",
        color=0x00ff00 if WELCOME_ENABLED else 0xff0000
    )
    
    if WELCOME_ENABLED:
        embed.add_field(
            name="Configuration",
            value=f"**Welcome Channel:** {WELCOME_CHANNEL_NAME}\n**Auto Role:** {MEMBER_ROLE_NAME}",
            inline=False
        )
        embed.add_field(
            name="Note",
            value="Make sure the channel and role exist in your server!",
            inline=False
        )
    
    await ctx.send(embed=embed)

@bot.command(name='terms')
async def terms(ctx):
  embed = discord.Embed(
    title="📜 Blox Templates — Terms & Conditions",
    description="By purchasing or using any product from **Blox Templates**, you agree to the following Terms & Conditions. Please read carefully before purchasing.",
    color=0x5865F2
)

embed.add_field(
    name="🔒 License & Ownership",
    value="All templates remain the exclusive property of Blox Templates. Purchasing a product grants you a non-exclusive, non-transferable license to use the template. You do not own the template and may not claim it as your own or sell it in any form.",
    inline=False
)

embed.add_field(
    name="🚫 No Reselling or Redistribution",
    value="Reselling, trading, leaking, sharing, uploading, or redistributing templates in any form is strictly prohibited. This includes public or private sharing, giving access to friends, collaborators, or developers, and selling the raw or lightly edited template. Violations result in immediate license revocation.",
    inline=False
)

embed.add_field(
    name="✅ Allowed Use",
    value="Templates may be used for personal or commercial Roblox games. Monetization is allowed. Selling a percentage of a game or revenue sharing is only permitted if clear, noticeable, and meaningful changes have been made. Minor edits such as recolors, renaming, or small tweaks do not qualify.",
    inline=False
)

embed.add_field(
    name="👥 Collaboration Responsibility",
    value="You are fully responsible for anyone who has access to your project. If a collaborator, friend, or developer leaks or redistributes the template, you will still be held liable.",
    inline=False
)

embed.add_field(
    name="💳 No Refunds",
    value="All sales are final. No refunds, chargebacks, or exchanges will be accepted under any circumstances.",
    inline=False
)

embed.add_field(
    name="⚖️ Enforcement & License Revocation",
    value="Blox Templates reserves the right to revoke access to current and future products, issue DMCA takedowns, and take further action if any part of these terms is violated.",
    inline=False
)

embed.add_field(
    name="📉 No Guarantees",
    value="All products are provided as templates. We do not guarantee performance, earnings, popularity, or compatibility with future Roblox updates.",
    inline=False
)

embed.add_field(
    name="🏷️ Credit & Claiming",
    value="If significant portions of the template remain unchanged, proper credit to Blox Templates is required. Claiming the template or its assets as entirely your own is prohibited.",
    inline=False
)

embed.add_field(
    name="🔄 Updates & Bug Fixes",
    value="Bug fixes may be provided free of charge for issues present in the original template. Updates or fixes may be refused if scripts or systems have been altered.",
    inline=False
)

embed.add_field(
    name="📋 Final Agreement",
    value="By purchasing or using any product from Blox Templates, you acknowledge and agree to all of the above Terms & Conditions.",
    inline=False
)

    
    embed.set_footer(text="By purchasing from Game Templates, you acknowledge and agree to all sections of this TOS")
    
    await ctx.send(embed=embed)

import asyncio

keep_alive()  # starts the web server in the background


print("Starting bot...")

bot.run(TOKEN)





