from datetime import datetime
from pytz import timezone
import discord
from discord.ext import commands
import os
from profanity_check import predict
from replit import db
import operator

prefix = "/"
token = os.environ['TOKEN']
bot = commands.Bot(command_prefix=prefix, intents=discord.Intents.all())

def update_fines(user_name):
  fine = 0
  
  try:
    fine = db[user_name]
    fine = fine + 1
    db[user_name] = fine
  except:
    db[user_name] = 1

  return fine

@bot.event
async def on_ready():
  print("The bot is online!")
  try:
    synced = await bot.tree.sync()
    print(f"Synced {len(synced)} command(s)")
  except Exception as e:
    print(e)

@bot.event
async def on_message(ctx):
  if ctx.author.id == bot.user.id:
    return

  profanity = predict([ctx.content])

  if profanity == 1:
    current_time = datetime.now(timezone('EST')).strftime("%H:%M:%S")
    current_date = datetime.now().strftime('%m.%d.%Y')
    user_name = str(ctx.author.id)
    outstandingfines = str(update_fines(user_name))
    server = ctx.guild.name
    channel = ctx.channel.name

    violation = discord.Embed(
      color=discord.Color.red(),
      title='MORALITY VIOLATION',
      description=f"Time: {current_time} EST \n \
      Date: {current_date} \n \
      Name: {ctx.author.mention} \n \
      Server: {server} \n \
      Channel: #{channel} \n \
      Punishment: Warning & fine \n \
      Fine: 1 Credit \n \
      Outstanding Fines: {outstandingfines} Credit(s)"
    )

    await ctx.channel.send(embed=violation)

@bot.tree.command(name="top10-violators", description="List of the Top 10 Morality Violators")
async def top10(interaction: discord.Interaction):
  key_values = db.items()

  key_values = sorted(key_values, key=operator.itemgetter(1), reverse=True)

  #top10_keys = keys_sorted[:10]

  print(key_values)  
    
  await interaction.response.send_message("Top10 Foo")

@bot.tree.command(name="outstanding-fines", description="Provide total outstanding fines for a user")
async def outstandingfines(interaction: discord.Interaction, user: str):
  await interaction.response.send_message(f"Outstanding fines {str}")

bot.run(token)