import discord, json, difflib
from discord.ext import commands
from discord import app_commands
from typing import List

def CommandInfo(コマンド, e, n):
    emb = discord.Embed(title="")
    view = discord.ui.View()
    with open('./data.json', encoding="utf-8") as f:
        j = json.load(f)
    data = j["command_data"]
    try:
        command = data["name." + コマンド]
        emb.color = 0xaafe79
        emb.title = コマンド
        description = "`/" + コマンド + "` の検索結果です。"
        if e == "Java":
            emb.add_field(name="バージョン等", value="エディション: `Java Edition`\nバージョン: `" + command["ver"]["je"] + "`")
            emb.add_field(name="使用例", value="```" + command["exmp"]["je"] + "```", inline=False)
            emb.add_field(name="引数", value="```" + command["options"]["je"] + "```", inline=False)
        elif e == "Bedrock":
            emb.add_field(name="バージョン等", value="エディション: `Bedrock Edition`\nバージョン: `" + command["ver"]["be"] + "`")
            emb.add_field(name="使用例", value="```" + command["exmp"]["be"] + "```", inline=False)
            emb.add_field(name="引数", value="```" + command["options"]["be"] + "```", inline=False)
        else:
            return
        emb.add_field(name="詳細", value="```" + command["desc"] + "```", inline=False)
        emb.set_footer(text="両エディションとも同じ構文で利用ができます。")
        if n == True:
            emb.set_footer(text="もう片方のエディションには実装されていません。")
        if command["is_diff"] == True:
            description += "\n### このコマンドはJEとBEで構文が違います！\n下のボタンからJEとBEの切り替えが可能です。\n \n" + "Wiki: [英語](https://minecraft.fandom.com/wiki/Commands/" + コマンド + ") / [日本語](https://minecraft.fandom.com/ja/wiki/コマンド/" + コマンド + ")"
            change_button = discord.ui.Button(label="切り替え", custom_id="change_edition", style=discord.ButtonStyle.gray)
            view.add_item(change_button)
            emb.set_footer(text=e + " Edition")
        emb.description = description
    except Exception as e:
        emb.color = 0xff1515
        emb.description = "## データが足りません\n検索したワード: `" + コマンド + "`\nデータ: " + str(command) + "\n" + str(e)
    return emb, view

class Search(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="search", description="コマンドを検索し、結果を表示します。")
    @app_commands.describe(コマンド="入力すると候補が出現します。")
    async def search(self, inter:discord.Interaction, コマンド: str) -> None:
        await inter.response.defer(thinking=True, ephemeral=False)
        with open('./data.json', encoding="utf-8") as f:
            j = json.load(f)
        e = "Java"
        n = False
        try:
            data = j["command_data"]["name." + コマンド]
            if data["ver"]["je"] == None:
                e = "Bedrock"
                n = True
            elif data["ver"]["be"] == None:
                e = "Java"
                n = True
            emb, view = CommandInfo(コマンド, e, n)
        except Exception as e:
            emb = discord.Embed()
            view = discord.ui.View()
            select_list = []
            similar = difflib.get_close_matches(コマンド, j["commands"])
            if similar:
                for w in similar:
                    select_list.append(discord.SelectOption(label=w, value=w))
                select = discord.ui.Select(custom_id="select_commands", placeholder="コマンドを選んでください", options=select_list)
                view.add_item(select)
                emb.description = "## 類似するコマンドが見つかりました。\n以下の選択肢から類似したコマンドの詳細が見れます。"
            else:
                emb.color = 0xff1515
                emb.description = "## コマンドが見つかりませんでした\n検索したワード: `" + コマンド + "`"
                emb.set_footer(text="コマンド検索では、コマンドを入力すると候補が表示されます。そこから検索すると結果がでるかも？")
        await inter.followup.send(embed = emb, view = view)
    
    @search.autocomplete('コマンド')
    async def search_autocomplete(
        self,
        inter:discord.Interaction,
        current:str
    ) -> List[app_commands.Choice[str]]:
        with open('./data.json', encoding="utf-8") as f:
            j = json.load(f)
        data = j["commands"]
        return [
            app_commands.Choice(name=query, value=query)
            for query in data if current.lower() in query.lower()
        ]
    
async def setup(bot):
    await bot.add_cog(Search(bot))