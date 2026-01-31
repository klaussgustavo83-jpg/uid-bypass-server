import os
import json
import time
import asyncio
import discord
from discord import app_commands

CLEAN_INTERVAL = 60

# ============================================
#  ____            _           _  __  ____   __
# |  _ \ _ __ ___ (_) ___  ___| |_\ \/ /\ \ / /
# | |_) | '__/ _ \| |/ _ \/ __| __|\  /  \ V / 
# |  __/| | | (_) | |  __/ (__| |_ /  \   | |  
# |_|   |_|  \___// |\___|\___|\__/_/\_\  |_|  
#               |__/                            
#
# Project  : Project XY Bypass
# Version  : v1.0.0
# Status   : Stable Release
# Author   : Quantum
# Discord  : https://discord.gg/nsXdFpE69b
# ============================================

def load_whitelist(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return {str(k): int(v) for k, v in json.load(f).items()}
    except:
        return {}


def save_whitelist(wl, path):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump({str(k): int(v) for k, v in wl.items()}, f, separators=(",", ":"), ensure_ascii=False)
    os.replace(tmp, path)


class WhitelistCog(app_commands.Group):
    def __init__(self, bot_name, file_path):
        super().__init__(name="whitelist", description="Manage whitelist")
        self.path = file_path
        self.wl = load_whitelist(self.path)
        self.bot_name = bot_name

    async def sexy_embed(self, title, desc, color=0x9B59B6):
        e = discord.Embed(title=f"✨ {title} ✨", description=desc, color=color)
        e.set_footer(text=f"{self.bot_name} • Whitelist Manager ⚡", icon_url="https://cdn.discordapp.com/emojis/903069137422565406.gif")
        e.set_thumbnail(url="https://cdn.discordapp.com/attachments/903069137422565406/1182390234879942746/neon_icon.gif")
        e.timestamp = discord.utils.utcnow()
        return e


# ============================================
#  ____            _           _  __  ____   __
# |  _ \ _ __ ___ (_) ___  ___| |_\ \/ /\ \ / /
# | |_) | '__/ _ \| |/ _ \/ __| __|\  /  \ V / 
# |  __/| | | (_) | |  __/ (__| |_ /  \   | |  
# |_|   |_|  \___// |\___|\___|\__/_/\_\  |_|  
#               |__/                            
#
# Project  : Project XY Bypass
# Version  : v1.0.0
# Status   : Stable Release
# Author   : Quantum
# Discord  : https://discord.gg/nsXdFpE69b
# ============================================

    @app_commands.command(name="add", description="Add user to whitelist")
    async def add(self, interaction: discord.Interaction, uid: str, hours: int):


        expire = int(time.time()) + hours * 3600
        self.wl[str(uid)] = expire
        save_whitelist(self.wl, self.path)

        msg = f"🆔 **User ID:** `{uid}`\n⏳ **Expires:** <t:{expire}:F> (<t:{expire}:R>)"
        await interaction.response.send_message(embed=await self.sexy_embed("✅ Added to Whitelist", msg, 0x2ECC71))

    @app_commands.command(name="remove", description="Remove a user from whitelist")
    async def remove(self, interaction: discord.Interaction, uid: str):

        if str(uid) not in self.wl:
            await interaction.response.send_message(embed=await self.sexy_embed("❔ Not Found", f"`{uid}` is not in whitelist.", 0xF1C40F))
            return

        del self.wl[str(uid)]
        save_whitelist(self.wl, self.path)
        await interaction.response.send_message(embed=await self.sexy_embed("🗑️ Removed", f"`{uid}` removed from whitelist.", 0xE67E22))

    @app_commands.command(name="list", description="Show all whitelisted users")
    async def list(self, interaction: discord.Interaction):
        if not self.wl:
            await interaction.response.send_message(embed=await self.sexy_embed("📜 Whitelist Empty", "Nobody is currently whitelisted.", 0x95A5A6))
            return

        lines = [f"💠 `{uid}` → <t:{ts}:R>" for uid, ts in sorted(self.wl.items(), key=lambda x: x[1])]
        desc = "\n".join(lines)
        await interaction.response.send_message(embed=await self.sexy_embed("👑 Whitelisted Users", desc, 0x1ABC9C))

    @app_commands.command(name="check", description="Check if a user is whitelisted")
    async def check(self, interaction: discord.Interaction, uid: str):
        ts = self.wl.get(str(uid))
        if not ts:
            await interaction.response.send_message(embed=await self.sexy_embed("❌ Not Whitelisted", f"`{uid}` is **not** in whitelist.", 0xE74C3C))
            return
        if ts <= int(time.time()):
            del self.wl[str(uid)]
            save_whitelist(self.wl, self.path)
            await interaction.response.send_message(embed=await self.sexy_embed("⌛ Expired", f"`{uid}` was expired and removed.", 0xE67E22))
            return
        await interaction.response.send_message(embed=await self.sexy_embed("✅ Active", f"`{uid}` is whitelisted until <t:{ts}:F>.", 0x2ECC71))


async def cleaner_task(group):
    while True:
        now = int(time.time())
        expired = [uid for uid, ts in list(group.wl.items()) if ts <= now]
        for uid in expired:
            del group.wl[uid]
        if expired:
            save_whitelist(group.wl, group.path)
        await asyncio.sleep(CLEAN_INTERVAL)


async def start_bot(token, name, file_path):
    intents = discord.Intents.default()
    client = discord.Client(intents=intents)
    tree = app_commands.CommandTree(client)
    wl = WhitelistCog(name, file_path)

    @client.event
    async def on_ready():
        tree.add_command(wl)
        await tree.sync()
        client.loop.create_task(cleaner_task(wl))
        print(f"💎 {name} logged in as {client.user} ({client.user.id})")

    # Retry com delay
    for attempt in range(3):
        try:
            await client.start(token)
            break
        except discord.HTTPException as e:
            if "429" in str(e):
                print(f"Rate limited, tentativa {attempt + 1}/3. Aguardando 60s...")
                await asyncio.sleep(60)
            else:
                raise


    @client.event
    async def on_ready():
        tree.add_command(wl)
        await tree.sync()
        client.loop.create_task(cleaner_task(wl))
        print(f"💎 {name} logged in as {client.user} ({client.user.id})")

    await client.start(token)


async def main(): 
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        print("❌ DISCORD_TOKEN não encontrado nas variáveis de ambiente!")
        return


    await asyncio.gather(     
        start_bot(token, "💎 Bot Two", "whitelist_ind.json"),
    )

asyncio.run(main())
