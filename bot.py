# -*- coding: utf-8 -*- #

from cogs import apple_invite
from cogs import apple_foc
import discord
from discord import app_commands
from discord.ext import commands, tasks
import json
import random
import wikipedia
import wikidata.client
import asyncio
import datetime
import traceback

import aiohttp
import aiosqlite
import database

from twitter import *
from dateutil.relativedelta import relativedelta as rdelta

from my_module import dpy_interaction as dpyui

# textto etc
import m10s_util as ut
from apple_util import AppleUtil
from l10n import TranslateHandler, LocalizedContext
from checker import MaliciousInput, content_checker
# tokens
import config


import logging

# logging.basicConfig(level=logging.DEBUG)

intents:discord.Intents = discord.Intents.default()
intents.typing = False
intents.members = True
intents.presences = True
intents.message_content = True

bot = commands.AutoShardedBot(command_prefix="s-", status=discord.Status.invisible,
                   allowed_mentions=discord.AllowedMentions(everyone=False),
                   intents=intents,
                   enable_debug_events=True
                   )
"""bot = commands.Bot(command_prefix="s-", status=discord.Status.invisible,
                   allowed_mentions=discord.AllowedMentions(everyone=False),
                   intents=intents,
                   enable_debug_events=True,
                   shard_id=0,
                   shard_count=2
                   )"""
bot.owner_id = None
bot.owner_ids = {404243934210949120, 525658651713601536}
bot.maintenance = False


bot.dpyui = dpyui.interaction_actions(bot)

bot.team_sina = config.team_sina

bot.comlocks = {}

# トークンたち
bot.DROP_TOKEN = config.DROP_TOKEN
bot.BOT_TEST_TOKEN = config.BOT_TEST_TOKEN
bot.BOT_TOKEN = config.BOT_TOKEN
bot.NAPI_TOKEN = config.NAPI_TOKEN
bot.GAPI_TOKEN = config.GAPI_TOKEN
bot.T_API_key = config.T_API_key
bot.T_API_SKey = config.T_API_SKey
bot.T_Acs_Token = config.T_Acs_Token
bot.T_Acs_SToken = config.T_Acs_SToken


# test
postcount = {}

db = None

async def db_setup():
    global db
    try:        
        #db = await aiomysql.connect(host=config.DB_HOST,
        #    user=config.DB_USER,
        #    password=config.DB_PW,
        #    db=config.DB_NAME,
        #    loop=main_loop,
        #    autocommit=True,
        #    charset="utf8mb4"
        #    )
        bot.cursor = database.Database(host=config.DB_HOST, port=3306, user=config.DB_USER, password=config.DB_PW, db=config.DB_NAME)
        #bot.cursor = await db.cursor(aiomysql.DictCursor)

    except:
        traceback.print_exc()

async def main():
    async with bot:
        await db_setup()

        await bot.load_extension("cogs.apple_misc")
        await bot.load_extension("cogs.apple_onlinenotif")

        await apple_invite.setup(bot)
        await apple_foc.setup(bot)

        bot.session = aiohttp.ClientSession(loop=bot.loop)

        # 通常トークン
        await bot.start(bot.BOT_TOKEN)

        # テストトークン
        # await bot.start(bot.BOT_TEST_TOKEN)


bot._default_close = bot.close


async def close_handler():
    await bot._default_close()
    await bot.session.close()
    try:
        await db.commit()
    except aiosqlite.ProgrammingError:
        pass
    else:
        await db.close()
bot.close = close_handler

bot.translate_handler = TranslateHandler(bot, ["en", "ja"])
bot._get_context = bot.get_context


async def get_context(msg, cls=LocalizedContext):
    ctx = await bot._get_context(msg, cls=cls)
    ctx.context_at = datetime.datetime.now(datetime.timezone.utc).timestamp()
    return ctx
bot.get_context = get_context

bot._ = bot.translate_handler.get_translation_for
bot.l10n_guild = bot.translate_handler.get_guild_translation_for
bot.l10n_any = bot.translate_handler.get_any_translation
bot.l10n_raw = bot.translate_handler.get_raw_translation

"""
au_w:[
        {
            "reactions":["str" or "id"(0-19)],
            "give_role"[None or id(int)],
            "text":str""
        },...
    ]
"""


DoServercmd = False
gprofilever = "v1.0.1"
wikipedia.set_lang('ja')
bot.mwc = wikidata.client.Client()
rpcct = 0
rpcs = [
    "ヘルプ:s-help",
    "アイコン:しおさばきゅーさん",
    "サーバー数:{0}/ユーザー数:{1}",
    "シャード番号:{2}",
    "作成:チーム☆思惟奈ちゃん",
    "help:s-help",
    "icon:しおさばきゅー",
    "{0}guilds/{1}users",
    "shard id:{2}",
    "created by team-sina"
]
"""db = dropbox.Dropbox(DROP_TOKEN)
db.users_get_current_account()"""
bot.twi = Twitter(auth=OAuth(
    bot.T_Acs_Token, bot.T_Acs_SToken, bot.T_API_key, bot.T_API_SKey))
bot.ec = 0x42bcf4
Donotif = False
bot.StartTime = datetime.datetime.now(datetime.timezone.utc)

aglch = None


bot.features = config.sp_features

bot.apple_util = AppleUtil(bot)


def shares_guild(user_id_a, user_id_b):
    return not not [
        guild
        for guild
        in bot.guilds
        if set([user_id_a, user_id_b]).issubset(frozenset(guild._members.keys()))
    ]


bot.shares_guild = shares_guild


async def can_use_online(user):
    enabled = await bot.cursor.fetchone("SELECT online_agreed FROM users WHERE id = %s", (user.id,))
    #enabled = await bot.cursor.fetchone()
    return enabled and enabled["online_agreed"]


bot.can_use_online = can_use_online

# 初回ロード
"""db.files_download_to_file( "guildsetting.json" , "/guildsetting.json" )
db.files_download_to_file( "profiles.json" , "/profiles.json" )
db.files_download_to_file( "gp.json" , "/gp.json" )
db.files_download_to_file( "globaldatas.json" , "/globaldatas.json" )
db.files_download_to_file( "gchatchs.json" , "/gchatchs.json" )"""

