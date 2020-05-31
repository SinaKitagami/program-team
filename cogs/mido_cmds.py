import discord
from discord.ext import commands
import m10s_util as ut

class mido_cmds(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
    
    #check
    @commands.command()
    async def check(self, ctx, uid:int=None):
        print(f'{ctx.message.author.name}({ctx.message.guild.name})_'+ ctx.message.content)
        e = discord.Embed(title="思惟奈ちゃん処罰情報", description="取得中です...", color=self.bot.ec)
        msg = await ctx.send(embed=e)        
        
        if uid == None:
            uid = ctx.author.id
        else:
            uid = uid
        
        self.bot.cursor.execute("select * from gban_dates where id=?", (uid,))
        gbaninfo = self.bot.cursor.fetchone()
        
        if gbaninfo:
            u = await self.bot.fetch_user(uid)
            by = await self.bot.fetch_user(gbaninfo["gban_by"])
            e.add_field(name="グローバルBan", value=f"{u} のグローバルBanについて")
            e.add_field(name="実行者", value=f"{by} ({by.id})")
            e.add_field(name="理由", value=f"```{gbaninfo['reason']}```", inline=False)
        else:
            e.add_field(name="グローバルBan", value="そのユーザーは思惟奈ちゃんのグローバルBanされていません。")
        
        self.bot.cursor.execute("select * from users where id=?", (uid,))
        upf = self.bot.cursor.fetchone()
        
        if upf["gban"]:
            u = await self.bot.fetch_user(uid)
            e.add_field(name="グローバルチャットBan", value=f"{u} のグローバルチャットBanについて")
            e.add_field(name="理由", value=f"```{upf['gbanhist']}```") 
        else:
            e.add_field(name="グローバルチャットBan", value=f"そのユーザーは思惟奈ちゃんのグローバルチャットBanされていません。") 
        
        e.description = None
        await msg.edit(embed=e)        

def setup(bot):
    bot.add_cog(mido_cmds(bot))
