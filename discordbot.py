import logging
import discord
import traceback
from discord.ext import commands
from os import getenv
import openai
from discord.utils import get

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='/', intents=intents)

messages = [
    {"role": "system", "content": "You are a helpful assistant. The AI assistant's name is AI Qiitan."},
    {"role": "user", "content": "こんにちは。あなたは誰ですか？"},
    {"role": "assistant", "content": "私は AI アシスタントの AI Qiitan です。なにかお手伝いできることはありますか？"}
]

@bot.event
async def on_command_error(ctx, error):
    orig_error = getattr(error, "original", error)
    error_msg = ''.join(traceback.TracebackException.from_exception(orig_error).format())
    await ctx.send(error_msg)

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # メンションを検出
    if get(message.mentions, id=bot.user.id):
        content = message.content.replace(f"<@{bot.user.id}>", "").strip()

        # OpenAI APIキーの確認
        openai_api_key = getenv('OPENAI_API_KEY')
        if not openai_api_key:
            await message.channel.send("OpenAI APIキーが設定されていません。")
            return
        openai.api_key = openai_api_key

        # メッセージ履歴を管理（最新10件のみ保持）
        messages.append({"role": "user", "content": content})
        messages[:] = messages[-10:]

        # OpenAI APIを呼び出す
        try:
            completion = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages
            )
            response = completion.choices[0].message.content
        except Exception as e:
            error_message = f"エラーが発生しました。\n```\n{e}\n```"
            logging.error(f"OpenAI API Error: {e}")
            await message.channel.send(error_message)

        await message.channel.send(response)

token = getenv('DISCORD_BOT_TOKEN')
bot.run(token)