bot.tl = "　ゔ 、。，．・：；？！゛゜´｀¨＾￣＿ヽヾゝゞ〃仝々〆〇ー―‐／＼～∥｜…‥‘’“”（）〔〕［］｛｝〈〉《》「」『』【】＋－±×÷＝≠＜＞≦≧∞∴♂♀°′″℃￥＄￠￡％＃＆＊＠§☆★○●◎◇◆□■△▲▽▼※〒→←↑↓〓∈∋⊆⊇⊂⊃∪∩∧∨￢⇒⇔∀∃∠⊥⌒∂∇≡≒≪≫√∽∝∵∫∬Å‰♯♭♪†‡¶◯０１２３４５６７８９1234567890ａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚabcdefghijklmnopqrstuvwxyz-^\=~|@[]:;\/.,<>?_+*}{`!\"#$%&'()ぁあぃいぅうぇえぉおかがきぎくぐけげこごさざしじすずせぜそぞただちぢっつづてでとどなにぬねのはばぱひびぴふぶぷへべぺほぼぽまみむめもゃやゅゆょよらりるれろゎわゐゑをんァアィイゥウェエォオカガキギクグケゲコゴサザシジスズセゼソゾタダチヂッツヅテデトドナニヌネノハバパヒビピフブプヘベペホボポマミムメモャヤュユョヨラリルレロヮワヰヱヲンヴヵヶΑΒΓΔΕΖΗΘΙΚΛΜΝΞΟΠΡΣΤΥΦΧΨΩαβγδεζηθικλμνξοπρστυφχψωАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯабвгдеёжзийклмнопрстуфхцчшщъыьэюя─│┌┐┘└├┬┤┴┼━┃┏┓┛┗┣┳┫┻╋┠┯┨┷┿┝┰┥┸╂亜唖娃阿哀愛挨姶逢葵茜穐悪握渥旭葦芦鯵梓圧斡扱宛姐虻飴絢綾鮎或粟袷安庵按暗案闇鞍杏以伊位依偉囲夷委威尉惟意慰易椅為畏異移維緯胃萎衣謂違遺医井亥域育郁磯一壱溢逸稲茨芋鰯允印咽員因姻引飲淫胤蔭院陰隠韻吋右宇烏羽迂雨卯鵜窺丑碓臼渦嘘唄欝蔚鰻姥厩浦瓜閏噂云運雲荏餌叡営嬰影映曳栄永泳洩瑛盈穎頴英衛詠鋭液疫益駅悦謁越閲榎厭円園堰奄宴延怨掩援沿演炎焔煙燕猿縁艶苑薗遠鉛鴛塩於汚甥凹央奥往応押旺横欧殴王翁襖鴬鴎黄岡沖荻億屋憶臆桶牡乙俺卸恩温穏音下化仮何伽価佳加可嘉夏嫁家寡科暇果架歌河火珂禍禾稼箇花苛茄荷華菓蝦課嘩貨迦過霞蚊俄峨我牙画臥芽蛾賀雅餓駕介会解回塊壊廻快怪悔恢懐戒拐改魁晦械海灰界皆絵芥蟹開階貝凱劾外咳害崖慨概涯碍蓋街該鎧骸浬馨蛙垣柿蛎鈎劃嚇各廓拡撹格核殻獲確穫覚角赫較郭閣隔革学岳楽額顎掛笠樫橿梶鰍潟割喝恰括活渇滑葛褐轄且鰹叶椛樺鞄株兜竃蒲釜鎌噛鴨栢茅萱粥刈苅瓦乾侃冠寒刊勘勧巻喚堪姦完官寛干幹患感慣憾換敢柑桓棺款歓汗漢澗潅環甘監看竿管簡緩缶翰肝艦莞観諌貫還鑑間閑関陥韓館舘丸含岸巌玩癌眼岩翫贋雁頑顔願企伎危喜器基奇嬉寄岐希幾忌揮机旗既期棋棄機帰毅気汽畿祈季稀紀徽規記貴起軌輝飢騎鬼亀偽儀妓宜戯技擬欺犠疑祇義蟻誼議掬菊鞠吉吃喫桔橘詰砧杵黍却客脚虐逆丘久仇休及吸宮弓急救朽求汲泣灸球究窮笈級糾給旧牛去居巨拒拠挙渠虚許距鋸漁禦魚亨享京供侠僑兇競共凶協匡卿叫喬境峡強彊怯恐恭挟教橋況狂狭矯胸脅興蕎郷鏡響饗驚仰凝尭暁業局曲極玉桐粁僅勤均巾錦斤欣欽琴禁禽筋緊芹菌衿襟謹近金吟銀九倶句区狗玖矩苦躯駆駈駒具愚虞喰空偶寓遇隅串櫛釧屑屈掘窟沓靴轡窪熊隈粂栗繰桑鍬勲君薫訓群軍郡卦袈祁係傾刑兄啓圭珪型契形径恵慶慧憩掲携敬景桂渓畦稽系経継繋罫茎荊蛍計詣警軽頚鶏芸迎鯨劇戟撃激隙桁傑欠決潔穴結血訣月件倹倦健兼券剣喧圏堅嫌建憲懸拳捲検権牽犬献研硯絹県肩見謙賢軒遣鍵険顕験鹸元原厳幻弦減源玄現絃舷言諺限乎個古呼固姑孤己庫弧戸故枯湖狐糊袴股胡菰虎誇跨鈷雇顧鼓五互伍午呉吾娯後御悟梧檎瑚碁語誤護醐乞鯉交佼侯候倖光公功効勾厚口向后喉坑垢好孔孝宏工巧巷幸広庚康弘恒慌抗拘控攻昂晃更杭校梗構江洪浩港溝甲皇硬稿糠紅紘絞綱耕考肯肱腔膏航荒行衡講貢購郊酵鉱砿鋼閤降項香高鴻剛劫号合壕拷濠豪轟麹克刻告国穀酷鵠黒獄漉腰甑忽惚骨狛込此頃今困坤墾婚恨懇昏昆根梱混痕紺艮魂些佐叉唆嵯左差査沙瑳砂詐鎖裟坐座挫債催再最哉塞妻宰彩才採栽歳済災采犀砕砦祭斎細菜裁載際剤在材罪財冴坂阪堺榊肴咲崎埼碕鷺作削咋搾昨朔柵窄策索錯桜鮭笹匙冊刷察拶撮擦札殺薩雑皐鯖捌錆鮫皿晒三傘参山惨撒散桟燦珊産算纂蚕讃賛酸餐斬暫残仕仔伺使刺司史嗣四士始姉姿子屍市師志思指支孜斯施旨枝止死氏獅祉私糸紙紫肢脂至視詞詩試誌諮資賜雌飼歯事似侍児字寺慈持時次滋治爾璽痔磁示而耳自蒔辞汐鹿式識鴫竺軸宍雫七叱執失嫉室悉湿漆疾質実蔀篠偲柴芝屡蕊縞舎写射捨赦斜煮社紗者謝車遮蛇邪借勺尺杓灼爵酌釈錫若寂弱惹主取守手朱殊狩珠種腫趣酒首儒受呪寿授樹綬需囚収周宗就州修愁拾洲秀秋終繍習臭舟蒐衆襲讐蹴輯週酋酬集醜什住充十従戎柔汁渋獣縦重銃叔夙宿淑祝縮粛塾熟出術述俊峻春瞬竣舜駿准循旬楯殉淳準潤盾純巡遵醇順処初所暑曙渚庶緒署書薯藷諸助叙女序徐恕鋤除傷償勝匠升召哨商唱嘗奨妾娼宵将小少尚庄床廠彰承抄招掌捷昇昌昭晶松梢樟樵沼消渉湘焼焦照症省硝礁祥称章笑粧紹肖菖蒋蕉衝裳訟証詔詳象賞醤鉦鍾鐘障鞘上丈丞乗冗剰城場壌嬢常情擾条杖浄状畳穣蒸譲醸錠嘱埴飾拭植殖燭織職色触食蝕辱尻伸信侵唇娠寝審心慎振新晋森榛浸深申疹真神秦紳臣芯薪親診身辛進針震人仁刃塵壬尋甚尽腎訊迅陣靭笥諏須酢図厨逗吹垂帥推水炊睡粋翠衰遂酔錐錘随瑞髄崇嵩数枢趨雛据杉椙菅頗雀裾澄摺寸世瀬畝是凄制勢姓征性成政整星晴棲栖正清牲生盛精聖声製西誠誓請逝醒青静斉税脆隻席惜戚斥昔析石積籍績脊責赤跡蹟碩切拙接摂折設窃節説雪絶舌蝉仙先千占宣専尖川戦扇撰栓栴泉浅洗染潜煎煽旋穿箭線繊羨腺舛船薦詮賎践選遷銭銑閃鮮前善漸然全禅繕膳糎噌塑岨措曾曽楚狙疏疎礎祖租粗素組蘇訴阻遡鼠僧創双叢倉喪壮奏爽宋層匝惣想捜掃挿掻操早曹巣槍槽漕燥争痩相窓糟総綜聡草荘葬蒼藻装走送遭鎗霜騒像増憎臓蔵贈造促側則即息捉束測足速俗属賊族続卒袖其揃存孫尊損村遜他多太汰詑唾堕妥惰打柁舵楕陀駄騨体堆対耐岱帯待怠態戴替泰滞胎腿苔袋貸退逮隊黛鯛代台大第醍題鷹滝瀧卓啄宅托択拓沢濯琢託鐸濁諾茸凧蛸只叩但達辰奪脱巽竪辿棚谷狸鱈樽誰丹単嘆坦担探旦歎淡湛炭短端箪綻耽胆蛋誕鍛団壇弾断暖檀段男談値知地弛恥智池痴稚置致蜘遅馳築畜竹筑蓄逐秩窒茶嫡着中仲宙忠抽昼柱注虫衷註酎鋳駐樗瀦猪苧著貯丁兆凋喋寵帖帳庁弔張彫徴懲挑暢朝潮牒町眺聴脹腸蝶調諜超跳銚長頂鳥勅捗直朕沈珍賃鎮陳津墜椎槌追鎚痛通塚栂掴槻佃漬柘辻蔦綴鍔椿潰坪壷嬬紬爪吊釣鶴亭低停偵剃貞呈堤定帝底庭廷弟悌抵挺提梯汀碇禎程締艇訂諦蹄逓邸鄭釘鼎泥摘擢敵滴的笛適鏑溺哲徹撤轍迭鉄典填天展店添纏甜貼転顛点伝殿澱田電兎吐堵塗妬屠徒斗杜渡登菟賭途都鍍砥砺努度土奴怒倒党冬凍刀唐塔塘套宕島嶋悼投搭東桃梼棟盗淘湯涛灯燈当痘祷等答筒糖統到董蕩藤討謄豆踏逃透鐙陶頭騰闘働動同堂導憧撞洞瞳童胴萄道銅峠鴇匿得徳涜特督禿篤毒独読栃橡凸突椴届鳶苫寅酉瀞噸屯惇敦沌豚遁頓呑曇鈍奈那内乍凪薙謎灘捺鍋楢馴縄畷南楠軟難汝二尼弐迩匂賑肉虹廿日乳入如尿韮任妊忍認濡禰祢寧葱猫熱年念捻撚燃粘乃廼之埜嚢悩濃納能脳膿農覗蚤巴把播覇杷波派琶破婆罵芭馬俳廃拝排敗杯盃牌背肺輩配倍培媒梅楳煤狽買売賠陪這蝿秤矧萩伯剥博拍柏泊白箔粕舶薄迫曝漠爆縛莫駁麦函箱硲箸肇筈櫨幡肌畑畠八鉢溌発醗髪伐罰抜筏閥鳩噺塙蛤隼伴判半反叛帆搬斑板氾汎版犯班畔繁般藩販範釆煩頒飯挽晩番盤磐蕃蛮匪卑否妃庇彼悲扉批披斐比泌疲皮碑秘緋罷肥被誹費避非飛樋簸備尾微枇毘琵眉美鼻柊稗匹疋髭彦膝菱肘弼必畢筆逼桧姫媛紐百謬俵彪標氷漂瓢票表評豹廟描病秒苗錨鋲蒜蛭鰭品彬斌浜瀕貧賓頻敏瓶不付埠夫婦富冨布府怖扶敷斧普浮父符腐膚芙譜負賦赴阜附侮撫武舞葡蕪部封楓風葺蕗伏副復幅服福腹複覆淵弗払沸仏物鮒分吻噴墳憤扮焚奮粉糞紛雰文聞丙併兵塀幣平弊柄並蔽閉陛米頁僻壁癖碧別瞥蔑箆偏変片篇編辺返遍便勉娩弁鞭保舗鋪圃捕歩甫補輔穂募墓慕戊暮母簿菩倣俸包呆報奉宝峰峯崩庖抱捧放方朋法泡烹砲縫胞芳萌蓬蜂褒訪豊邦鋒飽鳳鵬乏亡傍剖坊妨帽忘忙房暴望某棒冒紡肪膨謀貌貿鉾防吠頬北僕卜墨撲朴牧睦穆釦勃没殆堀幌奔本翻凡盆摩磨魔麻埋妹昧枚毎哩槙幕膜枕鮪柾鱒桝亦俣又抹末沫迄侭繭麿万慢満漫蔓味未魅巳箕岬密蜜湊蓑稔脈妙粍民眠務夢無牟矛霧鵡椋婿娘冥名命明盟迷銘鳴姪牝滅免棉綿緬面麺摸模茂妄孟毛猛盲網耗蒙儲木黙目杢勿餅尤戻籾貰問悶紋門匁也冶夜爺耶野弥矢厄役約薬訳躍靖柳薮鑓愉愈油癒諭輸唯佑優勇友宥幽悠憂揖有柚湧涌猶猷由祐裕誘遊邑郵雄融夕予余与誉輿預傭幼妖容庸揚揺擁曜楊様洋溶熔用窯羊耀葉蓉要謡踊遥陽養慾抑欲沃浴翌翼淀羅螺裸来莱頼雷洛絡落酪乱卵嵐欄濫藍蘭覧利吏履李梨理璃痢裏裡里離陸律率立葎掠略劉流溜琉留硫粒隆竜龍侶慮旅虜了亮僚両凌寮料梁涼猟療瞭稜糧良諒遼量陵領力緑倫厘林淋燐琳臨輪隣鱗麟瑠塁涙累類令伶例冷励嶺怜玲礼苓鈴隷零霊麗齢暦歴列劣烈裂廉恋憐漣煉簾練聯蓮連錬呂魯櫓炉賂路露労婁廊弄朗楼榔浪漏牢狼篭老聾蝋郎六麓禄肋録論倭和話歪賄脇惑枠鷲亙亘鰐詫藁蕨椀湾碗腕弌丐丕个丱丶丼丿乂乖乘亂亅豫亊舒弍于亞亟亠亢亰亳亶从仍仄仆仂仗仞仭仟价伉佚估佛佝佗佇佶侈侏侘佻佩佰侑佯來侖儘俔俟俎俘俛俑俚俐俤俥倚倨倔倪倥倅伜俶倡倩倬俾俯們倆偃假會偕偐偈做偖偬偸傀傚傅傴傲僉僊傳僂僖僞僥僭僣僮價僵儉儁儂儖儕儔儚儡儺儷儼儻儿兀兒兌兔兢竸兩兪兮冀冂囘册冉冏冑冓冕冖冤冦冢冩冪冫决冱冲冰况冽凅凉凛几處凩凭凰凵凾刄刋刔刎刧刪刮刳刹剏剄剋剌剞剔剪剴剩剳剿剽劍劔劒剱劈劑辨辧劬劭劼劵勁勍勗勞勣勦飭勠勳勵勸勹匆匈甸匍匐匏匕匚匣匯匱匳匸區卆卅丗卉卍凖卞卩卮夘卻卷厂厖厠厦厥厮厰厶參簒雙叟曼燮叮叨叭叺吁吽呀听吭吼吮吶吩吝呎咏呵咎呟呱呷呰咒呻咀呶咄咐咆哇咢咸咥咬哄哈咨咫哂咤咾咼哘哥哦唏唔哽哮哭哺哢唹啀啣啌售啜啅啖啗唸唳啝喙喀咯喊喟啻啾喘喞單啼喃喩喇喨嗚嗅嗟嗄嗜嗤嗔嘔嗷嘖嗾嗽嘛嗹噎噐營嘴嘶嘲嘸噫噤嘯噬噪嚆嚀嚊嚠嚔嚏嚥嚮嚶嚴囂嚼囁囃囀囈囎囑囓囗囮囹圀囿圄圉圈國圍圓團圖嗇圜圦圷圸坎圻址坏坩埀垈坡坿垉垓垠垳垤垪垰埃埆埔埒埓堊埖埣堋堙堝塲堡塢塋塰毀塒堽塹墅墹墟墫墺壞墻墸墮壅壓壑壗壙壘壥壜壤壟壯壺壹壻壼壽夂夊夐夛梦夥夬夭夲夸夾竒奕奐奎奚奘奢奠奧奬奩奸妁妝佞侫妣妲姆姨姜妍姙姚娥娟娑娜娉娚婀婬婉娵娶婢婪媚媼媾嫋嫂媽嫣嫗嫦嫩嫖嫺嫻嬌嬋嬖嬲嫐嬪嬶嬾孃孅孀孑孕孚孛孥孩孰孳孵學斈孺宀它宦宸寃寇寉寔寐寤實寢寞寥寫寰寶寳尅將專對尓尠尢尨尸尹屁屆屎屓屐屏孱屬屮乢屶屹岌岑岔妛岫岻岶岼岷峅岾峇峙峩峽峺峭嶌峪崋崕崗嵜崟崛崑崔崢崚崙崘嵌嵒嵎嵋嵬嵳嵶嶇嶄嶂嶢嶝嶬嶮嶽嶐嶷嶼巉巍巓巒巖巛巫已巵帋帚帙帑帛帶帷幄幃幀幎幗幔幟幢幤幇幵并幺麼广庠廁廂廈廐廏廖廣廝廚廛廢廡廨廩廬廱廳廰廴廸廾弃弉彝彜弋弑弖弩弭弸彁彈彌彎弯彑彖彗彙彡彭彳彷徃徂彿徊很徑徇從徙徘徠徨徭徼忖忻忤忸忱忝悳忿怡恠怙怐怩怎怱怛怕怫怦怏怺恚恁恪恷恟恊恆恍恣恃恤恂恬恫恙悁悍惧悃悚悄悛悖悗悒悧悋惡悸惠惓悴忰悽惆悵惘慍愕愆惶惷愀惴惺愃愡惻惱愍愎慇愾愨愧慊愿愼愬愴愽慂慄慳慷慘慙慚慫慴慯慥慱慟慝慓慵憙憖憇憬憔憚憊憑憫憮懌懊應懷懈懃懆憺懋罹懍懦懣懶懺懴懿懽懼懾戀戈戉戍戌戔戛戞戡截戮戰戲戳扁扎扞扣扛扠扨扼抂抉找抒抓抖拔抃抔拗拑抻拏拿拆擔拈拜拌拊拂拇抛拉挌拮拱挧挂挈拯拵捐挾捍搜捏掖掎掀掫捶掣掏掉掟掵捫捩掾揩揀揆揣揉插揶揄搖搴搆搓搦搶攝搗搨搏摧摯摶摎攪撕撓撥撩撈撼據擒擅擇撻擘擂擱擧舉擠擡抬擣擯攬擶擴擲擺攀擽攘攜攅攤攣攫攴攵攷收攸畋效敖敕敍敘敞敝敲數斂斃變斛斟斫斷旃旆旁旄旌旒旛旙无旡旱杲昊昃旻杳昵昶昴昜晏晄晉晁晞晝晤晧晨晟晢晰暃暈暎暉暄暘暝曁暹曉暾暼曄暸曖曚曠昿曦曩曰曵曷朏朖朞朦朧霸朮朿朶杁朸朷杆杞杠杙杣杤枉杰枩杼杪枌枋枦枡枅枷柯枴柬枳柩枸柤柞柝柢柮枹柎柆柧檜栞框栩桀桍栲桎梳栫桙档桷桿梟梏梭梔條梛梃檮梹桴梵梠梺椏梍桾椁棊椈棘椢椦棡椌棍棔棧棕椶椒椄棗棣椥棹棠棯椨椪椚椣椡棆楹楷楜楸楫楔楾楮椹楴椽楙椰楡楞楝榁楪榲榮槐榿槁槓榾槎寨槊槝榻槃榧樮榑榠榜榕榴槞槨樂樛槿權槹槲槧樅榱樞槭樔槫樊樒櫁樣樓橄樌橲樶橸橇橢橙橦橈樸樢檐檍檠檄檢檣檗蘗檻櫃櫂檸檳檬櫞櫑櫟檪櫚櫪櫻欅蘖櫺欒欖鬱欟欸欷盜欹飮歇歃歉歐歙歔歛歟歡歸歹歿殀殄殃殍殘殕殞殤殪殫殯殲殱殳殷殼毆毋毓毟毬毫毳毯麾氈氓气氛氤氣汞汕汢汪沂沍沚沁沛汾汨汳沒沐泄泱泓沽泗泅泝沮沱沾沺泛泯泙泪洟衍洶洫洽洸洙洵洳洒洌浣涓浤浚浹浙涎涕濤涅淹渕渊涵淇淦涸淆淬淞淌淨淒淅淺淙淤淕淪淮渭湮渮渙湲湟渾渣湫渫湶湍渟湃渺湎渤滿渝游溂溪溘滉溷滓溽溯滄溲滔滕溏溥滂溟潁漑灌滬滸滾漿滲漱滯漲滌漾漓滷澆潺潸澁澀潯潛濳潭澂潼潘澎澑濂潦澳澣澡澤澹濆澪濟濕濬濔濘濱濮濛瀉瀋濺瀑瀁瀏濾瀛瀚潴瀝瀘瀟瀰瀾瀲灑灣炙炒炯烱炬炸炳炮烟烋烝烙焉烽焜焙煥煕熈煦煢煌煖煬熏燻熄熕熨熬燗熹熾燒燉燔燎燠燬燧燵燼燹燿爍爐爛爨爭爬爰爲爻爼爿牀牆牋牘牴牾犂犁犇犒犖犢犧犹犲狃狆狄狎狒狢狠狡狹狷倏猗猊猜猖猝猴猯猩猥猾獎獏默獗獪獨獰獸獵獻獺珈玳珎玻珀珥珮珞璢琅瑯琥珸琲琺瑕琿瑟瑙瑁瑜瑩瑰瑣瑪瑶瑾璋璞璧瓊瓏瓔珱瓠瓣瓧瓩瓮瓲瓰瓱瓸瓷甄甃甅甌甎甍甕甓甞甦甬甼畄畍畊畉畛畆畚畩畤畧畫畭畸當疆疇畴疊疉疂疔疚疝疥疣痂疳痃疵疽疸疼疱痍痊痒痙痣痞痾痿痼瘁痰痺痲痳瘋瘍瘉瘟瘧瘠瘡瘢瘤瘴瘰瘻癇癈癆癜癘癡癢癨癩癪癧癬癰癲癶癸發皀皃皈皋皎皖皓皙皚皰皴皸皹皺盂盍盖盒盞盡盥盧盪蘯盻眈眇眄眩眤眞眥眦眛眷眸睇睚睨睫睛睥睿睾睹瞎瞋瞑瞠瞞瞰瞶瞹瞿瞼瞽瞻矇矍矗矚矜矣矮矼砌砒礦砠礪硅碎硴碆硼碚碌碣碵碪碯磑磆磋磔碾碼磅磊磬磧磚磽磴礇礒礑礙礬礫祀祠祗祟祚祕祓祺祿禊禝禧齋禪禮禳禹禺秉秕秧秬秡秣稈稍稘稙稠稟禀稱稻稾稷穃穗穉穡穢穩龝穰穹穽窈窗窕窘窖窩竈窰窶竅竄窿邃竇竊竍竏竕竓站竚竝竡竢竦竭竰笂笏笊笆笳笘笙笞笵笨笶筐筺笄筍笋筌筅筵筥筴筧筰筱筬筮箝箘箟箍箜箚箋箒箏筝箙篋篁篌篏箴篆篝篩簑簔篦篥籠簀簇簓篳篷簗簍篶簣簧簪簟簷簫簽籌籃籔籏籀籐籘籟籤籖籥籬籵粃粐粤粭粢粫粡粨粳粲粱粮粹粽糀糅糂糘糒糜糢鬻糯糲糴糶糺紆紂紜紕紊絅絋紮紲紿紵絆絳絖絎絲絨絮絏絣經綉絛綏絽綛綺綮綣綵緇綽綫總綢綯緜綸綟綰緘緝緤緞緻緲緡縅縊縣縡縒縱縟縉縋縢繆繦縻縵縹繃縷縲縺繧繝繖繞繙繚繹繪繩繼繻纃緕繽辮繿纈纉續纒纐纓纔纖纎纛纜缸缺罅罌罍罎罐网罕罔罘罟罠罨罩罧罸羂羆羃羈羇羌羔羞羝羚羣羯羲羹羮羶羸譱翅翆翊翕翔翡翦翩翳翹飜耆耄耋耒耘耙耜耡耨耿耻聊聆聒聘聚聟聢聨聳聲聰聶聹聽聿肄肆肅肛肓肚肭冐肬胛胥胙胝胄胚胖脉胯胱脛脩脣脯腋隋腆脾腓腑胼腱腮腥腦腴膃膈膊膀膂膠膕膤膣腟膓膩膰膵膾膸膽臀臂膺臉臍臑臙臘臈臚臟臠臧臺臻臾舁舂舅與舊舍舐舖舩舫舸舳艀艙艘艝艚艟艤艢艨艪艫舮艱艷艸艾芍芒芫芟芻芬苡苣苟苒苴苳苺莓范苻苹苞茆苜茉苙茵茴茖茲茱荀茹荐荅茯茫茗茘莅莚莪莟莢莖茣莎莇莊荼莵荳荵莠莉莨菴萓菫菎菽萃菘萋菁菷萇菠菲萍萢萠莽萸蔆菻葭萪萼蕚蒄葷葫蒭葮蒂葩葆萬葯葹萵蓊葢蒹蒿蒟蓙蓍蒻蓚蓐蓁蓆蓖蒡蔡蓿蓴蔗蔘蔬蔟蔕蔔蓼蕀蕣蕘蕈蕁蘂蕋蕕薀薤薈薑薊薨蕭薔薛藪薇薜蕷蕾薐藉薺藏薹藐藕藝藥藜藹蘊蘓蘋藾藺蘆蘢蘚蘰蘿虍乕虔號虧虱蚓蚣蚩蚪蚋蚌蚶蚯蛄蛆蚰蛉蠣蚫蛔蛞蛩蛬蛟蛛蛯蜒蜆蜈蜀蜃蛻蜑蜉蜍蛹蜊蜴蜿蜷蜻蜥蜩蜚蝠蝟蝸蝌蝎蝴蝗蝨蝮蝙蝓蝣蝪蠅螢螟螂螯蟋螽蟀蟐雖螫蟄螳蟇蟆螻蟯蟲蟠蠏蠍蟾蟶蟷蠎蟒蠑蠖蠕蠢蠡蠱蠶蠹蠧蠻衄衂衒衙衞衢衫袁衾袞衵衽袵衲袂袗袒袮袙袢袍袤袰袿袱裃裄裔裘裙裝裹褂裼裴裨裲褄褌褊褓襃褞褥褪褫襁襄褻褶褸襌褝襠襞襦襤襭襪襯襴襷襾覃覈覊覓覘覡覩覦覬覯覲覺覽覿觀觚觜觝觧觴觸訃訖訐訌訛訝訥訶詁詛詒詆詈詼詭詬詢誅誂誄誨誡誑誥誦誚誣諄諍諂諚諫諳諧諤諱謔諠諢諷諞諛謌謇謚諡謖謐謗謠謳鞫謦謫謾謨譁譌譏譎證譖譛譚譫譟譬譯譴譽讀讌讎讒讓讖讙讚谺豁谿豈豌豎豐豕豢豬豸豺貂貉貅貊貍貎貔豼貘戝貭貪貽貲貳貮貶賈賁賤賣賚賽賺賻贄贅贊贇贏贍贐齎贓賍贔贖赧赭赱赳趁趙跂趾趺跏跚跖跌跛跋跪跫跟跣跼踈踉跿踝踞踐踟蹂踵踰踴蹊蹇蹉蹌蹐蹈蹙蹤蹠踪蹣蹕蹶蹲蹼躁躇躅躄躋躊躓躑躔躙躪躡躬躰軆躱躾軅軈軋軛軣軼軻軫軾輊輅輕輒輙輓輜輟輛輌輦輳輻輹轅轂輾轌轉轆轎轗轜轢轣轤辜辟辣辭辯辷迚迥迢迪迯邇迴逅迹迺逑逕逡逍逞逖逋逧逶逵逹迸遏遐遑遒逎遉逾遖遘遞遨遯遶隨遲邂遽邁邀邊邉邏邨邯邱邵郢郤扈郛鄂鄒鄙鄲鄰酊酖酘酣酥酩酳酲醋醉醂醢醫醯醪醵醴醺釀釁釉釋釐釖釟釡釛釼釵釶鈞釿鈔鈬鈕鈑鉞鉗鉅鉉鉤鉈銕鈿鉋鉐銜銖銓銛鉚鋏銹銷鋩錏鋺鍄錮錙錢錚錣錺錵錻鍜鍠鍼鍮鍖鎰鎬鎭鎔鎹鏖鏗鏨鏥鏘鏃鏝鏐鏈鏤鐚鐔鐓鐃鐇鐐鐶鐫鐵鐡鐺鑁鑒鑄鑛鑠鑢鑞鑪鈩鑰鑵鑷鑽鑚鑼鑾钁鑿閂閇閊閔閖閘閙閠閨閧閭閼閻閹閾闊濶闃闍闌闕闔闖關闡闥闢阡阨阮阯陂陌陏陋陷陜陞陝陟陦陲陬隍隘隕隗險隧隱隲隰隴隶隸隹雎雋雉雍襍雜霍雕雹霄霆霈霓霎霑霏霖霙霤霪霰霹霽霾靄靆靈靂靉靜靠靤靦靨勒靫靱靹鞅靼鞁靺鞆鞋鞏鞐鞜鞨鞦鞣鞳鞴韃韆韈韋韜韭齏韲竟韶韵頏頌頸頤頡頷頽顆顏顋顫顯顰顱顴顳颪颯颱颶飄飃飆飩飫餃餉餒餔餘餡餝餞餤餠餬餮餽餾饂饉饅饐饋饑饒饌饕馗馘馥馭馮馼駟駛駝駘駑駭駮駱駲駻駸騁騏騅駢騙騫騷驅驂驀驃騾驕驍驛驗驟驢驥驤驩驫驪骭骰骼髀髏髑髓體髞髟髢髣髦髯髫髮髴髱髷髻鬆鬘鬚鬟鬢鬣鬥鬧鬨鬩鬪鬮鬯鬲魄魃魏魍魎魑魘魴鮓鮃鮑鮖鮗鮟鮠鮨鮴鯀鯊鮹鯆鯏鯑鯒鯣鯢鯤鯔鯡鰺鯲鯱鯰鰕鰔鰉鰓鰌鰆鰈鰒鰊鰄鰮鰛鰥鰤鰡鰰鱇鰲鱆鰾鱚鱠鱧鱶鱸鳧鳬鳰鴉鴈鳫鴃鴆鴪鴦鶯鴣鴟鵄鴕鴒鵁鴿鴾鵆鵈鵝鵞鵤鵑鵐鵙鵲鶉鶇鶫鵯鵺鶚鶤鶩鶲鷄鷁鶻鶸鶺鷆鷏鷂鷙鷓鷸鷦鷭鷯鷽鸚鸛鸞鹵鹹鹽麁麈麋麌麒麕麑麝麥麩麸麪麭靡黌黎黏黐黔黜點黝黠黥黨黯黴黶黷黹黻黼黽鼇鼈皷鼕鼡鼬鼾齊齒齔齣齟齠齡齦齧齬齪齷齲齶龕龜龠堯槇遙瑤凜熙"

