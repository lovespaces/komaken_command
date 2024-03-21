import discord, json, difflib
from discord import app_commands
from typing import List

intents = discord.Intents.all()
client = discord.Client(intents = intents)
tree = discord.app_commands.CommandTree(client)
gld = discord.Object(id=1130363081428582491)

def CommandInfo(コマンド, e, n):
    emb = discord.Embed(title="")
    view = discord.ui.View()
    with open("./data.json", encoding="utf-8") as f:
        j = json.load(f)
    data = j["command_data"]
    try:
        command = data["name." + コマンド]
        emb.color = 0xAAFE79
        emb.title = コマンド
        description = "`/" + コマンド + "` の検索結果です。"
        if e == "Java":
            emb.add_field(
                name="バージョン等",
                value="エディション: `Java Edition`\nバージョン: `"
                + command["ver"]["je"]
                + "`",
            )
            emb.add_field(
                name="使用例", value="```" + command["exmp"]["je"] + "```", inline=False
            )
            emb.add_field(
                name="引数",
                value="```" + command["options"]["je"] + "```",
                inline=False,
            )
        elif e == "Bedrock":
            emb.add_field(
                name="バージョン等",
                value="エディション: `Bedrock Edition`\nバージョン: `"
                + command["ver"]["be"]
                + "`",
            )
            emb.add_field(
                name="使用例", value="```" + command["exmp"]["be"] + "```", inline=False
            )
            emb.add_field(
                name="引数",
                value="```" + command["options"]["be"] + "```",
                inline=False,
            )
        else:
            return
        emb.add_field(name="詳細", value="```" + command["desc"] + "```", inline=False)
        emb.set_footer(text="両エディションとも同じ構文で利用ができます。")
        if n == True:
            emb.set_footer(text="もう片方のエディションには実装されていません。")
        if command["is_diff"] == True:
            description += (
                "\n### このコマンドはJEとBEで構文が違います！\n下のボタンからJEとBEの切り替えが可能です。\n \n"
                + "Wiki: [英語](https://minecraft.fandom.com/wiki/Commands/"
                + コマンド
                + ") / [日本語](https://minecraft.fandom.com/ja/wiki/コマンド/"
                + コマンド
                + ")"
            )
            change_button = discord.ui.Button(
                label="切り替え",
                custom_id="change_edition",
                style=discord.ButtonStyle.gray,
            )
            view.add_item(change_button)
            emb.set_footer(text=e + " Edition")
        emb.description = description
    except Exception as e:
        emb.color = 0xFF1515
        emb.description = (
            "## データが足りません\n検索したワード: `"
            + コマンド
            + "`\nデータ: "
            + str(command)
            + "\n"
            + str(e)
        )
    return emb, view


