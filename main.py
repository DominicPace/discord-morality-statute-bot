# Requires Python 3.8, dicord.py 2.1.0, and most importantly, alt-profanity-check (not profanity-check)!

import discord
import os
import sqlite3
from datetime import datetime
from discord.ext import commands
from profanity_check import predict
from pytz import timezone

# Global variables
os.environ["TOKEN"] = ""
prefix = "/"
token = os.environ['TOKEN']
bot = commands.Bot(command_prefix=prefix, intents=discord.Intents.all())

# This function updates fines from sqlite3. If the user has no existing fines it creates a new entry.
def update_fines(user_name):
  fine = 0
  user_name = str(user_name)
  
  db = sqlite3.connect('main.sqlite')
  cursor = db.cursor()
  sql = ("SELECT fines FROM violators WHERE user = ?")
  val = [user_name]
  cursor.execute(sql, val)
  fine = cursor.fetchone()

  if fine is None:
    sql = ("INSERT INTO violators(user, fines) VALUES (?,?)")
    val = (user_name, 1)
    fine = 1
  elif fine is not None:
    fine = fine[0]
    fine = fine + 1
    
    sql = ("UPDATE violators SET fines = ? WHERE user = ?")
    val = (fine, user_name)

  cursor.execute(sql, val)
  db.commit()
  cursor.close()
  db.close()

  return fine

# Main function of bot.
@bot.event
async def on_ready():
  # Remvoe on first time to create DB then add comments back. This should prob be a function that creats the DB if one doesn't already exist.
  # db = sqlite3.connect('main.sqlite')
  # cursor = db.cursor()
  # cursor.execute("CREATE TABLE IF NOT EXISTS violators(user TEXT, fines INT)")

  print("The bot is online!")
  try:
    synced = await bot.tree.sync()
    print(f"Synced {len(synced)} command(s)")
  except Exception as e:
    print(e)

# This function monitors chat for infractions.
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
      description=f"{ctx.author.mention}, you are fined 1 credit for a violation of the verbal morality statue. \n \n Outstanding Fines: {outstandingfines} Credit(s)"
    )
    
    ### REMOVED Time: {current_time} EST \n Date: {current_date} \n Name: {ctx.author} \n Server: {server} \n Channel: #{channel} \n Punishment: Warning & fine \n Fine: 1 Credit \n

    await ctx.channel.send(embed=violation)

# This function adds a "/" command to Discord that reports a top 10 list of violators stored in the sqlite3 DB.
@bot.tree.command(name="top10-violators", description="List of the Top 10 Morality Violators")
async def top10(interaction: discord.Interaction):
  db = sqlite3.connect('main.sqlite')
  cursor = db.cursor()
  sql = ("SELECT user, fines FROM violators ORDER BY fines DESC LIMIT 10")
  cursor.execute(sql)
  fine = cursor.fetchall()
  cursor.close()
  db.close()

  top10_dict = dict(fine)
  items = top10_dict.items()

  violators_string = ""
  x = 1
  
  for item in items:
    violators_string = violators_string + str(x) + ": " + f"<@{item[0]}>" + " - " + str(item[1]) + " violations \n"
    x = x + 1

  violators = discord.Embed(
      color=discord.Color.red(),
      title='TOP 10 MORALITY VIOLATORS',
      description=f"{violators_string}"
    )
    
  await interaction.response.send_message(embed=violators)

# This function adds a "/" command to Discord that allows one user to lookup the fines of another (single) user.
@bot.tree.command(name="outstanding-fines", description="Provide total outstanding fines for a user")
async def outstandingfines(interaction: discord.Interaction, user: discord.User):
  user_name = str(user.id)
  
  db = sqlite3.connect('main.sqlite')
  cursor = db.cursor()
  sql = ("SELECT fines FROM violators WHERE user = ?")
  val = [user_name]
  try:
    cursor.execute(sql, val)
    fines = cursor.fetchone()[0]
  except:
    fines = 0

  cursor.close()
  db.close()

  await interaction.response.send_message(f"Outstanding fines for {user.name}: {fines} Credits")

bot.run(token)
