import discord
from discord.ext import commands
import json, os, random, asyncio

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

FILE = "bank_real.json"
BANK_CHANNEL_ID = None # بنحطه بعدين

def load():
    if not os.path.exists(FILE): return {}
    with open(FILE, "r", encoding="utf-8") as f: return json.load(f)
def save(data):
    with open(FILE, "w", encoding="utf-8") as f: json.dump(f, f, ensure_ascii=False, indent=4)

def gen_transfer_id():
    return str(random.randint(100000000, 999999999))

# ===== الواجهة الرئيسية =====
class BankPanel(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="انشاء حساب بنكي 🏦", style=discord.ButtonStyle.green, custom_id="create_acc")
    async def create_acc(self, interaction: discord.Interaction, button: discord.ui.Button):
        data = load()
        uid = str(interaction.user.id)
        if uid in data:
            await interaction.response.send_message("❌ عندك حساب already! اضغط فتح البنك", ephemeral=True)
            return

        await interaction.response.send_message("✅ رحت لك خاص، كمل هناك", ephemeral=True)

        try:
            dm = await interaction.user.create_dm()
            await dm.send("🏦 **مرحبا في بنك السيرفر**\nاكتب **اسمك الثلاثي** الكامل:")

            def check(m): return m.author.id == interaction.user.id and isinstance(m.channel, discord.DMChannel)

            name_msg = await bot.wait_for("message", check=check, timeout=120)
            full_name = name_msg.content

            await dm.send("🔒 الان اكتب **الرقم السري** المكون من 4 ارقام فقط (مثال: 1234):")
            pin_msg = await bot.wait_for("message", check=check, timeout=120)

            if not pin_msg.content.isdigit() or len(pin_msg.content)!= 4:
                await dm.send("❌ لازم 4 ارقام فقط! اضغط انشاء حساب من جديد.")
                return

            transfer_id = gen_transfer_id()
            data[uid] = {
                "name": full_name,
                "pin": pin_msg.content,
                "transfer_id": transfer_id,
                "wallet": 0,
                "bank": 0
            }
            save(data)
            await dm.send(f"✅ **تم انشاء حسابك البنكي بنجاح!**\n👤 الاسم: {full_name}\n🔢 رقم التحويل الخاص بك: `{transfer_id}`\n🔒 رقمك السري: `{pin_msg.content}`\n\n> احتفظ برقم التحويل، الناس تحول لك عليه.")

        except asyncio.TimeoutError:
            await interaction.user.send("⏳ انتهى الوقت، اضغط الزر مرة ثانية.")
        except Exception as e:
            print(e)

    @discord.ui.button(label="فتح البنك 🔓", style=discord.ButtonStyle.blurple, custom_id="open_acc")
    async def open_acc(self, interaction: discord.Interaction, button: discord.ui.Button):
        data = load()
        uid = str(interaction.user.id)
        if uid not in data:
            await interaction.response.send_message("❌ ما عندك حساب، اضغط انشاء حساب بنكي اول", ephemeral=True)
            return

        await interaction.response.send_message("✅ رحت لك خاص", ephemeral=True)

        try:
            dm = await interaction.user.create_dm()
            await dm.send("🔐 **فتح البنك**\nاكتب رقمك السري المكون من 4 ارقام:")

            def check(m): return m.author.id == interaction.user.id and isinstance(m.channel, discord.DMChannel)
            pin_msg = await bot.wait_for("message", check=check, timeout=60)

            if pin_msg.content!= data[uid]["pin"]:
                await dm.send("❌ الرقم السري غلط!")
                return

            # تم الدخول - نعرض له الاوامر
            embed = discord.Embed(title=f"🏦 مرحبا {data[uid]['name']}", color=0x00ff00)
            embed.add_field(name="💰 رصيدك", value=f"محفظة: {data[uid]['wallet']}\nبنك: {data[uid]['bank']}", inline=False)
            embed.add_field(name="📜 الاوامر في الخاص", value="`رصيدي`\n`رقم التحويل`\n`تحويل [رقم التحويل] [المبلغ]`\nمثال: `تحويل 184639752 500`", inline=False)
            embed.set_footer(text=f"رقم تحويلك: {data[uid]['transfer_id']}")
            await dm.send(embed=embed)

            # نستمع لاوامره في الخاص لمدة 5 دقايق
            for _ in range(10):
                msg = await bot.wait_for("message", check=check, timeout=300)
                content = msg.content.strip()

                if content == "رصيدي" or content == "معرفة رصيدي":
                    d = load()[uid]
                    await dm.send(f"💳 **رصيدك**\n🏦 البنك: {d['bank']}\n💵 الكاش: {d['wallet']}\n💎 الكلي: {d['bank']+d['wallet']}")

                elif content == "رقم التحويل" or "رقم التحويل الخاص بي" in content:
                    d = load()[uid]
                    await dm.send(f"🔢 رقم التحويل الخاص بك هو: `{d['transfer_id']}`\nاعطيه للي بيحول لك.")

                elif content.startswith("تحويل"):
                    try:
                        parts = content.split()
                        target_transfer = parts[1]
                        amount = int(parts[2])
                        db = load()
                        # دور صاحب رقم التحويل
                        target_uid = None
                        for k,v in db.items():
                            if v["transfer_id"] == target_transfer:
                                target_uid = k
                                break
                        if not target_uid:
                            await dm.send("❌ رقم التحويل غير موجود")
                            continue
                        if target_uid == uid:
                            await dm.send("❌ ما تقدر تحول لنفسك")
                            continue
                        if db[uid]["bank"] < amount:
                            await dm.send(f"❌ رصيدك في البنك ما يكفي، عندك {db[uid]['bank']}")
                            continue

                        db[uid]["bank"] -= amount
                        db[target_uid]["bank"] += amount
                        save(db)
                        await dm.send(f"✅ تم تحويل {amount} الى {db[target_uid]['name']} ({target_transfer})")
                        try:
                            user_obj = await bot.fetch_user(int(target_uid))
                            await user_obj.send(f"💸 جاك تحويل {amount} من {db[uid]['name']}")
                        except: pass

                    except:
                        await dm.send("❌ الصيغة غلط! اكتب: `تحويل 184639752 500`")

        except asyncio.TimeoutError:
            await dm.send("⏳ انتهت جلسة البنك، اضغط فتح البنك مرة ثانية")
        except Exception as e:
            print(e)

