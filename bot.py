import discord
from discord.ext import commands
import os

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

class IdentityModal(discord.ui.Modal, title="إنشاء الهوية"):
    name = discord.ui.TextInput(label="اسم ثلاثي", placeholder="مثال: عبدالله محمد احمد", required=True)
    age = discord.ui.TextInput(label="العمر", placeholder="25", required=True, max_length=2)
    birth_year = discord.ui.TextInput(label="عام الم
