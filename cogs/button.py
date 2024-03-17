import discord, json
from discord.ext import commands
from .search import CommandInfo
from .edit import ShowConfig

class Modal(discord.ui.Modal):
    def __init__(self, questions: list):
        super().__init__(title="入力フォーム", timeout=None)
        self.questions = questions
        for i in questions:
            self.add_item(i)
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()

class Button(commands.Cog):
    def __init__(self, bot:commands.Bot) -> None:
        self.bot = bot
    
    @commands.Cog.listener('on_interaction')
    async def detect(self, inter: discord.Interaction):
        try:
            if inter.data['component_type'] == 2:
                await button(inter)
        except KeyError:
            pass

async def button(inter: discord.Interaction):
    custom_id = inter.data['custom_id']
    with open('./data.json', encoding="utf-8") as f:
        j = json.load(f)
    if custom_id == "change_edition":
        original_emb = inter.message.embeds[0]
        await inter.response.defer()
        コマンド = str(original_emb.title)
        n = False
        if str(original_emb.footer.text) == "Java Edition":
            e = "Bedrock"
        elif str(original_emb.footer.text) == "Bedrock Edition":
            e = "Java"
        emb, view = CommandInfo(コマンド, e, n)
        await inter.edit_original_response(embed = emb, view = view)
    # edit pages
    elif custom_id == "help_message":
        example_json = j["example"]["name.command_name"]
        json_str = json.dumps(example_json, indent=2, ensure_ascii=False)
        emb = discord.Embed(color=0x333b78, description="このボットでは以下のようなデータを使用しています。\n```json\n" + str(json_str) + "```\n**※もしどちらかのエディションにしかコマンドが存在しない場合は存在しないエディションのverの項目にnullと入力し、is_diffをFalseにしてください。**\n**※両エディションの構文が変わらない場合はis_diffをFalseにしてください。尚、</search:1218753514684289098> での検索結果ではJE版に書かれているデータが表示されます。**\n**※引数の編集の際、元々記載している通りに書いてもらうのが理想的ですが、難しい場合は別の書き方をしてもらっても構いません。**\n↑に関して、元々の書き方はマイクラのFandomウィキページに書かれてる書き方を利用しています。\nウィキページ: [`英語`](https://minecraft.fandom.com/wiki/Commands) / [`日本語`](https://minecraft.fandom.com/ja/wiki/コマンド)")
        await inter.response.send_message(embed = emb, ephemeral=True)
    elif "edit_change_description" in custom_id:
        sp = custom_id.split(".")
        コマンド = str(sp[1])
        data = j["command_data"]["name." + コマンド]
        old_data = data["desc"]
        questions = [discord.ui.TextInput(custom_id="changes_desc", label="詳細を入力してください", required=True, default=str(old_data), style=discord.TextStyle.long, max_length=1024)]
        modal = Modal(questions)
        await inter.response.send_modal(modal)
        await modal.wait()
        new_data = modal.questions[0].value
        data["desc"] = str(new_data)
        with open('./data.json', "w", encoding="utf-8") as f:
            json.dump(j, f, indent=4, ensure_ascii=False)
        emb, view = ShowConfig(コマンド)
        await inter.edit_original_response(embed = emb, view = view)
        log_emb = discord.Embed(description="**変更が行われました**\n`" + コマンド + "` の `desc` にて:\n \n変更者: " + inter.user.mention + "\n`OLD:` ```" + str(old_data) + "```\n`NEW:` ```" + str(new_data) + "```")
        await inter.channel.send(embed = log_emb)
    elif "edit_edition" in custom_id:
        sp = custom_id.split(".")
        data = j["command_data"]["name." + str(sp[1])][str(sp[2])]
        data_je = data["je"]
        data_be = data["be"]
        コマンド = str(sp[1])
        questions = [discord.ui.TextInput(default=str(data_je), label="JE版", required=False), discord.ui.TextInput(default=str(data_be), label="BE版", required=False)]
        modal = Modal(questions)
        await inter.response.send_modal(modal)
        await modal.wait()
        new_data_je = modal.questions[0].value
        new_data_be = modal.questions[1].value
        if sp[2] == "ver":
            if modal.questions[0].value == "null":
                new_data_je = None
            elif modal.questions[1].value == "null":
                new_data_be = None
        data["je"] = new_data_je
        data["be"] = new_data_be
        with open('./data.json', "w", encoding="utf-8") as f:
            json.dump(j, f, indent=4, ensure_ascii=False)
        emb, view = ShowConfig(コマンド)
        await inter.edit_original_response(embed = emb, view = view)
        log_emb = discord.Embed(description="**変更が行われました**\n`" + コマンド + "` の `" + str(sp[2]) + "`にて:\n \n変更者: " + inter.user.mention + f"\n`OLD:` ```JE: {str(data_je)}\nBE: {str(data_be)}```\n`NEW:` ```JE: {str(new_data_je)}\nBE: {str(new_data_be)}```")
        await inter.channel.send(embed = log_emb)
    elif "edit_isdiff" in custom_id:
        sp = custom_id.split(".")
        コマンド = str(sp[1])
        data = j["command_data"]["name." + コマンド]
        await inter.response.defer()
        description = "**変更が行われました**\n`" + コマンド + "` の `" + "is_diff" + "`にて:\n \n変更者: " + inter.user.mention + "\n`OLD`: ```"
        if data["is_diff"] is True:
            data["is_diff"] = False
            await inter.followup.send("**:exclamation: どちらかのエディション限定のコマンドである場合は「対応バージョンを変更」ボタンからコマンドが存在しないエディションの値をnullに設定してください。**", ephemeral=True)
            description += "True```\n`NEW:` ```False```"
        else:
            data["is_diff"] = True
            data["ver"] = {
                "je": "-" if data["ver"]["je"] is None else data["ver"]["je"],
                "be": "-" if data["ver"]["be"] is None else data["ver"]["be"]
            }
            await inter.followup.send("**:exclamation: 片方のエディションのコマンド情報がない場合はできる限りデータを入れてください。**", ephemeral=True)
            description += "False```\n`NEW:` ```True```"
        with open("./data.json", "w", encoding="utf-8") as f:
            json.dump(j, f, indent=4, ensure_ascii=False)
        emb, view = ShowConfig(コマンド)
        await inter.edit_original_response(embed = emb, view = view)
        log_emb = discord.Embed(description=description)
        await inter.channel.send(embed=log_emb)
    elif custom_id == "create_new_command":
        questions = [discord.ui.TextInput(label="コマンド名", required=True, style=discord.TextStyle.short, placeholder="スラッシュを外して入力してください"), discord.ui.TextInput(label="詳細", required=False, style=discord.TextStyle.long, min_length=5, max_length=1024, placeholder="入力せずに登録すると\"-\"と登録されます")]
        modal = Modal(questions)
        await inter.response.send_modal(modal)
        await modal.wait()
        data = j["command_data"]
        commands = j["commands"]
        if not "name." + modal.questions[0].value in j["command_data"]:
            if modal.questions[1].value == "":
                desc = "-"
            else:
                desc = modal.questions[1].value
            data["name." + modal.questions[0].value] = json_data = {
                "is_diff": False,
                "ver": {
                    "je": "-",
                    "be": "-"
                },
                "desc": desc,
                "exmp": {
                    "je": "-",
                    "be": "-"
                },
                "options": {
                    "je": "-",
                    "be": "-"
                }
            }
            commands.append(modal.questions[0].value)
            commands = sorted(commands)
            data = dict(sorted(data.items()))
            j["commands"] = commands
            j["command_data"] = data
            json_data = json.dumps(json_data, indent=2, ensure_ascii=False)
            with open('./data.json', "w", encoding="utf-8") as f:
                json.dump(j, f, indent=4, ensure_ascii=False)
            emb, view = ShowConfig(コマンド = modal.questions[0].value)
            await inter.followup.send(embed = emb, view = view, ephemeral=True)
            log_emb = discord.Embed(description="新しいコマンドが追加されました\nコマンド名: `" + modal.questions[0].value + "`\n \n作成者: " + inter.user.mention + "\n```json\n" + str(json_data) + "```")
            await inter.channel.send(embed = log_emb)
        else:
            await inter.followup.send("既にコマンドが存在しています！", ephemeral=True)            

async def setup(bot):
    await bot.add_cog(Button(bot))
