from datetime import datetime
from glob import glob
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from discord.ext.commands import Bot as BotBase
from discord.ext.commands import (CommandNotFound,BadArgument,MissingRequiredArgument)
from discord.ext.commands import Context
from discord.errors import HTTPException,Forbidden
from discord import Intents
from discord import Embed, File,DMChannel
import asyncio
from asyncio import sleep
from ..db import db

PREFIX  ="+"
OWNER_IDS = [948223023088042004]
COGS = [path.split("\\")[-1][:-3] for path in glob("./lib/cogs/*.py")]
IGNORE_EXCEPTIONS = (CommandNotFound,BadArgument)
class Ready(object):
	def __init__(self):
		for cog in COGS:
			setattr(self,cog,False)

	def ready_up(self,cog):
		setattr(self,cog,True)
		print(f"{cog} cog ready")

	def all_ready(self):
		return all([getattr(self,cog)for cog in COGS])
class Bot(BotBase):
	def __init__(self):
		self.PREFIX = PREFIX
		self.ready = False
		self.cogs_ready = Ready()
		self.guild = None
		self.scheduler = AsyncIOScheduler()

		db.autosave(self.scheduler)
		intents = Intents.all()
		super().__init__(command_prefix = PREFIX, owner_ids = OWNER_IDS,intents = intents)

	async def setup(self):
		for cog in COGS:
			await self.load_extension(f"lib.cogs.{cog}")
			print(f"{cog} cog loaded")
		print("setup complete")
	def run(self,version):
		self.VERSION = version
		print("running setup...")
		asyncio.run(self.setup())
		with open("./lib/bot/token.0","r",encoding="utf-8") as tf:
			self.TOKEN = tf.read()
		print("running bot ...")
		super().run(self.TOKEN,reconnect = True)

	async def process_commands(self,message):
		ctx = await self.get_context(message,cls = Context)
		if ctx.command is not None and ctx.guild is not None:
			if self.ready:
					await self.invoke(ctx)
			else:
				await ctx.send("I'm not ready for command. Please wait for a few seconds!")
	async def rules_reminder(self):
		await self.stdout.send("Remember to adhere to the rules")
	async def on_connect(self):
		print("bot connected")

	async def on_disconnect(self):
		print("bot disconnected")

	async def on_error(self, err, *args, **kwargs):
		if err == "on_command_error":
			await args[0].send("Something went wrong.")

		await self.stdout.send("An error occured.")
		raise
	async def on_command_error(self,ctx,exc):
		if any([isinstance(exc, error) for error in IGNORE_EXCEPTIONS]):
			pass

		elif isinstance(exc, MissingRequiredArgument):
			await ctx.send("One or more required arguments are missing.")

		# elif isinstance(exc, CommandOnCooldown):
		# 	await ctx.send(f"That command is on {str(exc.cooldown.type).split('.')[-1]} cooldown. Try again in {exc.retry_after:,.2f} secs.")

		elif hasattr(exc, "original"):
			# if isinstance(exc.original, HTTPException):
			# 	await ctx.send("Unable to send message.")

			if isinstance(exc.original, Forbidden):
				await ctx.send("I do not have permission to do that.")

			else:
				raise exc.original

		else:
			raise exc
	async def on_ready(self):
		if not self.ready:
			self.ready =True
			self.guild = self.get_guild(1335448600427237406)
			self.stdout = self.get_channel(1335448602675515455)
			self.scheduler.add_job(self.rules_reminder,CronTrigger(day_of_week =0,hour=12,minute=0,second = 0))
			self.scheduler.start()
			if self.guild:
				print(f"Connected to: {self.guild.name} (ID: {self.guild.id})")
			else:
				print("Guild not found. Make sure the bot is in the server.")
			while not  self.cogs_ready.all_ready():
				await sleep(0.5)
			self.ready = True
			print("bot ready")
			
			await self.stdout.send("Now online!")

			# embed = Embed(title = "Now online!", description="PTN's bot is now online",colour = 0xFF0000,timestamp =datetime.utcnow())
			# fields = [("Name","Value",True),("Another field","This is next to the other one.",True),
			# ("A non-inline field","This field will appear on it's own row.",False)]
			# for name,value,inline in fields:
			# 	embed.add_field(name = name,value = value,inline = inline)
			# embed.set_author(name="Steve", icon_url=self.guild.icon.url if self.guild.icon else None)
			# embed.set_footer(text = "This is a footer!")
			# embed.set_thumbnail(url = self.guild.icon.url if self.guild.icon else None)
			# embed.set_image(url = self.guild.icon.url if self.guild.icon else None)
			# await channel.send(embed = embed)

			# await channel.send(file = File("./data/images/pic1.jpg"))
		else:
			print("bot connected")
	async def on_message(self,message):
		if not message.author.bot:
			if isinstance(message.channel, DMChannel):
				if len(message.content) < 50:
					await message.channel.send("Your message should be at least 50 characters in length.")

				else:
					member = self.guild.get_member(message.author.id)
					embed = Embed(title="Modmail",
								  colour=member.colour,
								  timestamp=datetime.utcnow())

					embed.set_thumbnail(url=member.avatar_url)

					fields = [("Member", member.display_name, False),
							  ("Message", message.content, False)]

					for name, value, inline in fields:
						embed.add_field(name=name, value=value, inline=inline)
					
					mod = self.get_cog("Mod")
					await mod.log_channel.send(embed=embed)
					await message.channel.send("Message relayed to moderators.")


			else:
				await self.process_commands(message)
bot = Bot()