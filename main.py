import discord
import operator
import os
from datetime import datetime
from discord.ext import commands
from profanity_check import predict
from pytz import timezone
from replit import db
from keep_alive import keep_alive

prefix = "/"
token = os.environ['TOKEN']
bot = commands.Bot(command_prefix=prefix, intents=discord.Intents.all())

def update_fines(user_name):
  #fine = 0
  
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
  my_dict = dict(db.items())
  
  sorted_dict = dict(sorted(my_dict.items(), key=lambda item: item[1], reverse=True))
  print(sorted_dict)
  
  top10_dict = dict(list(sorted_dict.items())[:10])
  items = top10_dict.items()

  violators_string = ""
  x = 1
  
  for item in items:
    print(item[0], item[1]) ## remove later
    violators_string = violators_string + str(x) + ": " + f"<@{item[0]}>" + " - " + str(item[1]) + " violations \n"
    x = x + 1

  violators = discord.Embed(
      color=discord.Color.red(),
      title='TOP 10 MORALITY VIOLATORS',
      description=f"{violators_string}"
    )
    
  await interaction.response.send_message(embed=violators)

@bot.tree.command(name="outstanding-fines", description="Provide total outstanding fines for a user")
async def outstandingfines(interaction: discord.Interaction, user: str):
  await interaction.response.send_message(f"Outstanding fines {str}")

keep_alive()
bot.run(token)