bot.gguide = """思惟奈ちゃんのグローバルチャット利用規約 最終更新 2020/02/22
1.思惟奈ちゃんグローバルチャットで発言を行った時点で、この規約に同意したものとする。
2.規約違反者の扱い
  運営での話し合いのうえ、処罰内容は変動するものとする。(行った行為の重大さ等によって判断される。)
3.グローバルチャットに、以下のようなテキスト、画像、そのようなコンテンツにつながるURLを投稿することを禁止する。
  ただし、グローバルチャット作成者、およびグローバルモデレーターは、管理運営に必要な場合は、投稿してもよいとする。
  ・年齢制限の必要なもの
  ・閲覧に金銭や個人情報が必要なもの(ただし、これによって投稿などにログインが必要なサイトのリンク投稿を制限するものではない)
  ・Discordのサーバー招待。ただし新機能のテストのために、「思惟奈ちゃん更新関係サーバー」に誘導する場合など、一部の例外を除く。これによって他のグローバルチャットのグローバルチャンネル名の送信を禁止するものではない。
  ・意味のない文字列の羅列。ただし、接続テストの場合を除く。
  ・その他法律、Discord利用規約に違反するもの
  このうちいくつかの項目に関しては、自動的に送信がブロックされるものもある。
4.グローバルチャット製作者および、グローバルモデレーターは、利用者のできることに加えて、次の行為を行うことができる。
  ・利用者の使用禁止状態の切り替え
  ・オリジナルメッセージサーバーにいない状態での投稿の削除
5.グローバルチャットにて、ほかのサーバーに送信される項目は、以下のとおりである。
  ・メッセージ内容、付属するembed、添付されたファイル、返信元の投稿内容、一部スタンプ
  ・ユーザーのid、投稿時にオフラインでないデバイス(PC,moblie,webの三通り)
  ・送信したサーバーの名前、アイコン、id
  ・投稿時間
  また、送信された内容に関して次のような行為が加わった際にはそれが反映される。
  ・メッセージ内容の変更
  ・オリジナルメッセージの削除
6.この規約は`s-globalguide`でいつでも見ることができる。
7.改定
  ・制作者が予告なしに改定することがある。改定後は、グローバルチャットにて報告される。
  ・予告して改定した場合も、同じように改定後に報告する。
"""


