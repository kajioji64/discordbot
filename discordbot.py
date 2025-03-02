import logging
import discord
import traceback
from discord.ext import commands
from os import getenv
import openai
from discord.utils import get

# Discordのintents設定
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='/', intents=intents)

# OpenAIクライアントの初期化
openai_api_key = getenv('OPENAI_API_KEY')
if not openai_api_key:
    raise ValueError("環境変数 OPENAI_API_KEY が設定されていません。")

client = openai.Client(api_key=openai_api_key)

# 許可するユーザーのIDをリストで管理（自分のDiscord IDを設定）
ALLOWED_USERS = [kajioji.]  # ここに自分のDiscord IDを入れる

# メッセージ履歴の管理
messages = [
    {"role": "system", "content": "You are a helpful assistant. The AI assistant's name is AI Qiitan."},
    {"role": "user", "content": "こんにちは。あなたは誰ですか？"},
    {"role": "assistant", "content": "私は AI アシスタントの AI Qiitan です。なにかお手伝いできることはありますか？"}
]

@bot.event
async def on_command_error(ctx, error):
    orig_error = getattr(error, "original", error)
    error_msg = ''.join(traceback.TracebackException.from_exception(orig_error).format())
    await ctx.send(f"エラーが発生しました。\n```\n{error_msg}\n```")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # 許可されていないユーザーなら無視
    if message.author.id not in ALLOWED_USERS:
        return

    # メンションを検出
    if get(message.mentions, id=bot.user.id):
        content = message.content.replace(f"<@{bot.user.id}>", "").strip()

        # メッセージ履歴を更新（最大10件まで）
        messages.append({"role": "user", "content": content})
        messages[:] = messages[-10:]

        try:
            # OpenAI APIを呼び出す
            completion = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages
            )
            response = completion.choices[0].message.content

            # AIの応答を履歴に追加
            messages.append({"role": "assistant", "content": response})
            messages[:] = messages[-10:]  # 最大10件まで保持

        except openai.OpenAIError as e:
            error_message = f"OpenAI APIエラーが発生しました。\n```\n{e}\n```"
            logging.error(f"OpenAI API Error: {e}")
            await message.channel.send(error_message)
            return

        await message.channel.send(response)

    # コマンドの処理を許可する
    await bot.process_commands(message)

# Discord Botの起動
token = getenv('DISCORD_BOT_TOKEN')
if not token:
    raise ValueError("環境変数 DISCORD_BOT_TOKEN が設定されていません。")

bot.run(token)