# امر تثبيت الرسالة في روم مقفل
@bot.command(name="تثبيت_البنك")
@commands.has_permissions(administrator=True)
async def setup(ctx):
    global BANK_CHANNEL_ID
    BANK_CHANNEL_ID = ctx.channel.id
    embed = discord.Embed(title="🏦 نظام البنك الرسمي - Real Bank", description="**مرحبا بك في البنك المركزي**\n\nكل تعاملاتك سرية 100% في الخاص\n\n🔹 اضغط **انشاء حساب بنكي** لفتح حساب جديد\n🔹 اضغط **فتح البنك** للدخول لحسابك\n\n> الفلوس فقط من الادارة", color=0x2b2d31)
    embed.set_footer(text="نظام بنكي واقعي و آمن")
    await ctx.send(embed=embed, view=BankPanel())

# امر الادارة يعطي فلوس
@bot.command(name="عطاء")
@commands.has_permissions(administrator=True)
async def عطاء(ctx, member: discord.Member, amount: int):
    data = load()
    uid = str(member.id)
    if uid not in data:
        await ctx.send("❌ الشخص ما عنده حساب بنكي")
        return
    data[uid]["bank"] += amount
    save(data)
    await ctx.send(f"✅ تم اضافة {amount} لحساب {data[uid]['name']} في البنك")
    try:
        await member.send(f"💰 الادارة اضافت لك {amount} في حسابك البنكي!")
    except: pass

@bot.event
async def on_ready():
    bot.add_view(BankPanel())
    print(f"البنك جاهز: {bot.user}")

bot.run(os.getenv("TOKEN"))
