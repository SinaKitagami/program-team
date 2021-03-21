import asyncio

class CannotPaginate(Exception):
    pass

class EmbedPaginator:
    
    def __init__(self, ctx, *, entries, timeout=30.0):
        self.ctx = ctx
        self.bot = ctx.bot
        self.entries = entries
        self.max_page = len(entries) - 1
        self.page = 0
        self.timeout = timeout
        
        if ctx.guild is None:
            perm = self.ctx.channel.permissions_for(ctx.bot.user)
        else:
            perm = self.ctx.channel.permissions_for(ctx.guild.me)
        
        if not perm.embed_links:
            raise CannotPaginate("Missing Permissions : embed_links")
        if not perm.send_messages:
            raise CannotPaginate("Missing Permissions : send_messages")
        if not perm.add_reactions:
            raise CannotPaginate("Missing Permissions : add_reactions")
        if not perm.read_message_history:
            raise CannotPaginate("Missing Permissions : read_message_history")
        
    def get_page(self, page:int):
        self.page = page
        return self.entries[page]
    
    async def paginate(self):
        msg = await self.ctx.send(embed=self.entries[self.page])
        
        tasks = []
        tasks.append(msg.add_reaction('⏮'))
        tasks.append(msg.add_reaction('◀'))
        tasks.append(msg.add_reaction('⏹️'))
        tasks.append(msg.add_reaction('▶'))
        tasks.append(msg.add_reaction('⏭️'))
        tasks.append(msg.add_reaction('🔢'))
        
        asyncio.gather(*tasks)
        
        def check(reaction, user):
            if reaction.message.id == msg.id and user.id == self.ctx.message.author.id:
                return True
            else:
                return False
        
        while True:
            try:
                reaction, user = await self.bot.wait_for("reaction_add", check=check, timeout=self.timeout)
            except:
                break
            
            try:
                await msg.remove_reaction(reaction, user)
            except:
                pass
            
            if str(reaction) == "⏮":
                embed = self.get_page(0)
            elif str(reaction) == "◀":
                if self.page == 0:
                    embed = self.get_page(self.max_page)
                else:
                    embed = self.get_page(self.page - 1)
            elif str(reaction) == "⏹️":
                cl = []
                cl.append(msg.remove_reaction('⏮', self.bot.user))
                cl.append(msg.remove_reaction('◀', self.bot.user))
                cl.append(msg.remove_reaction('⏹️', self.bot.user))
                cl.append(msg.remove_reaction('▶', self.bot.user))
                cl.append(msg.remove_reaction('⏭️', self.bot.user))
                cl.append(msg.remove_reaction('🔢', self.bot.user))
         
                try:
                    await asyncio.gather(*cl)
                except:
                    pass
                
                break
            elif str(reaction) == "▶":
                if self.page == self.max_page:
                    embed = self.get_page(0)
                else:
                    embed = self.get_page(self.page + 1)
            elif str(reaction) == "⏭️":
                embed = self.get_page(self.max_page)
            elif str(reaction) == "🔢":
                a = await self.ctx.send("> 何ページに移動しますか？")
                
                try:
                    m = await self.bot.wait_for("message", check=lambda message: message.channel.id == self.ctx.channel.id and message.author.id == self.ctx.message.author.id and str(message.content).isdigit(), timeout=self.timeout)
                except:
                    embed = self.get_page(0)
                else:
                    try:
                        await a.delete()
                    except:
                        pass
                    
                    p = int(m.content) - 1
                    
                    if p > self.max_page:
                        embed = self.get_page(self.max_page)
                    elif p < 0:
                        embed = self.get_page(0)
                    else:
                        embed = self.get_page(p)
            
            await msg.edit(embed=embed)