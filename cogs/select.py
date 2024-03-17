import discord, json
from discord.ext import commands
from .search import CommandInfo

class Select(commands.Cog):
    def __init__(self, bot:commands.Bot) -> None:
        self.bot = bot
    
    @commands.Cog.listener('on_interaction')
    async def detect(self, inter: discord.Interaction):
        try:
            if inter.data['component_type'] == 3:
                await select(inter)
        except KeyError:
            pass

async def select(inter: discord.Interaction):
    custom_id = inter.data['custom_id']
    values = inter.data['values']
    if custom_id == "select_commands":
        await inter.response.defer(thinking=True, ephemeral=False)
        with open('./data.json', encoding="utf-8") as f:
            j = json.load(f)
        e = "Java"
        n = False
        data = j["command_data"]["name." + str(values[0])]
        if data["ver"]["je"] == None:
            e = "Bedrock"
            n = True
        elif data["ver"]["be"] == None:
            e = "Java"
            n = True
        コマンド = str(values[0])
        emb, view = CommandInfo(コマンド, e, n)
        await inter.followup.send(embed = emb, view = view)

async def setup(bot):
    await bot.add_cog(Select(bot))