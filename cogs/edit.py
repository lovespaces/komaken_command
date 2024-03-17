import discord, json
from discord.ext import commands
from discord import app_commands
from typing import List

def ShowConfig(コマンド):
    emb = discord.Embed()
    view = discord.ui.View()
    with open('./data.json', encoding="utf-8") as f:
        j = json.load(f)
    try:
        data = j["command_data"]["name." + コマンド]
        json_str = json.dumps(data, indent=2, ensure_ascii=False)
        emb.description = "`" + コマンド + "`の編集画面です:\n```json\n" + str(json_str) + "```\n### ❗必ずどの値がどのようなものなのかを把握してから編集・追加をしてください。\n`❓ヘルプメッセージ`から確認することができます"
        view.add_item(discord.ui.Button(style=discord.ButtonStyle.green, label="ヘルプメッセージ", emoji="❓", custom_id="help_message"))
        view.add_item(discord.ui.Button(style=discord.ButtonStyle.blurple, label="新しくコマンドを追加", emoji="✨", custom_id="create_new_command"))
        view.add_item(discord.ui.Button(style=discord.ButtonStyle.gray, label="エディションで構文が変わるか(is_diff)", emoji="\N{ANTICLOCKWISE DOWNWARDS AND UPWARDS OPEN CIRCLE ARROWS}", custom_id="edit_isdiff." + コマンド))
        view.add_item(discord.ui.Button(style=discord.ButtonStyle.gray, label="対応バージョンを変更(ver)", emoji="🔢", custom_id="edit_edition." + コマンド + ".ver"))
        view.add_item(discord.ui.Button(style=discord.ButtonStyle.gray, label="詳細を変更(desc)", emoji="✏️", custom_id="edit_change_description." + コマンド))
        view.add_item(discord.ui.Button(style=discord.ButtonStyle.gray, label="使用例変更(exmp)", emoji="💎", custom_id="edit_edition." + コマンド + ".exmp"))
        view.add_item(discord.ui.Button(style=discord.ButtonStyle.gray, label="引数変更(options)", emoji="📑", custom_id="edit_edition." + コマンド + ".options"))
        emb.color = 0xbfb4bb
    except KeyError:
        emb.description = f"指定されたキーが見つかりません: `{コマンド}`"
    except Exception as e:
        emb.color = 0xff1515
        emb.title = "エラー"
        emb.description = "エラーが発生しました。原因がわからなかったらスクショして <@305607244945293314> にスクショと一緒にメンションをすっ飛ばしてください。よろしくお願いします。\n```" + str(e) + "```"
    return emb, view

class AddOrEdit(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="edit", description="コマンドの情報を追加もしくは編集を行います。")
    @app_commands.describe(コマンド='編集をするコマンドを選んでください')
    async def add(self, inter: discord.Interaction, コマンド: str) -> None:
        await inter.response.defer(thinking=True, ephemeral=True)
        emb, view = ShowConfig(コマンド)
        await inter.followup.send(embed = emb, view = view)
    
    @add.autocomplete('コマンド')
    async def add_autocomplete(
        self,
        inter:discord.Interaction,
        current:str
    ) -> List[app_commands.Choice[str]]:
        with open('./data.json', encoding="utf-8") as f:
            j = json.load(f)
        data = j["commands"]
        return [
            app_commands.Choice(name=query,value=query)
            for query in data if current.lower() in query.lower()
        ]

async def setup(bot):
    await bot.add_cog(AddOrEdit(bot))