def ShowConfig(コマンド):
    emb = discord.Embed()
    view = discord.ui.View()
    with open("./data.json", encoding="utf-8") as f:
        j = json.load(f)
    try:
        data = j["command_data"]["name." + コマンド]
        json_str = json.dumps(data, indent=2, ensure_ascii=False)
        emb.description = (
            "`"
            + コマンド
            + "`の編集画面です:\n```json\n"
            + str(json_str)
            + "```\n### ❗必ずどの値がどのようなものなのかを把握してから編集・追加をしてください。\n`❓ヘルプメッセージ`から確認することができます"
        )
        view.add_item(
            discord.ui.Button(
                style=discord.ButtonStyle.green,
                label="ヘルプメッセージ",
                emoji="❓",
                custom_id="help_message",
            )
        )
        view.add_item(
            discord.ui.Button(
                style=discord.ButtonStyle.blurple,
                label="新しくコマンドを追加",
                emoji="✨",
                custom_id="create_new_command",
            )
        )
        view.add_item(
            discord.ui.Button(
                style=discord.ButtonStyle.gray,
                label="エディションで構文が変わるか(is_diff)",
                emoji="\N{ANTICLOCKWISE DOWNWARDS AND UPWARDS OPEN CIRCLE ARROWS}",
                custom_id="edit_isdiff." + コマンド,
            )
        )
        view.add_item(
            discord.ui.Button(
                style=discord.ButtonStyle.gray,
                label="対応バージョンを変更(ver)",
                emoji="🔢",
                custom_id="edit_edition." + コマンド + ".ver",
            )
        )
        view.add_item(
            discord.ui.Button(
                style=discord.ButtonStyle.gray,
                label="詳細を変更(desc)",
                emoji="✏️",
                custom_id="edit_change_description." + コマンド,
            )
        )
        view.add_item(
            discord.ui.Button(
                style=discord.ButtonStyle.gray,
                label="使用例変更(exmp)",
                emoji="💎",
                custom_id="edit_edition." + コマンド + ".exmp",
            )
        )
        view.add_item(
            discord.ui.Button(
                style=discord.ButtonStyle.gray,
                label="引数変更(options)",
                emoji="📑",
                custom_id="edit_edition." + コマンド + ".options",
            )
        )
        emb.color = 0xBFB4BB
    except KeyError:
        emb.description = f"指定されたキーが見つかりません: `{コマンド}`"
    except Exception as e:
        emb.color = 0xFF1515
        emb.title = "エラー"
        emb.description = (
            "エラーが発生しました。原因がわからなかったらスクショして <@305607244945293314> にスクショと一緒にメンションをすっ飛ばしてください。よろしくお願いします。\n```"
            + str(e)
            + "```"
        )
    return emb, view


class Modal(discord.ui.Modal):
    def __init__(self, questions: list):
        super().__init__(title="入力フォーム", timeout=None)
        self.questions = questions
        for i in questions:
            self.add_item(i)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()

@client.event
async def on_ready():
    print('ITS ME')
    await tree.sync(guild=gld)

@tree.command(
        name="search", description="コマンドを検索し、結果を表示します。"
    )
@app_commands.describe(コマンド="入力すると候補が出現します。")
async def search(interaction: discord.Interaction, コマンド: str) -> None:
    await interaction.response.defer(thinking=True, ephemeral=False)
    with open("./data.json", encoding="utf-8") as f:
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
            select = discord.ui.Select(
                custom_id="select_commands",
                placeholder="コマンドを選んでください",
                options=select_list,
            )
            view.add_item(select)
            emb.description = "## 類似するコマンドが見つかりました。\n以下の選択肢から類似したコマンドの詳細が見れます。"
        else:
            emb.color = 0xFF1515
            emb.description = (
                "## コマンドが見つかりませんでした\n検索したワード: `"
                + コマンド
                + "`"
            )
            emb.set_footer(
                text="コマンド検索では、コマンドを入力すると候補が表示されます。そこから検索すると結果がでるかも？"
            )
    await interaction.followup.send(embed=emb, view=view)

@search.autocomplete("コマンド")
async def search_autocomplete(
    interaction: discord.Interaction, current: str
) -> List[app_commands.Choice[str]]:
    with open("./data.json", encoding="utf-8") as f:
        j = json.load(f)
    data = j["commands"]
    return [
        app_commands.Choice(name=query, value=query)
        for query in data
        if current.lower() in query.lower()
    ]

@tree.command(
        name="edit", description="コマンドの情報を追加もしくは編集を行います。"
    )
@app_commands.describe(コマンド='編集をするコマンドを選んでください')
async def add(interaction: discord.Interaction, コマンド: str) -> None:
    await interaction.response.defer(thinking=True, ephemeral=True)
    emb, view = ShowConfig(コマンド)
    await interaction.followup.send(embed=emb, view=view)

@add.autocomplete("コマンド")
async def add_autocomplete(
    interaction: discord.Interaction, current: str
) -> List[app_commands.Choice[str]]:
    with open("./data.json", encoding="utf-8") as f:
        j = json.load(f)
    data = j["commands"]
    return [
        app_commands.Choice(name=query, value=query)
        for query in data
        if current.lower() in query.lower()
    ]