@tasks.loop(minutes=20.0)
async def cRPC():
    global rpcct
    if rpcct == 7:
        rpcct = 0
    else:
        rpcct = rpcct+1
    await bot.change_presence(status=discord.Status.online, activity=discord.Game(name=rpcs[rpcct].format(len(bot.guilds), len(bot.users), bot.shard_id)))



@bot.event
async def on_ready():
    global aglch
    print('ログインしました。')
    print(bot.user.name)
    print(bot.user.id)
    print('------------------')
    aglch = bot.get_channel(659706303521751072)
    pmsgc = bot.get_channel(676371380111015946)
    cRPC.start()
    """invite_tweet.start()
    now_sina_tweet.start()"""
    await bot.load_extension("jishaku")
    
    files = [
            "m10s_info", "m10s_owner", "m10s_settings", "m10s_manage",
            "m10s_other", "m10s_search", "m10s_games", "P143_jyanken",
            "nekok500_mee6", "pf9_symmetry", "syouma", #"m10s_bmail",
            "m10s_auth_wiz",
            "m10s_role_panel", "m10s_partners", "m10s_remainder", "m10s_set_activity_roles",

            "m10s_api", "takumi_twinotif",
            "m10s_app_metadata",
            
            # "__part_pjsekai_music_select"
            "slash.pjsekai_music_select", # 思惟奈ちゃんパートナー向け機能-ぱすこみゅ
            "slash.mini_features", # -> スポイラー展開
            "slash.m10s_messageinfo", # -> メッセージコマンドでの実行

            "hybrid.m10s_re_gchat",
            "hybrid.m10s_quick_cmd",
            "hybrid.m10s_levels",
            "hybrid.m10s_music",
            "hybrid.info_check",
            "hybrid.m10s_help",
            "m10s_guild_log"
            ]
    
    embed = discord.Embed(title="読み込みに失敗したCog", color=bot.ec)
    txt = ""
    for file in files:
        try:
            await bot.load_extension(f"cogs.{file}")
        except:

            traceback.print_exc()
            print(f"Extension {file} Load Failed.")
            txt += f"`{file}`, "
        else:
            print(f"Extension {file} Load.")
    embed.description = txt

    # テストサバ
    # await bot.tree.sync(guild=discord.Object(id=560434525277126656))

    # パートナーコマンド
    # await bot.tree.sync(guild=discord.Object(id=764088457785638922))

    # グローバルコマンド
    await bot.tree.sync()

    boot_info_channel_id = 595526013031546890

    try:
        ch = bot.get_channel(boot_info_channel_id)
        if ch == None:
            try:
                await bot.fetch_channel(boot_info_channel_id)
            except:
                return
        e=discord.Embed(title="起動時インフォメーション", description=f"シャードID:{bot.shard_id}\n認識ユーザー数:{len(bot.users)}\n認識サーバー数:{len(bot.guilds)}\n認識チャンネル数:{len([c for c in bot.get_all_channels()])}\ndiscord.py ver_{discord.__version__}", color=bot.ec)
        await ch.send(f"{bot.get_emoji(653161518531215390)}on_ready!", embed=e)
        if txt:
            await ch.send(embed=embed)
    except:
        pass


