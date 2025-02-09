from discord.ext.commands import Cog
from discord import Forbidden
from discord.ext.commands import command

from ..db import db

class Welcome(Cog):
	def __init__(self,bot):
		self.bot = bot

	@Cog.listener()
	async def on_ready(self):
		if not self.bot.ready:
			self.bot.cogs_ready.ready_up("welcome")

	@Cog.listener()
	async def on_member_join(self,member):
		db.execute("INSERT INTO exp (UserID) VALUES(?)",member.id)
		await self.bot.get_chanel(1337331201836322826).send("Welcome to **{member.guild.name}** {member.mention}! Head over to <#.1335448602675515455> to say hi")
		try:
			await member.send(f"Welcome to **{member.guild.name}**!Enjoy your stay!")
		except Forbidden:
			pass
		await member.add_roles(member.guild.get_role(1337333404869333063),member.guild.get_role(1337333498209374219))
		await self.bot.get_chanel(1337331201836322826).send(f"{member.display_name} has left {member.guild.name}.")

	@Cog.listener()
	async def on_member_remove(self,member):
		db.execute("DELETE FROM exp WHERE UserID=?",member.id)


async def setup(bot):
	await bot.add_cog(Welcome(bot))