@client.event
async def on_interaction(interaction: discord.Interaction):
    try:
        if interaction.data['component_type'] == 2:
            await on_button_click(interaction)
        elif interaction.data["component_type"] == 3:
            await on_select_click(interaction)
    except KeyError:
        pass

async def on_button_click(interaction: discord.Interaction):
    custom_id = interaction.data["custom_id"]
    with open("./data.json", encoding="utf-8") as f:
        j = json.load(f)
    if custom_id == "change_edition":
        original_emb = interaction.message.embeds[0]
        await interaction.response.defer()
        コマンド = str(original_emb.title)
        n = False
        if str(original_emb.footer.text) == "Java Edition":
            e = "Bedrock"
        elif str(original_emb.footer.text) == "Bedrock Edition":
            e = "Java"
        emb, view = CommandInfo(コマンド, e, n)
        await interaction.edit_original_response(embed=emb, view=view)
    # edit pages
    elif custom_id == "help_message":
        example_json = j["example"]["name.command_name"]
        json_str = json.dumps(example_json, indent=2, ensure_ascii=False)
        emb = discord.Embed(
            color=0x333B78,
            description="このボットでは以下のようなデータを使用しています。\n```json\n"
            + str(json_str)
            + "```\n**※もしどちらかのエディションにしかコマンドが存在しない場合は存在しないエディションのverの項目にnullと入力し、is_diffをFalseにしてください。**\n**※両エディションの構文が変わらない場合はis_diffをFalseにしてください。尚、</search:1218753514684289098> での検索結果ではJE版に書かれているデータが表示されます。**\n**※引数の編集の際、元々記載している通りに書いてもらうのが理想的ですが、難しい場合は別の書き方をしてもらっても構いません。**\n↑に関して、元々の書き方はマイクラのFandomウィキページに書かれてる書き方を利用しています。\nウィキページ: [`英語`](https://minecraft.fandom.com/wiki/Commands) / [`日本語`](https://minecraft.fandom.com/ja/wiki/コマンド)",
        )
        await interaction.response.send_message(embed=emb, ephemeral=True)
    elif "edit_change_description" in custom_id:
        sp = custom_id.split(".")
        コマンド = str(sp[1])
        data = j["command_data"]["name." + コマンド]
        old_data = data["desc"]
        questions = [
            discord.ui.TextInput(
                custom_id="changes_desc",
                label="詳細を入力してください",
                required=True,
                default=str(old_data),
                style=discord.TextStyle.long,
                max_length=1024,
            )
        ]
        modal = Modal(questions)
        await interaction.response.send_modal(modal)
        await modal.wait()
        new_data = modal.questions[0].value
        data["desc"] = str(new_data)
        with open("./data.json", "w", encoding="utf-8") as f:
            json.dump(j, f, indent=4, ensure_ascii=False)
        emb, view = ShowConfig(コマンド)
        await interaction.edit_original_response(embed=emb, view=view)
        log_emb = discord.Embed(
            description="**変更が行われました**\n`"
            + コマンド
            + "` の `desc` にて:\n \n変更者: "
            + interaction.user.mention
            + "\n`OLD:` ```"
            + str(old_data)
            + "```\n`NEW:` ```"
            + str(new_data)
            + "```"
        )
        await interaction.channel.send(embed=log_emb)
    elif "edit_edition" in custom_id:
        sp = custom_id.split(".")
        data = j["command_data"]["name." + str(sp[1])][str(sp[2])]
        data_je = data["je"]
        data_be = data["be"]
        コマンド = str(sp[1])
        questions = [
            discord.ui.TextInput(default=str(data_je), label="JE版", required=False),
            discord.ui.TextInput(default=str(data_be), label="BE版", required=False),
        ]
        modal = Modal(questions)
        await interaction.response.send_modal(modal)
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
        with open("./data.json", "w", encoding="utf-8") as f:
            json.dump(j, f, indent=4, ensure_ascii=False)
        emb, view = ShowConfig(コマンド)
        await interaction.edit_original_response(embed=emb, view=view)
        log_emb = discord.Embed(
            description="**変更が行われました**\n`"
            + コマンド
            + "` の `"
            + str(sp[2])
            + "`にて:\n \n変更者: "
            + interaction.user.mention
            + f"\n`OLD:` ```JE: {str(data_je)}\nBE: {str(data_be)}```\n`NEW:` ```JE: {str(new_data_je)}\nBE: {str(new_data_be)}```"
        )
        await interaction.channel.send(embed=log_emb)
    elif "edit_isdiff" in custom_id:
        sp = custom_id.split(".")
        コマンド = str(sp[1])
        data = j["command_data"]["name." + コマンド]
        await interaction.response.defer()
        description = (
            "**変更が行われました**\n`"
            + コマンド
            + "` の `"
            + "is_diff"
            + "`にて:\n \n変更者: "
            + interaction.user.mention
            + "\n`OLD`: ```"
        )
        if data["is_diff"] is True:
            data["is_diff"] = False
            await interaction.followup.send(
                "**:exclamation: どちらかのエディション限定のコマンドである場合は「対応バージョンを変更」ボタンからコマンドが存在しないエディションの値をnullに設定してください。**",
                ephemeral=True,
            )
            description += "True```\n`NEW:` ```False```"
        else:
            data["is_diff"] = True
            data["ver"] = {
                "je": "-" if data["ver"]["je"] is None else data["ver"]["je"],
                "be": "-" if data["ver"]["be"] is None else data["ver"]["be"],
            }
            await interaction.followup.send(
                "**:exclamation: 片方のエディションのコマンド情報がない場合はできる限りデータを入れてください。**",
                ephemeral=True,
            )
            description += "False```\n`NEW:` ```True```"
        with open("./data.json", "w", encoding="utf-8") as f:
            json.dump(j, f, indent=4, ensure_ascii=False)
        emb, view = ShowConfig(コマンド)
        await interaction.edit_original_response(embed=emb, view=view)
        log_emb = discord.Embed(description=description)
        await interaction.channel.send(embed=log_emb)
    elif custom_id == "create_new_command":
        questions = [
            discord.ui.TextInput(
                label="コマンド名",
                required=True,
                style=discord.TextStyle.short,
                placeholder="スラッシュを外して入力してください",
            ),
            discord.ui.TextInput(
                label="詳細",
                required=False,
                style=discord.TextStyle.long,
                min_length=5,
                max_length=1024,
                placeholder='入力せずに登録すると"-"と登録されます',
            ),
        ]
        modal = Modal(questions)
        await interaction.response.send_modal(modal)
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
                "ver": {"je": "-", "be": "-"},
                "desc": desc,
                "exmp": {"je": "-", "be": "-"},
                "options": {"je": "-", "be": "-"},
            }
            commands.append(modal.questions[0].value)
            commands = sorted(commands)
            data = dict(sorted(data.items()))
            j["commands"] = commands
            j["command_data"] = data
            json_data = json.dumps(json_data, indent=2, ensure_ascii=False)
            with open("./data.json", "w", encoding="utf-8") as f:
                json.dump(j, f, indent=4, ensure_ascii=False)
            emb, view = ShowConfig(コマンド=modal.questions[0].value)
            await interaction.followup.send(embed=emb, view=view, ephemeral=True)
            log_emb = discord.Embed(
                description="新しいコマンドが追加されました\nコマンド名: `"
                + modal.questions[0].value
                + "`\n \n作成者: "
                + interaction.user.mention
                + "\n```json\n"
                + str(json_data)
                + "```"
            )
            await interaction.channel.send(embed=log_emb)
        else:
            await interaction.followup.send("既にコマンドが存在しています！", ephemeral=True)

async def on_select_click(interaction: discord.Interaction):
    custom_id = interaction.data["custom_id"]
    values = interaction.data["values"]
    if custom_id == "select_commands":
        await interaction.response.defer(thinking=True, ephemeral=False)
        with open("./data.json", encoding="utf-8") as f:
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
        await interaction.followup.send(embed=emb, view=view)

client.run('')
