import asyncio
import json
import os

import discord
from discord.ext import commands

TOKEN = os.getenv("MTU2MjEzMzUxNDE1MTkyNzgxOA.GIVX3M.BI_QCDQFdVvLox72HNTC1HbuUon6a8vr4DpSEY")
PREFIX = "&"
DATA_FILE = "roles.json"

intents = discord.Intents.default()
intents.members = True          # à activer dans le portail développeur
intents.message_content = True  # idem

bot = commands.Bot(command_prefix=PREFIX, intents=intents)


def load():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}


def save(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)


def get_role(guild):
    role_id = load().get(str(guild.id))
    return guild.get_role(role_id) if role_id else None


@bot.event
async def on_ready():
    print(f"Connecté en tant que {bot.user}")


@bot.command(name="adddmall")
@commands.has_permissions(administrator=True)
async def adddmall(ctx, role: discord.Role):
    """Définit le rôle abonné aux DM."""
    data = load()
    data[str(ctx.guild.id)] = role.id
    save(data)
    await ctx.send(
        f"Rôle {role.mention} défini. Les membres peuvent le prendre avec "
        f"`{PREFIX}dmjoin` et le retirer avec `{PREFIX}dmleave`.",
        allowed_mentions=discord.AllowedMentions.none(),
    )


@bot.command(name="dmjoin")
async def dmjoin(ctx):
    role = get_role(ctx.guild)
    if not role:
        return await ctx.send("Aucun rôle n'a été défini.")
    await ctx.author.add_roles(role)
    await ctx.send("✅ Tu recevras les DM du serveur.")


@bot.command(name="dmleave")
async def dmleave(ctx):
    role = get_role(ctx.guild)
    if not role:
        return await ctx.send("Aucun rôle n'a été défini.")
    await ctx.author.remove_roles(role)
    await ctx.send("❌ Tu ne recevras plus de DM.")


@bot.command(name="dm")
@commands.has_permissions(administrator=True)
async def dm(ctx, *, texte: str):
    """Envoie le texte en DM aux membres qui ont le rôle."""
    role = get_role(ctx.guild)
    if not role:
        return await ctx.send(f"Définis d'abord un rôle avec `{PREFIX}adddmall @role`.")

    membres = [m for m in role.members if not m.bot]
    await ctx.send(f"Envoi à {len(membres)} membre(s)...")

    ok, echec = 0, 0
    for m in membres:
        try:
            await m.send(f"📢 **{ctx.guild.name}**\n{texte}\n\n"
                         f"*Pour ne plus recevoir ces messages : `{PREFIX}dmleave` sur le serveur.*")
            ok += 1
        except (discord.Forbidden, discord.HTTPException):
            echec += 1
        await asyncio.sleep(2)  # évite le rate limit / le ban

    await ctx.send(f"Terminé : {ok} envoyé(s), {echec} échec(s) (DM fermés).")


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("Tu dois être administrateur.")
    elif isinstance(error, (commands.MissingRequiredArgument, commands.BadArgument)):
        await ctx.send("Utilisation incorrecte, vérifie la commande.")
    else:
        raise error


bot.run(TOKEN)
