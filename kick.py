import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.members = True


class kick(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.yes_counter = 0
        self.no_counter = 0
        self.author = ""
        self.target = discord.Member
        self.yes = '✔️'
        self.no = '❌'
        self.vote_is_active = False
        self.current_ctx = ''
        self.voted_members = set()

    @commands.command()
    async def kick(self, ctx, user: discord.Member):
        if ctx.author.voice is None:
            await ctx.send("You're not in a voice channel.")
            return
        if user.voice is None:
            await ctx.send("User is not in a voice channel.")
            return
        if self.vote_is_active:
            await ctx.send("There is already a vote active.")
            return
        if len(ctx.author.voice.channel.members) <= 1:
            await ctx.send("Need more people to start a vote!")
        else:
            message = await ctx.send(
                f'Vote off {user} Started by {ctx.author.name} \n\'✔️\' = YES, \'❌\' = NO '
            )
            self.vote_is_active = True
            self.current_ctx = ctx
            self.author = ctx.author
            self.target = user
            await message.add_reaction(self.yes)
            await message.add_reaction(self.no)
            self.yes_counter = 1
            self.no_counter = 1

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user: discord.Member):
        if (self.yes_counter >= 1
                or self.no_counter >= 1) and (user == self.author
                                              or user == self.target
                                              or user.voice is None):
            await reaction.remove(user)
            return

        if user in self.voted_members:
            return

        else:
            if reaction.emoji == self.yes:
                await self.upvote()

            else:
                await self.downvote()

            self.voted_members.add(user)

    async def upvote(self):
        self.yes_counter += 1
        member_count = len(self.author.voice.channel.members) - 2
        offset = 1 if member_count == 3 else 2
        if self.yes_counter >= member_count - offset:
            await self.target.edit(voice_channel=None)
            await self.reset()
        return

    async def downvote(self):
        self.no_counter += 1
        member_count = len(self.author.voice.channel.members) - 2
        offset = 1 if member_count == 3 else 2
        if self.no_counter > offset:
            await self.current_ctx.ctx.send(f'{self.target} was saved')
            await self.reset()
        return

    async def reset(self):
        print('here')
        self.yes_counter = 0
        self.no_counter = 0
        self.author = discord.Member
        self.target = discord.Member
        self.vote_is_active = False
        self.current_ctx = ''
        self.voted_members.clear()


def setup(client):
    client.add_cog(kick(client))