@bot.event
async def on_message(message):
    if "cu:on_msg" in bot.features.get(message.author.id, []):
        return
    if "cu:on_msg" in bot.features.get(message.guild.id, []):
        return
    if isinstance(message.channel, discord.DMChannel):
        return
    if message.webhook_id:
        return
    if message.author.id == bot.user.id:
        return
    if postcount.get(str(message.guild.id), None) is None:
        postcount[str(message.guild.id)] = 1
    else:
        postcount[str(message.guild.id)] += 1
    # if message.content == "check_msgs":
        # on_messageを呼ぶだけの処理がすぐに終わるかの確認
        # with open("post_count.json", mode="w", encoding="utf-8") as f:
            # json.dump(postcount, f, indent=4)
        # await message.channel.send(file=discord.File("post_count.json"))
    # db.files_download_to_file( "guildsetting.json" , "/guildsetting.json" )
    # db.files_download_to_file( "profiles.json" , "/profiles.json" )
    tks = [
        domsg(message)
        # globalSend(message), グローバルチャットは進化した！ -> cogs.m10s_re_gchat
    ]
    await asyncio.gather(*tks)
    # await domsg(message)
    # await globalSend(message)


async def domsg(message):
    global DoServercmd

    if not message.author.id in bot.team_sina:
        if bot.maintenance:
            return
        else:
            pass
    else:
        pass

    gs = await bot.cursor.fetchone("select * from guilds where id=%s", (message.guild.id,))
    #gs = await bot.cursor.fetchone()
    if not gs:
        guild_lang = await bot.translate_handler.get_lang_by_guild(
            message.guild, False)
        await bot.cursor.execute("INSERT INTO guilds(id,levels,commands,hash,levelupsendto,reward,jltasks,lockcom,sendlog,prefix,lang,verified) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                           (message.guild.id, "{}", "{}", "[]", None, "{}", "{}", "[]", None, "[]", guild_lang, 0))
        try:
            await message.channel.send(f"{bot.get_emoji(653161518153596950)}このサーバーの思惟奈ちゃんサーバープロファイルを作成しました！いくつかの項目はコマンドを使って書き換えることができます。詳しくはヘルプ(`s-help`)をご覧ください。\nまた、不具合や疑問点などがありましたら`mii-10#3110`にお願いします。\n思惟奈ちゃんのお知らせは`/rnotify [チャンネル(省略可能)]`で、コマンド等の豆知識は`/rtopic [チャンネル(省略可能)]`で受信する設定にできます。(Webhook管理権限が必要です。)")
        except:
            pass
        gs = await bot.cursor.fetchone("select * from guilds where id=%s",
                           (message.guild.id,))
        #gs = await bot.cursor.fetchone()

    pf = await bot.cursor.fetchone("select * from users where id=%s", (message.author.id,))
    #pf = await bot.cursor.fetchone()
    if not pf:
        if message.is_system():
            return
        
        try:
            await bot.cursor.execute("INSERT INTO users(id,prefix,gpoint,memo,levcard,onnotif,lang,sinapartner,gban,gnick,gcolor,gmod,gstar,galpha,gbanhist,online_agreed) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                        (message.author.id, "[]", 0, "{}", "m@ji☆", "[]", "ja", 0, 0, message.author.name, 0, 0, 0, 0, "なし",0))
        except Exception as exc:
            print(exc)
            
        try:
            if not "disable_profile_msg" in json.loads(gs["lockcom"]):
                await message.add_reaction(bot.get_emoji(653161518153596950))
        except:
            pass
        pf = await bot.cursor.fetchone("select * from users where id=%s",
                        (message.author.id,))
        #pf = await bot.cursor.fetchone()

    """await bot.cursor.execute(
    "CREATE TABLE IF NOT EXISTS actrole_optin(id integer PRIMARY KEY NOT NULL, is_enable integer NOT NULL default 0);")"""

    data = await bot.cursor.fetchone("select * from actrole_optin where id=%s", (message.author.id,))
    if not data:
        if message.is_system():
            return
        await bot.cursor.execute("INSERT INTO actrole_optin(id,is_enable) VALUES(%s,%s)",
                        (message.author.id, 0))
        data = await bot.cursor.execute("select * from actrole_optin where id=%s",
                        (message.author.id,))


    tks = [
        asyncio.ensure_future(gahash(message, gs)),
        asyncio.ensure_future(runsercmd(message, gs, pf))
    ]
    await asyncio.gather(*tks)

    tpf = json.loads(pf["prefix"]) + json.loads(gs["prefix"])
    if not ("disable_defprefix" in json.loads(gs["lockcom"])):
        tpf.insert(0,"s-")
    bot.command_prefix = tpf
    bot.comlocks[str(message.guild.id)] = json.loads(gs["lockcom"])
    """for pf in tpf:
        if message.content.startswith(pf):
            if "disable_prefix_cmd" in bot.features[0]:
                await message.channel.send("> お知らせ\n　メッセージコンテントインテントの特権化に伴い、ご利用の呼び出し方法はサポートされません。\n　スラッシュコマンドで利用していただくよう、お願いします。")
                break
            else:
                await message.channel.send("> お知らせ\n　メッセージコンテントインテントの特権化に伴い、ご利用の呼び出し方法は近日サポートを終了します。\n　スラッシュコマンドで利用していただくよう、お願いします。")
                break
    if not "disable_prefix_cmd" in bot.features[0]:"""
    await bot.process_commands(message)

async def runsercmd(message, gs, pf):
    if "cu:cmd" in bot.features.get(message.author.id, []):
        return
    if "cu:cmd" in bot.features.get(message.guild.id, []):
        return
    # servercmd
    if "scom" not in json.loads(gs["lockcom"]):
        if not message.author.id == bot.user.id and message.webhook_id is None:
            tpf = json.loads(pf["prefix"]) + json.loads(gs["prefix"])
            tpf.append("s-")
            try:
                if not json.loads(gs["commands"]) is None:
                    cmds = json.loads(gs["commands"])
                    ctts = message.content.split(" ")
                    for k, v in cmds.items():
                        for px in tpf:
                            if px+k == ctts[0]:
                                DoServercmd = True
                                if v["mode"] == "random":
                                    await message.channel.send(random.choice(v["rep"]))
                                elif v["mode"] == "one":
                                    await message.channel.send(v["rep"])
                                elif v["mode"] == "role":
                                    try:
                                        role = message.guild.get_role(v["rep"])
                                    except:
                                        await message.channel.send(await bot._(message.author, "scmd-notfound-role"))
                                        return
                                    if role < message.author.top_role:
                                        if role in message.author.roles:
                                            await message.author.remove_roles(role)
                                            await message.channel.send(await bot._(message.author, "scmd-delrole"))
                                        else:
                                            await message.author.add_roles(role)
                                            await message.channel.send(await bot._(message.author, "scmd-addrole"))
                                    else:
                                        await message.channel.send(await bot._(message.author, "scmd-notrole"))
                                break
            except:
                pass


async def gahash(message, gs):
    # hash
    if "cu:auto_sends" in bot.features.get(message.author.id,[]):
        return
    if "cu:auto_sends" in bot.features.get(message.guild.id,[]):
        return
    try:
        if "s-noHashSend" in (message.channel.topic or ""):
            return
    except:
        pass
    if "shash" not in json.loads(gs["lockcom"]):
        ch = json.loads(gs["hash"])
        if ch is not []:
            menchan = message.channel_mentions
            for sch in menchan:
                if sch.id in ch:
                    if message.channel.is_nsfw():
                        embed = discord.Embed(title="", description=await bot.l10n_guild(
                            message.guild, "hash-nsfw"), color=message.author.color)
                        embed.add_field(name=await bot.l10n_guild(message.guild, "hash-from"),
                                        value=f'{await bot.l10n_guild(message.guild,"hash-chmention")}:{message.channel.mention}\n{await bot.l10n_guild(message.guild,"hash-chname")}:{message.channel.name}')
                        embed.add_field(name=await bot.l10n_guild(
                            message.guild, "hash-link"), value=message.jump_url)
                        embed.set_author(name=message.author.display_name, icon_url=message.author.display_avatar.replace(
                            static_format='png'))
                    else:
                        embed = discord.Embed(
                            title="", description=message.content, color=message.author.color)
                        embed.add_field(name=await bot.l10n_guild(message.guild, "hash-from"),
                                        value=f'{await bot.l10n_guild(message.guild,"hash-chmention")}:{message.channel.mention}\n{await bot.l10n_guild(message.guild,"hash-chname")}:{message.channel.name}')
                        embed.add_field(name=await bot.l10n_guild(
                            message.guild, "hash-link"), value=message.jump_url)
                        embed.set_author(name=message.author.display_name, icon_url=message.author.display_avatar.replace(
                            static_format='png'))
                        if not message.attachments == [] and (not message.attachments[0].is_spoiler()):
                            embed.set_image(url=message.attachments[0].url)
                    await sch.send(embed=embed)



@commands.is_owner()
@ut.runnable_check()
@bot.command()
async def ldb(ctx, name):
    sddb = await bot.cursor.fetchall(f"select * from {name}")
    #sddb = await bot.cursor.fetchall()
    await ctx.send(f"{len(sddb)}")


@commands.is_owner()
@ut.runnable_check()
@bot.command()
async def mentdb(ctx):
    sddb = await bot.cursor.fetchall(f"select * from users")
    #sddb = await bot.cursor.fetchall()
    async with ctx.channel.typing():
        for ctt in sddb:
            if not (ctt["id"] in [i.id for i in bot.users]):
                await bot.cursor.execute(f"delete from users where id = {ctt['id']}")
    await ctx.send("完了しました☆")

@commands.is_owner()
@ut.runnable_check()
@bot.command()
async def maintenance(ctx):
    if bot.maintenance:
        bot.maintenance = False
        await ctx.send("falseにしたよ")
    else:
        bot.maintenance = True
        await ctx.send("trueにしたよ")

@bot.command(description="思惟奈ちゃんの豆知識チャンネルをフォローします。")
@app_commands.describe(ch="受け取るチャンネル")
@commands.bot_has_permissions(manage_webhooks=True)
@commands.has_permissions(administrator=True)
@app_commands.checks.bot_has_permissions(manage_webhooks=True)
@app_commands.checks.has_permissions(administrator=True)
@ut.runnable_check()
async def rnotify(ctx, ch: discord.TextChannel=None):
    if ctx.author.guild_permissions.administrator or ctx.author.id == 404243934210949120:
        tch = ch or ctx.channel
        fch = bot.get_channel(667351221106901042)
        await fch.follow(destination=tch)
        await ctx.send("フォローが完了しました。")
    else:
        await ctx.send("サーバー管理者である必要があります。")


@bot.hybrid_command(description="トピックチャンネルをフォローします")
@app_commands.describe(ch="受け取るチャンネル")
@commands.bot_has_permissions(manage_webhooks=True)
@commands.has_permissions(administrator=True)
@app_commands.checks.bot_has_permissions(manage_webhooks=True)
@app_commands.checks.has_permissions(administrator=True)
@ut.runnable_check()
async def rtopic(ctx, ch:discord.TextChannel=None):
    if ctx.author.guild_permissions.administrator or ctx.author.id == 404243934210949120:
        tch = ch or ctx.channel
        fch = bot.get_channel(677862542298710037)
        await fch.follow(destination=tch)
        await ctx.send("フォローが完了しました。")
    else:
        await ctx.send("サーバー管理者である必要があります。")



@bot.event
async def on_command(ctx:commands.Context):
    if ctx.interaction:return
    ch = bot.get_channel(693048961107230811)
    e = discord.Embed(title=f"prefixコマンド:{ctx.command.full_parent_name}の実行",
                      description=f"実行文:`{ctx.message.clean_content}`", color=bot.ec)
    e.set_author(name=f"実行者:{str(ctx.author)}({ctx.author.id})",
                 icon_url=ctx.author.display_avatar.replace(static_format="png").url)
    if ctx.guild.icon:
        e.set_footer(text=f"実行サーバー:{ctx.guild.name}({ctx.guild.id})",
                    icon_url=ctx.guild.icon.replace(static_format="png").url)
    else:
        e.set_footer(text=f"実行サーバー:{ctx.guild.name}({ctx.guild.id})")
    e.add_field(name="実行チャンネル", value=ctx.channel.name)
    e.timestamp = ctx.message.created_at
    await ch.send(embed=e)

@bot.event
async def on_interaction(interaction:discord.Interaction):
    ch = bot.get_channel(693048961107230811)
    e = discord.Embed(title=f"スラッシュコマンド:{interaction.command.qualified_name}の実行",color=bot.ec)
    e.set_author(name=f"実行者:{str(interaction.user)}({interaction.user.id})",
                 icon_url=interaction.user.display_avatar.replace(static_format="png").url)
    if interaction.guild.icon:
        e.set_footer(text=f"実行サーバー:{interaction.guild.name}({interaction.guild.id})",
                    icon_url=interaction.guild.icon.replace(static_format="png").url)
    else:
        e.set_footer(text=f"実行サーバー:{interaction.guild.name}({interaction.guild.id})")
    e.add_field(name="実行チャンネル", value=interaction.channel.name)
    e.timestamp = interaction.created_at
    await ch.send(embed=e)


@bot.event
async def on_command_error(ctx, error):
    # await ctx.send(f"{error}")
    # global DoServercmd
    """if isinstance(error, commands.CommandNotFound):
        if not DoServercmd:
            embed = discord.Embed(title=await ctx._("cmd-error-t"), description=await ctx._("cmd-notfound-d"), color=bot.ec)
            DoServercmd = False
            await ctx.send(embed=embed)
    el"""
    if isinstance(error, commands.CommandOnCooldown):
        # クールダウン
        embed = discord.Embed(title=await ctx._("cmd-error-t"), description=await ctx._(
            "cmd-cooldown-d", str(error.retry_after)[:4]), color=bot.ec)
        await ctx.send(embed=embed)
    elif isinstance(error, commands.NotOwner):
        # オーナー専用コマンド
        embed = discord.Embed(title=await ctx._("cmd-error-t"),
                              description=await ctx._("only-mii-10"), color=bot.ec)
        await ctx.send(embed=embed)
        ch = bot.get_channel(652127085598474242)
        await ch.send(embed=ut.getEmbed("エラーログ", f"コマンド:`{ctx.command.full_parent_name}`\n```{str(error)}```", bot.ec, f"サーバー", ctx.guild.name, "実行メンバー", ctx.author.name, "メッセージ内容", ctx.message.content or "(本文なし)"))
    elif isinstance(error, commands.MissingRequiredArgument):
        # 引数がないよっ☆
        embed = discord.Embed(title=await ctx._("cmd-error-t"),
                              description=await ctx._("pls-arg"), color=bot.ec)
        await ctx.send(embed=embed)
    elif isinstance(error, commands.MissingPermissions):
        embed = discord.Embed(title=await ctx._("cmd-error-t"),
                              description=f"このコマンドの実行には、あなたに次の権限が必要です。\n```py\n{error.missing_perms}```", color=bot.ec)
        try:
            await ctx.send(embed=embed)
        except:
            await ctx.send(f'> {await ctx._("cmd-error-t")}\n　このコマンドの実行には、あなたに次の権限が必要です。\n```py\n{error.missing_perms}```')
    elif isinstance(error, commands.BotMissingPermissions):
        embed = discord.Embed(title=await ctx._("cmd-error-t"),
                              description=f"このコマンドの実行には、Botに次の権限が必要です。\n```py\n{error.missing_perms}```", color=bot.ec)
        try:
            await ctx.send(embed=embed)
        except:
            await ctx.send(f'> {await ctx._("cmd-error-t")}\n　このコマンドの実行には、Botに次の権限が必要です。\n```py\n{error.missing_perms}```')
    elif isinstance(error, commands.CheckFailure):
        embed = discord.Embed(title=await ctx._("cmd-error-t"), description="comlock、メンテナンス、使用制限等、実行時チェックを通過できなかったため、コマンド実行が失敗しました。", color=bot.ec)
        try:
            await ctx.send(embed=embed)
        except:
            await ctx.send(f'> {await ctx._("cmd-error-t")}\n　comlock、メンテナンス、使用制限等、実行時チェックを通過できなかったため、コマンド実行が失敗しました。')

    else:
        # その他例外
        ch = bot.get_channel(652127085598474242)
        msg = await ch.send(embed=ut.getEmbed("エラーログ", f"コマンド:`{ctx.command.full_parent_name}`\n```{str(error)}```", bot.ec, f"サーバー", ctx.guild.name, "実行メンバー", ctx.author.name, "メッセージ内容", ctx.message.content or "(本文なし)"))
        await ctx.send(embed=ut.getEmbed(await ctx._("com-error-t"), await ctx._("cmd-other-d", "詳細は無効化されています…。"), bot.ec, "error id", msg.id, "サポートが必要ですか？", "[サポートサーバー](https://discord.gg/vtn2V3v)に参加して、「view-思惟奈ちゃんch」役職をつけて質問してみましょう！"))


"""
@tasks.loop(time=datetime.time(hour=23,minute=0,second=0))
async def invite_tweet():
    try:
        bot.twi.statuses.update(status=f"[定期投稿]\nみぃてん☆の公開Discordサーバー:https://discord.gg/GbHq7fz\nみぃてん☆制作、多機能Discordbot思惟奈ちゃん:https://discordapp.com/oauth2/authorize?client_id=462885760043843584&permissions=8&scope=bot\n<この投稿は思惟奈ちゃんより行われました。>")
    except:
        dc=bot.get_user(404243934210949120)
        await dc.send(f"have error:```{traceback.format_exc(1)}```")
@tasks.loop(time=datetime.time(hour=8,minute=0,second=0))
async def now_sina_tweet():
    try:
        bot.twi.statuses.update(status=f"[定期投稿]\n思惟奈ちゃんのいるサーバー数:{len(bot.guilds)}\n思惟奈ちゃんの公式サーバー:https://discord.gg/udA3qgZ\n<この投稿は思惟奈ちゃんより行われました。>")
    except:
        dc=bot.get_user(404243934210949120)
        await dc.send(f"have error:```{traceback.format_exc(1)}```")
"""


asyncio.run(main())