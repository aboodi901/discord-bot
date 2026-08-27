import discord
from discord.ext import commands
import os

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

class IdentityModal(discord.ui.Modal, title="إنشاء الهوية"):
    name = discord.ui.TextInput(label="الاسم الثلاثي", placeholder="مثال: عبدالله محمد احمد", required=True)
    age = discord.ui.TextInput(label="العمر", placeholder="مثال: 25", required=True)
    birth_year = discord.ui.TextInput(label="عام الميلاد", placeholder="مثال: 1998", required=True)
    birth_place = discord.ui.TextInput(label="مكان الميلاد", placeholder="ساندي / بوليتو / لوس", required=True)
    id_number = discord.ui.TextInput(label="رقم الهوية", placeholder="مثال: 1001", required=True)

    async def on_submit(self, interaction: discord.Interaction):
        embed = discord.Embed(title="🪪 طلب هوية جديدة", color=0x5865F2, description=f"تم تقديم طلب بواسطة {interaction.user.mention}")
        embed.add_field(name="👤 الاسم", value=str(self.name), inline=False)
        embed.add_field(name="🎂 العمر", value=str(self.age), inline=True)
        embed.add_field(name="📅 سنة الميلاد", value=str(self.birth_year), inline=True)
        embed.add_field(name="📍 مكان الميلاد", value=str(self.birth_place), inline=True)
        embed.add_field(name="🆔 رقم الهوية", value=str(self.id_number), inline=False)
        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        
        await interaction.response.send_message("✅ تم ارسال هويتك للإدارة بنجاح!", ephemeral=True)
        await interaction.channel.send(embed=embed)

class IdentityView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="إنشاء الهوية 🪪", style=discord.ButtonStyle.blurple, custom_id="create_id_btn")
    async def create_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(IdentityModal())

@bot.event
async def on_ready():
    print(f"✅ البوت اشتغل: {bot.user}")
    bot.add_view(IdentityView())
    try:
        synced = await bot.tree.sync()
        print(f"تم مزامنة {len(synced)} امر")
    except Exception as e:
        print(e)

@bot.tree.command(name="setup_id", description="ارسال لوحة نظام الهويات")
async def setup_id(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ لازم تكون ادمن", ephemeral=True)
        return
    
    embed = discord.Embed(
        title="🪪 نظام الهويات",
        description="اضغط الزر بالأسفل لإنشاء هويتك.\n\n**المطلوب:**\n• اسم ثلاثي\n• العمر\n• عام الميلاد\n• مكان الميلاد\n• رقم الهوية\n\n**أماكن الميلاد المتاحة:**\n`ساندي` • `بوليتو` • `لوس`\n\n⚠️ يُمنع إنشاء أكثر من هوية للشخص نفسه",
        color=0x2B2D31
    )
    await interaction.channel.send(embed=embed, view=IdentityView())
    await interaction.response.send_message("✅ تم ارسال لوحة الهوية", ephemeral=True)

bot.run(os.getenv("TOKEN"))
