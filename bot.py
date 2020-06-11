# -*- coding: utf-8 -*- #

from cogs import apple_invite
import discord
from discord.ext import commands, tasks
import json
import random
import wikipedia
import wikidata.client
from PIL import Image, ImageDraw, ImageFont
import time
import asyncio
import datetime
import pickle
import sys
import platform
import re
from twitter import *
from dateutil.relativedelta import relativedelta as rdelta
import traceback
import os
import shutil
import pytz
import sqlite3
import aiohttp

# textto etc
import m10s_util as ut
from apple_util import AppleUtil
from l10n import TranslateHandler, LocalizedContext
from checker import MaliciousInput, content_checker
# tokens
import config
# cog
from cogs import m10s_music
from cogs import m10s_info
from cogs import m10s_owner
from cogs import m10s_settings
from cogs import m10s_manage
from cogs import m10s_levels
from cogs import m10s_tests
from cogs import m10s_gcoms
from cogs import m10s_search
from cogs import m10s_other
from cogs import m10s_games
from cogs import P143_jyanken
from cogs import nekok500_mee6
from cogs import syouma
from cogs import pf9_symmetry
from cogs import apple_foc
from cogs import m10s_gban
from cogs import m10s_bmail
from cogs import m10s_auth_wiz

"""import logging

logging.basicConfig(level=logging.DEBUG)"""

bot = commands.Bot(command_prefix="s-", status=discord.Status.invisible,
                   allowed_mentions=discord.AllowedMentions(everyone=False))
bot.owner_id = 404243934210949120

bot.team_sina = config.team_sina

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

sqlite3.register_converter('pickle', pickle.loads)
sqlite3.register_converter('json', json.loads)
sqlite3.register_adapter(dict, json.dumps)
sqlite3.register_adapter(list, pickle.dumps)
db = sqlite3.connect(
    "sina_datas.db", detect_types=sqlite3.PARSE_DECLTYPES, isolation_level=None)
db.row_factory = sqlite3.Row
bot.cursor = db.cursor()
bot.cursor.execute("CREATE TABLE IF NOT EXISTS users(id integer PRIMARY KEY NOT NULL,prefix pickle,gpoint integer,memo json,levcard text,onnotif pickle,lang text,accounts pickle,sinapartner integer,gban integer,gnick text,gcolor integer,gmod integer,gstar integer,galpha integer,gbanhist text)")
bot.cursor.execute("CREATE TABLE IF NOT EXISTS guilds(id integer PRIMARY KEY NOT NULL,levels json,commands json,hash pickle,levelupsendto integer,reward json,jltasks json,lockcom pickle,sendlog integer,prefix pickle,lang text)")
bot.cursor.execute(
    "CREATE TABLE IF NOT EXISTS globalchs(name text PRIMARY KEY NOT NULL,ids pickle)")
bot.cursor.execute(
    "CREATE TABLE IF NOT EXISTS globaldates(id integer PRIMARY KEY NOT NULL,content text,allid pickle,aid integer,gid integer,timestamp text)")
bot.cursor.execute(
    "CREATE TABLE IF NOT EXISTS invites(id text PRIMARY KEY NOT NULL, guild_id int NOT NULL, uses integer, inviter_id integer NOT NULL);")
bot.cursor.execute(
    "CREATE TABLE IF NOT EXISTS gban_settings(id integer PRIMARY KEY NOT NULL,chid integer);")
bot.cursor.execute(
    "CREATE TABLE IF NOT EXISTS gban_dates(id integer PRIMARY KEY NOT NULL,reason text NOT NULL,gban_by id NOT NULL);")

bot.cursor.execute("CREATE TABLE IF NOT EXISTS welcome_auth(id integer PRIMARY KEY NOT NULL,category integer,use integer NOT NULL,can_view pickle NOT NULL,next_reaction NOT NULL,au_w pickle NOT NULL,give_role integer NOT NULL);")
try:
    bot.cursor.execute("ALTER TABLE users ADD COLUMN online_agreed integer;")
except:
    pass
bot.session = aiohttp.ClientSession(loop=bot.loop)

bot._default_close = bot.close


async def close_handler():
    await bot._default_close()
    await bot.session.close()
    try:
        db.commit()
    except sqlite3.ProgrammingError:
        pass
    else:
        db.close()
bot.close = close_handler

bot.translate_handler = TranslateHandler(bot, ["en", "ja"])
bot._get_context = bot.get_context


async def get_context(msg, cls=LocalizedContext):
    ctx = await bot._get_context(msg, cls=cls)
    ctx.context_at = datetime.datetime.utcnow().timestamp()
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
    "アイコン:おあずさん",
    "サーバー数:{0}",
    "ユーザー数:{1}",
    "作成:チーム☆思惟奈ちゃん",
    "制作リーダー:mii-10#3110",
    "help:s-help",
    "icon:oaz_n",
    "{0}guilds",
    "{1}users",
    "created by mii-10#3110"
]
"""db = dropbox.Dropbox(DROP_TOKEN)
db.users_get_current_account()"""
bot.twi = Twitter(auth=OAuth(
    bot.T_Acs_Token, bot.T_Acs_SToken, bot.T_API_key, bot.T_API_SKey))
bot.ec = 0x42bcf4
Donotif = False
bot.StartTime = datetime.datetime.now()

aglch = None

bot.partnerg = config.pg

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


def can_use_online(user):
    enabled = bot.cursor.execute(
        "SELECT online_agreed FROM users WHERE id = ?", (user.id,)).fetchone()
    return enabled and enabled["online_agreed"]


bot.can_use_online = can_use_online

# 初回ロード
"""db.files_download_to_file( "guildsetting.json" , "/guildsetting.json" )
db.files_download_to_file( "profiles.json" , "/profiles.json" )
db.files_download_to_file( "gp.json" , "/gp.json" )
db.files_download_to_file( "globaldatas.json" , "/globaldatas.json" )
db.files_download_to_file( "gchatchs.json" , "/gchatchs.json" )"""

bot.tl = "　ゔ 、。，．・：；？！゛゜´｀¨＾￣＿ヽヾゝゞ〃仝々〆〇ー―‐／＼～∥｜…‥‘’“”（）〔〕［］｛｝〈〉《》「」『』【】＋－±×÷＝≠＜＞≦≧∞∴♂♀°′″℃￥＄￠￡％＃＆＊＠§☆★○●◎◇◆□■△▲▽▼※〒→←↑↓〓∈∋⊆⊇⊂⊃∪∩∧∨￢⇒⇔∀∃∠⊥⌒∂∇≡≒≪≫√∽∝∵∫∬Å‰♯♭♪†‡¶◯０１２３４５６７８９1234567890ａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚabcdefghijklmnopqrstuvwxyz-^\=~|@[]:;\/.,<>?_+*}{`!\"#$%&'()ぁあぃいぅうぇえぉおかがきぎくぐけげこごさざしじすずせぜそぞただちぢっつづてでとどなにぬねのはばぱひびぴふぶぷへべぺほぼぽまみむめもゃやゅゆょよらりるれろゎわゐゑをんァアィイゥウェエォオカガキギクグケゲコゴサザシジスズセゼソゾタダチヂッツヅテデトドナニヌネノハバパヒビピフブプヘベペホボポマミムメモャヤュユョヨラリルレロヮワヰヱヲンヴヵヶΑΒΓΔΕΖΗΘΙΚΛΜΝΞΟΠΡΣΤΥΦΧΨΩαβγδεζηθικλμνξοπρστυφχψωАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯабвгдеёжзийклмнопрстуфхцчшщъыьэюя─│┌┐┘└├┬┤┴┼━┃┏┓┛┗┣┳┫┻╋┠┯┨┷┿┝┰┥┸╂亜唖娃阿哀愛挨姶逢葵茜穐悪握渥旭葦芦鯵梓圧斡扱宛姐虻飴絢綾鮎或粟袷安庵按暗案闇鞍杏以伊位依偉囲夷委威尉惟意慰易椅為畏異移維緯胃萎衣謂違遺医井亥域育郁磯一壱溢逸稲茨芋鰯允印咽員因姻引飲淫胤蔭院陰隠韻吋右宇烏羽迂雨卯鵜窺丑碓臼渦嘘唄欝蔚鰻姥厩浦瓜閏噂云運雲荏餌叡営嬰影映曳栄永泳洩瑛盈穎頴英衛詠鋭液疫益駅悦謁越閲榎厭円園堰奄宴延怨掩援沿演炎焔煙燕猿縁艶苑薗遠鉛鴛塩於汚甥凹央奥往応押旺横欧殴王翁襖鴬鴎黄岡沖荻億屋憶臆桶牡乙俺卸恩温穏音下化仮何伽価佳加可嘉夏嫁家寡科暇果架歌河火珂禍禾稼箇花苛茄荷華菓蝦課嘩貨迦過霞蚊俄峨我牙画臥芽蛾賀雅餓駕介会解回塊壊廻快怪悔恢懐戒拐改魁晦械海灰界皆絵芥蟹開階貝凱劾外咳害崖慨概涯碍蓋街該鎧骸浬馨蛙垣柿蛎鈎劃嚇各廓拡撹格核殻獲確穫覚角赫較郭閣隔革学岳楽額顎掛笠樫橿梶鰍潟割喝恰括活渇滑葛褐轄且鰹叶椛樺鞄株兜竃蒲釜鎌噛鴨栢茅萱粥刈苅瓦乾侃冠寒刊勘勧巻喚堪姦完官寛干幹患感慣憾換敢柑桓棺款歓汗漢澗潅環甘監看竿管簡緩缶翰肝艦莞観諌貫還鑑間閑関陥韓館舘丸含岸巌玩癌眼岩翫贋雁頑顔願企伎危喜器基奇嬉寄岐希幾忌揮机旗既期棋棄機帰毅気汽畿祈季稀紀徽規記貴起軌輝飢騎鬼亀偽儀妓宜戯技擬欺犠疑祇義蟻誼議掬菊鞠吉吃喫桔橘詰砧杵黍却客脚虐逆丘久仇休及吸宮弓急救朽求汲泣灸球究窮笈級糾給旧牛去居巨拒拠挙渠虚許距鋸漁禦魚亨享京供侠僑兇競共凶協匡卿叫喬境峡強彊怯恐恭挟教橋況狂狭矯胸脅興蕎郷鏡響饗驚仰凝尭暁業局曲極玉桐粁僅勤均巾錦斤欣欽琴禁禽筋緊芹菌衿襟謹近金吟銀九倶句区狗玖矩苦躯駆駈駒具愚虞喰空偶寓遇隅串櫛釧屑屈掘窟沓靴轡窪熊隈粂栗繰桑鍬勲君薫訓群軍郡卦袈祁係傾刑兄啓圭珪型契形径恵慶慧憩掲携敬景桂渓畦稽系経継繋罫茎荊蛍計詣警軽頚鶏芸迎鯨劇戟撃激隙桁傑欠決潔穴結血訣月件倹倦健兼券剣喧圏堅嫌建憲懸拳捲検権牽犬献研硯絹県肩見謙賢軒遣鍵険顕験鹸元原厳幻弦減源玄現絃舷言諺限乎個古呼固姑孤己庫弧戸故枯湖狐糊袴股胡菰虎誇跨鈷雇顧鼓五互伍午呉吾娯後御悟梧檎瑚碁語誤護醐乞鯉交佼侯候倖光公功効勾厚口向后喉坑垢好孔孝宏工巧巷幸広庚康弘恒慌抗拘控攻昂晃更杭校梗構江洪浩港溝甲皇硬稿糠紅紘絞綱耕考肯肱腔膏航荒行衡講貢購郊酵鉱砿鋼閤降項香高鴻剛劫号合壕拷濠豪轟麹克刻告国穀酷鵠黒獄漉腰甑忽惚骨狛込此頃今困坤墾婚恨懇昏昆根梱混痕紺艮魂些佐叉唆嵯左差査沙瑳砂詐鎖裟坐座挫債催再最哉塞妻宰彩才採栽歳済災采犀砕砦祭斎細菜裁載際剤在材罪財冴坂阪堺榊肴咲崎埼碕鷺作削咋搾昨朔柵窄策索錯桜鮭笹匙冊刷察拶撮擦札殺薩雑皐鯖捌錆鮫皿晒三傘参山惨撒散桟燦珊産算纂蚕讃賛酸餐斬暫残仕仔伺使刺司史嗣四士始姉姿子屍市師志思指支孜斯施旨枝止死氏獅祉私糸紙紫肢脂至視詞詩試誌諮資賜雌飼歯事似侍児字寺慈持時次滋治爾璽痔磁示而耳自蒔辞汐鹿式識鴫竺軸宍雫七叱執失嫉室悉湿漆疾質実蔀篠偲柴芝屡蕊縞舎写射捨赦斜煮社紗者謝車遮蛇邪借勺尺杓灼爵酌釈錫若寂弱惹主取守手朱殊狩珠種腫趣酒首儒受呪寿授樹綬需囚収周宗就州修愁拾洲秀秋終繍習臭舟蒐衆襲讐蹴輯週酋酬集醜什住充十従戎柔汁渋獣縦重銃叔夙宿淑祝縮粛塾熟出術述俊峻春瞬竣舜駿准循旬楯殉淳準潤盾純巡遵醇順処初所暑曙渚庶緒署書薯藷諸助叙女序徐恕鋤除傷償勝匠升召哨商唱嘗奨妾娼宵将小少尚庄床廠彰承抄招掌捷昇昌昭晶松梢樟樵沼消渉湘焼焦照症省硝礁祥称章笑粧紹肖菖蒋蕉衝裳訟証詔詳象賞醤鉦鍾鐘障鞘上丈丞乗冗剰城場壌嬢常情擾条杖浄状畳穣蒸譲醸錠嘱埴飾拭植殖燭織職色触食蝕辱尻伸信侵唇娠寝審心慎振新晋森榛浸深申疹真神秦紳臣芯薪親診身辛進針震人仁刃塵壬尋甚尽腎訊迅陣靭笥諏須酢図厨逗吹垂帥推水炊睡粋翠衰遂酔錐錘随瑞髄崇嵩数枢趨雛据杉椙菅頗雀裾澄摺寸世瀬畝是凄制勢姓征性成政整星晴棲栖正清牲生盛精聖声製西誠誓請逝醒青静斉税脆隻席惜戚斥昔析石積籍績脊責赤跡蹟碩切拙接摂折設窃節説雪絶舌蝉仙先千占宣専尖川戦扇撰栓栴泉浅洗染潜煎煽旋穿箭線繊羨腺舛船薦詮賎践選遷銭銑閃鮮前善漸然全禅繕膳糎噌塑岨措曾曽楚狙疏疎礎祖租粗素組蘇訴阻遡鼠僧創双叢倉喪壮奏爽宋層匝惣想捜掃挿掻操早曹巣槍槽漕燥争痩相窓糟総綜聡草荘葬蒼藻装走送遭鎗霜騒像増憎臓蔵贈造促側則即息捉束測足速俗属賊族続卒袖其揃存孫尊損村遜他多太汰詑唾堕妥惰打柁舵楕陀駄騨体堆対耐岱帯待怠態戴替泰滞胎腿苔袋貸退逮隊黛鯛代台大第醍題鷹滝瀧卓啄宅托択拓沢濯琢託鐸濁諾茸凧蛸只叩但達辰奪脱巽竪辿棚谷狸鱈樽誰丹単嘆坦担探旦歎淡湛炭短端箪綻耽胆蛋誕鍛団壇弾断暖檀段男談値知地弛恥智池痴稚置致蜘遅馳築畜竹筑蓄逐秩窒茶嫡着中仲宙忠抽昼柱注虫衷註酎鋳駐樗瀦猪苧著貯丁兆凋喋寵帖帳庁弔張彫徴懲挑暢朝潮牒町眺聴脹腸蝶調諜超跳銚長頂鳥勅捗直朕沈珍賃鎮陳津墜椎槌追鎚痛通塚栂掴槻佃漬柘辻蔦綴鍔椿潰坪壷嬬紬爪吊釣鶴亭低停偵剃貞呈堤定帝底庭廷弟悌抵挺提梯汀碇禎程締艇訂諦蹄逓邸鄭釘鼎泥摘擢敵滴的笛適鏑溺哲徹撤轍迭鉄典填天展店添纏甜貼転顛点伝殿澱田電兎吐堵塗妬屠徒斗杜渡登菟賭途都鍍砥砺努度土奴怒倒党冬凍刀唐塔塘套宕島嶋悼投搭東桃梼棟盗淘湯涛灯燈当痘祷等答筒糖統到董蕩藤討謄豆踏逃透鐙陶頭騰闘働動同堂導憧撞洞瞳童胴萄道銅峠鴇匿得徳涜特督禿篤毒独読栃橡凸突椴届鳶苫寅酉瀞噸屯惇敦沌豚遁頓呑曇鈍奈那内乍凪薙謎灘捺鍋楢馴縄畷南楠軟難汝二尼弐迩匂賑肉虹廿日乳入如尿韮任妊忍認濡禰祢寧葱猫熱年念捻撚燃粘乃廼之埜嚢悩濃納能脳膿農覗蚤巴把播覇杷波派琶破婆罵芭馬俳廃拝排敗杯盃牌背肺輩配倍培媒梅楳煤狽買売賠陪這蝿秤矧萩伯剥博拍柏泊白箔粕舶薄迫曝漠爆縛莫駁麦函箱硲箸肇筈櫨幡肌畑畠八鉢溌発醗髪伐罰抜筏閥鳩噺塙蛤隼伴判半反叛帆搬斑板氾汎版犯班畔繁般藩販範釆煩頒飯挽晩番盤磐蕃蛮匪卑否妃庇彼悲扉批披斐比泌疲皮碑秘緋罷肥被誹費避非飛樋簸備尾微枇毘琵眉美鼻柊稗匹疋髭彦膝菱肘弼必畢筆逼桧姫媛紐百謬俵彪標氷漂瓢票表評豹廟描病秒苗錨鋲蒜蛭鰭品彬斌浜瀕貧賓頻敏瓶不付埠夫婦富冨布府怖扶敷斧普浮父符腐膚芙譜負賦赴阜附侮撫武舞葡蕪部封楓風葺蕗伏副復幅服福腹複覆淵弗払沸仏物鮒分吻噴墳憤扮焚奮粉糞紛雰文聞丙併兵塀幣平弊柄並蔽閉陛米頁僻壁癖碧別瞥蔑箆偏変片篇編辺返遍便勉娩弁鞭保舗鋪圃捕歩甫補輔穂募墓慕戊暮母簿菩倣俸包呆報奉宝峰峯崩庖抱捧放方朋法泡烹砲縫胞芳萌蓬蜂褒訪豊邦鋒飽鳳鵬乏亡傍剖坊妨帽忘忙房暴望某棒冒紡肪膨謀貌貿鉾防吠頬北僕卜墨撲朴牧睦穆釦勃没殆堀幌奔本翻凡盆摩磨魔麻埋妹昧枚毎哩槙幕膜枕鮪柾鱒桝亦俣又抹末沫迄侭繭麿万慢満漫蔓味未魅巳箕岬密蜜湊蓑稔脈妙粍民眠務夢無牟矛霧鵡椋婿娘冥名命明盟迷銘鳴姪牝滅免棉綿緬面麺摸模茂妄孟毛猛盲網耗蒙儲木黙目杢勿餅尤戻籾貰問悶紋門匁也冶夜爺耶野弥矢厄役約薬訳躍靖柳薮鑓愉愈油癒諭輸唯佑優勇友宥幽悠憂揖有柚湧涌猶猷由祐裕誘遊邑郵雄融夕予余与誉輿預傭幼妖容庸揚揺擁曜楊様洋溶熔用窯羊耀葉蓉要謡踊遥陽養慾抑欲沃浴翌翼淀羅螺裸来莱頼雷洛絡落酪乱卵嵐欄濫藍蘭覧利吏履李梨理璃痢裏裡里離陸律率立葎掠略劉流溜琉留硫粒隆竜龍侶慮旅虜了亮僚両凌寮料梁涼猟療瞭稜糧良諒遼量陵領力緑倫厘林淋燐琳臨輪隣鱗麟瑠塁涙累類令伶例冷励嶺怜玲礼苓鈴隷零霊麗齢暦歴列劣烈裂廉恋憐漣煉簾練聯蓮連錬呂魯櫓炉賂路露労婁廊弄朗楼榔浪漏牢狼篭老聾蝋郎六麓禄肋録論倭和話歪賄脇惑枠鷲亙亘鰐詫藁蕨椀湾碗腕弌丐丕个丱丶丼丿乂乖乘亂亅豫亊舒弍于亞亟亠亢亰亳亶从仍仄仆仂仗仞仭仟价伉佚估佛佝佗佇佶侈侏侘佻佩佰侑佯來侖儘俔俟俎俘俛俑俚俐俤俥倚倨倔倪倥倅伜俶倡倩倬俾俯們倆偃假會偕偐偈做偖偬偸傀傚傅傴傲僉僊傳僂僖僞僥僭僣僮價僵儉儁儂儖儕儔儚儡儺儷儼儻儿兀兒兌兔兢竸兩兪兮冀冂囘册冉冏冑冓冕冖冤冦冢冩冪冫决冱冲冰况冽凅凉凛几處凩凭凰凵凾刄刋刔刎刧刪刮刳刹剏剄剋剌剞剔剪剴剩剳剿剽劍劔劒剱劈劑辨辧劬劭劼劵勁勍勗勞勣勦飭勠勳勵勸勹匆匈甸匍匐匏匕匚匣匯匱匳匸區卆卅丗卉卍凖卞卩卮夘卻卷厂厖厠厦厥厮厰厶參簒雙叟曼燮叮叨叭叺吁吽呀听吭吼吮吶吩吝呎咏呵咎呟呱呷呰咒呻咀呶咄咐咆哇咢咸咥咬哄哈咨咫哂咤咾咼哘哥哦唏唔哽哮哭哺哢唹啀啣啌售啜啅啖啗唸唳啝喙喀咯喊喟啻啾喘喞單啼喃喩喇喨嗚嗅嗟嗄嗜嗤嗔嘔嗷嘖嗾嗽嘛嗹噎噐營嘴嘶嘲嘸噫噤嘯噬噪嚆嚀嚊嚠嚔嚏嚥嚮嚶嚴囂嚼囁囃囀囈囎囑囓囗囮囹圀囿圄圉圈國圍圓團圖嗇圜圦圷圸坎圻址坏坩埀垈坡坿垉垓垠垳垤垪垰埃埆埔埒埓堊埖埣堋堙堝塲堡塢塋塰毀塒堽塹墅墹墟墫墺壞墻墸墮壅壓壑壗壙壘壥壜壤壟壯壺壹壻壼壽夂夊夐夛梦夥夬夭夲夸夾竒奕奐奎奚奘奢奠奧奬奩奸妁妝佞侫妣妲姆姨姜妍姙姚娥娟娑娜娉娚婀婬婉娵娶婢婪媚媼媾嫋嫂媽嫣嫗嫦嫩嫖嫺嫻嬌嬋嬖嬲嫐嬪嬶嬾孃孅孀孑孕孚孛孥孩孰孳孵學斈孺宀它宦宸寃寇寉寔寐寤實寢寞寥寫寰寶寳尅將專對尓尠尢尨尸尹屁屆屎屓屐屏孱屬屮乢屶屹岌岑岔妛岫岻岶岼岷峅岾峇峙峩峽峺峭嶌峪崋崕崗嵜崟崛崑崔崢崚崙崘嵌嵒嵎嵋嵬嵳嵶嶇嶄嶂嶢嶝嶬嶮嶽嶐嶷嶼巉巍巓巒巖巛巫已巵帋帚帙帑帛帶帷幄幃幀幎幗幔幟幢幤幇幵并幺麼广庠廁廂廈廐廏廖廣廝廚廛廢廡廨廩廬廱廳廰廴廸廾弃弉彝彜弋弑弖弩弭弸彁彈彌彎弯彑彖彗彙彡彭彳彷徃徂彿徊很徑徇從徙徘徠徨徭徼忖忻忤忸忱忝悳忿怡恠怙怐怩怎怱怛怕怫怦怏怺恚恁恪恷恟恊恆恍恣恃恤恂恬恫恙悁悍惧悃悚悄悛悖悗悒悧悋惡悸惠惓悴忰悽惆悵惘慍愕愆惶惷愀惴惺愃愡惻惱愍愎慇愾愨愧慊愿愼愬愴愽慂慄慳慷慘慙慚慫慴慯慥慱慟慝慓慵憙憖憇憬憔憚憊憑憫憮懌懊應懷懈懃懆憺懋罹懍懦懣懶懺懴懿懽懼懾戀戈戉戍戌戔戛戞戡截戮戰戲戳扁扎扞扣扛扠扨扼抂抉找抒抓抖拔抃抔拗拑抻拏拿拆擔拈拜拌拊拂拇抛拉挌拮拱挧挂挈拯拵捐挾捍搜捏掖掎掀掫捶掣掏掉掟掵捫捩掾揩揀揆揣揉插揶揄搖搴搆搓搦搶攝搗搨搏摧摯摶摎攪撕撓撥撩撈撼據擒擅擇撻擘擂擱擧舉擠擡抬擣擯攬擶擴擲擺攀擽攘攜攅攤攣攫攴攵攷收攸畋效敖敕敍敘敞敝敲數斂斃變斛斟斫斷旃旆旁旄旌旒旛旙无旡旱杲昊昃旻杳昵昶昴昜晏晄晉晁晞晝晤晧晨晟晢晰暃暈暎暉暄暘暝曁暹曉暾暼曄暸曖曚曠昿曦曩曰曵曷朏朖朞朦朧霸朮朿朶杁朸朷杆杞杠杙杣杤枉杰枩杼杪枌枋枦枡枅枷柯枴柬枳柩枸柤柞柝柢柮枹柎柆柧檜栞框栩桀桍栲桎梳栫桙档桷桿梟梏梭梔條梛梃檮梹桴梵梠梺椏梍桾椁棊椈棘椢椦棡椌棍棔棧棕椶椒椄棗棣椥棹棠棯椨椪椚椣椡棆楹楷楜楸楫楔楾楮椹楴椽楙椰楡楞楝榁楪榲榮槐榿槁槓榾槎寨槊槝榻槃榧樮榑榠榜榕榴槞槨樂樛槿權槹槲槧樅榱樞槭樔槫樊樒櫁樣樓橄樌橲樶橸橇橢橙橦橈樸樢檐檍檠檄檢檣檗蘗檻櫃櫂檸檳檬櫞櫑櫟檪櫚櫪櫻欅蘖櫺欒欖鬱欟欸欷盜欹飮歇歃歉歐歙歔歛歟歡歸歹歿殀殄殃殍殘殕殞殤殪殫殯殲殱殳殷殼毆毋毓毟毬毫毳毯麾氈氓气氛氤氣汞汕汢汪沂沍沚沁沛汾汨汳沒沐泄泱泓沽泗泅泝沮沱沾沺泛泯泙泪洟衍洶洫洽洸洙洵洳洒洌浣涓浤浚浹浙涎涕濤涅淹渕渊涵淇淦涸淆淬淞淌淨淒淅淺淙淤淕淪淮渭湮渮渙湲湟渾渣湫渫湶湍渟湃渺湎渤滿渝游溂溪溘滉溷滓溽溯滄溲滔滕溏溥滂溟潁漑灌滬滸滾漿滲漱滯漲滌漾漓滷澆潺潸澁澀潯潛濳潭澂潼潘澎澑濂潦澳澣澡澤澹濆澪濟濕濬濔濘濱濮濛瀉瀋濺瀑瀁瀏濾瀛瀚潴瀝瀘瀟瀰瀾瀲灑灣炙炒炯烱炬炸炳炮烟烋烝烙焉烽焜焙煥煕熈煦煢煌煖煬熏燻熄熕熨熬燗熹熾燒燉燔燎燠燬燧燵燼燹燿爍爐爛爨爭爬爰爲爻爼爿牀牆牋牘牴牾犂犁犇犒犖犢犧犹犲狃狆狄狎狒狢狠狡狹狷倏猗猊猜猖猝猴猯猩猥猾獎獏默獗獪獨獰獸獵獻獺珈玳珎玻珀珥珮珞璢琅瑯琥珸琲琺瑕琿瑟瑙瑁瑜瑩瑰瑣瑪瑶瑾璋璞璧瓊瓏瓔珱瓠瓣瓧瓩瓮瓲瓰瓱瓸瓷甄甃甅甌甎甍甕甓甞甦甬甼畄畍畊畉畛畆畚畩畤畧畫畭畸當疆疇畴疊疉疂疔疚疝疥疣痂疳痃疵疽疸疼疱痍痊痒痙痣痞痾痿痼瘁痰痺痲痳瘋瘍瘉瘟瘧瘠瘡瘢瘤瘴瘰瘻癇癈癆癜癘癡癢癨癩癪癧癬癰癲癶癸發皀皃皈皋皎皖皓皙皚皰皴皸皹皺盂盍盖盒盞盡盥盧盪蘯盻眈眇眄眩眤眞眥眦眛眷眸睇睚睨睫睛睥睿睾睹瞎瞋瞑瞠瞞瞰瞶瞹瞿瞼瞽瞻矇矍矗矚矜矣矮矼砌砒礦砠礪硅碎硴碆硼碚碌碣碵碪碯磑磆磋磔碾碼磅磊磬磧磚磽磴礇礒礑礙礬礫祀祠祗祟祚祕祓祺祿禊禝禧齋禪禮禳禹禺秉秕秧秬秡秣稈稍稘稙稠稟禀稱稻稾稷穃穗穉穡穢穩龝穰穹穽窈窗窕窘窖窩竈窰窶竅竄窿邃竇竊竍竏竕竓站竚竝竡竢竦竭竰笂笏笊笆笳笘笙笞笵笨笶筐筺笄筍笋筌筅筵筥筴筧筰筱筬筮箝箘箟箍箜箚箋箒箏筝箙篋篁篌篏箴篆篝篩簑簔篦篥籠簀簇簓篳篷簗簍篶簣簧簪簟簷簫簽籌籃籔籏籀籐籘籟籤籖籥籬籵粃粐粤粭粢粫粡粨粳粲粱粮粹粽糀糅糂糘糒糜糢鬻糯糲糴糶糺紆紂紜紕紊絅絋紮紲紿紵絆絳絖絎絲絨絮絏絣經綉絛綏絽綛綺綮綣綵緇綽綫總綢綯緜綸綟綰緘緝緤緞緻緲緡縅縊縣縡縒縱縟縉縋縢繆繦縻縵縹繃縷縲縺繧繝繖繞繙繚繹繪繩繼繻纃緕繽辮繿纈纉續纒纐纓纔纖纎纛纜缸缺罅罌罍罎罐网罕罔罘罟罠罨罩罧罸羂羆羃羈羇羌羔羞羝羚羣羯羲羹羮羶羸譱翅翆翊翕翔翡翦翩翳翹飜耆耄耋耒耘耙耜耡耨耿耻聊聆聒聘聚聟聢聨聳聲聰聶聹聽聿肄肆肅肛肓肚肭冐肬胛胥胙胝胄胚胖脉胯胱脛脩脣脯腋隋腆脾腓腑胼腱腮腥腦腴膃膈膊膀膂膠膕膤膣腟膓膩膰膵膾膸膽臀臂膺臉臍臑臙臘臈臚臟臠臧臺臻臾舁舂舅與舊舍舐舖舩舫舸舳艀艙艘艝艚艟艤艢艨艪艫舮艱艷艸艾芍芒芫芟芻芬苡苣苟苒苴苳苺莓范苻苹苞茆苜茉苙茵茴茖茲茱荀茹荐荅茯茫茗茘莅莚莪莟莢莖茣莎莇莊荼莵荳荵莠莉莨菴萓菫菎菽萃菘萋菁菷萇菠菲萍萢萠莽萸蔆菻葭萪萼蕚蒄葷葫蒭葮蒂葩葆萬葯葹萵蓊葢蒹蒿蒟蓙蓍蒻蓚蓐蓁蓆蓖蒡蔡蓿蓴蔗蔘蔬蔟蔕蔔蓼蕀蕣蕘蕈蕁蘂蕋蕕薀薤薈薑薊薨蕭薔薛藪薇薜蕷蕾薐藉薺藏薹藐藕藝藥藜藹蘊蘓蘋藾藺蘆蘢蘚蘰蘿虍乕虔號虧虱蚓蚣蚩蚪蚋蚌蚶蚯蛄蛆蚰蛉蠣蚫蛔蛞蛩蛬蛟蛛蛯蜒蜆蜈蜀蜃蛻蜑蜉蜍蛹蜊蜴蜿蜷蜻蜥蜩蜚蝠蝟蝸蝌蝎蝴蝗蝨蝮蝙蝓蝣蝪蠅螢螟螂螯蟋螽蟀蟐雖螫蟄螳蟇蟆螻蟯蟲蟠蠏蠍蟾蟶蟷蠎蟒蠑蠖蠕蠢蠡蠱蠶蠹蠧蠻衄衂衒衙衞衢衫袁衾袞衵衽袵衲袂袗袒袮袙袢袍袤袰袿袱裃裄裔裘裙裝裹褂裼裴裨裲褄褌褊褓襃褞褥褪褫襁襄褻褶褸襌褝襠襞襦襤襭襪襯襴襷襾覃覈覊覓覘覡覩覦覬覯覲覺覽覿觀觚觜觝觧觴觸訃訖訐訌訛訝訥訶詁詛詒詆詈詼詭詬詢誅誂誄誨誡誑誥誦誚誣諄諍諂諚諫諳諧諤諱謔諠諢諷諞諛謌謇謚諡謖謐謗謠謳鞫謦謫謾謨譁譌譏譎證譖譛譚譫譟譬譯譴譽讀讌讎讒讓讖讙讚谺豁谿豈豌豎豐豕豢豬豸豺貂貉貅貊貍貎貔豼貘戝貭貪貽貲貳貮貶賈賁賤賣賚賽賺賻贄贅贊贇贏贍贐齎贓賍贔贖赧赭赱赳趁趙跂趾趺跏跚跖跌跛跋跪跫跟跣跼踈踉跿踝踞踐踟蹂踵踰踴蹊蹇蹉蹌蹐蹈蹙蹤蹠踪蹣蹕蹶蹲蹼躁躇躅躄躋躊躓躑躔躙躪躡躬躰軆躱躾軅軈軋軛軣軼軻軫軾輊輅輕輒輙輓輜輟輛輌輦輳輻輹轅轂輾轌轉轆轎轗轜轢轣轤辜辟辣辭辯辷迚迥迢迪迯邇迴逅迹迺逑逕逡逍逞逖逋逧逶逵逹迸遏遐遑遒逎遉逾遖遘遞遨遯遶隨遲邂遽邁邀邊邉邏邨邯邱邵郢郤扈郛鄂鄒鄙鄲鄰酊酖酘酣酥酩酳酲醋醉醂醢醫醯醪醵醴醺釀釁釉釋釐釖釟釡釛釼釵釶鈞釿鈔鈬鈕鈑鉞鉗鉅鉉鉤鉈銕鈿鉋鉐銜銖銓銛鉚鋏銹銷鋩錏鋺鍄錮錙錢錚錣錺錵錻鍜鍠鍼鍮鍖鎰鎬鎭鎔鎹鏖鏗鏨鏥鏘鏃鏝鏐鏈鏤鐚鐔鐓鐃鐇鐐鐶鐫鐵鐡鐺鑁鑒鑄鑛鑠鑢鑞鑪鈩鑰鑵鑷鑽鑚鑼鑾钁鑿閂閇閊閔閖閘閙閠閨閧閭閼閻閹閾闊濶闃闍闌闕闔闖關闡闥闢阡阨阮阯陂陌陏陋陷陜陞陝陟陦陲陬隍隘隕隗險隧隱隲隰隴隶隸隹雎雋雉雍襍雜霍雕雹霄霆霈霓霎霑霏霖霙霤霪霰霹霽霾靄靆靈靂靉靜靠靤靦靨勒靫靱靹鞅靼鞁靺鞆鞋鞏鞐鞜鞨鞦鞣鞳鞴韃韆韈韋韜韭齏韲竟韶韵頏頌頸頤頡頷頽顆顏顋顫顯顰顱顴顳颪颯颱颶飄飃飆飩飫餃餉餒餔餘餡餝餞餤餠餬餮餽餾饂饉饅饐饋饑饒饌饕馗馘馥馭馮馼駟駛駝駘駑駭駮駱駲駻駸騁騏騅駢騙騫騷驅驂驀驃騾驕驍驛驗驟驢驥驤驩驫驪骭骰骼髀髏髑髓體髞髟髢髣髦髯髫髮髴髱髷髻鬆鬘鬚鬟鬢鬣鬥鬧鬨鬩鬪鬮鬯鬲魄魃魏魍魎魑魘魴鮓鮃鮑鮖鮗鮟鮠鮨鮴鯀鯊鮹鯆鯏鯑鯒鯣鯢鯤鯔鯡鰺鯲鯱鯰鰕鰔鰉鰓鰌鰆鰈鰒鰊鰄鰮鰛鰥鰤鰡鰰鱇鰲鱆鰾鱚鱠鱧鱶鱸鳧鳬鳰鴉鴈鳫鴃鴆鴪鴦鶯鴣鴟鵄鴕鴒鵁鴿鴾鵆鵈鵝鵞鵤鵑鵐鵙鵲鶉鶇鶫鵯鵺鶚鶤鶩鶲鷄鷁鶻鶸鶺鷆鷏鷂鷙鷓鷸鷦鷭鷯鷽鸚鸛鸞鹵鹹鹽麁麈麋麌麒麕麑麝麥麩麸麪麭靡黌黎黏黐黔黜點黝黠黥黨黯黴黶黷黹黻黼黽鼇鼈皷鼕鼡鼬鼾齊齒齔齣齟齠齡齦齧齬齪齷齲齶龕龜龠堯槇遙瑤凜熙"

bot.gguide = """思惟奈ちゃんのグローバルチャット利用規約 最終更新 2019/05/27

1.思惟奈ちゃんグローバルチャット(以下「グローバルチャット」とする)のプロファイルを作成した時点で、この規約に同意したものとする。
2.規約違反者は
  一回目:警告
  二回目:一週間使用禁止
  三回目:永久使用禁止
  を原則とする。使用禁止中に、サブアカウントなどでの禁止回避は判明し次第、メインアカウント、サブアカウントともに永久使用禁止とする。
3.グローバルチャットに、以下のようなテキスト、画像、そのようなコンテンツにつながるURLを投稿することを禁止する。ただし、グローバルチャット作成者、およびグローバルモデレーターは、管理運営に必要な場合は、投稿してもよいとする。
  ・年齢制限の必要なもの
  ・閲覧に金銭や個人情報が必要なもの(ただし、これによって投稿などにログインが必要なサイトのリンク投稿を制限するものではない)
  ・Discordのサーバー招待。ただし新機能のテストのために、「思惟奈ちゃん更新関係サーバー」に誘導する場合など、一部の例外を除く。これによって他のグローバルチャットのグローバルチャンネル名の送信を禁止するものではない。
  ・意味のない文字列の羅列。ただし、接続テストの場合を除く。
  ・その他法律、Discord利用規約に違反するもの
4.グローバルチャット製作者および、グローバルモデレーターは、利用者のできることに加えて、次の行為を行うことができる。
  ・role(肩書)の変更
  (本人からの依頼などの場合。ただし、一部文字列はなりすまし防止のために却下される。)
  ・利用者の使用禁止状態の切り替え
  ・投稿の削除
  上二つの行為を行うのは、前項の項目にある投稿が行われた場合や、製作者、グローバルモデレーターの話し合いの結果、不適切だと判断されたものの場合に限る
5.グローバルチャットにて、ほかのサーバーに送信される項目は、以下のとおりである。
  ・(メッセージの場合)メッセージ内容、付属するembed、添付された画像(ただし一枚のみ)
  ・(リアクションの場合)つけた/外したリアクション
  ・ユーザーのid、投稿時にオフラインでないデバイス(PC,moblie,webの三通り)
  ・送信したサーバーの名前、アイコン、id
  ・送信先のメッセージid一覧
  ・投稿時間
6.この規約は`s-globalguide`でいつでも見ることができる。
7.改定
  ・制作者が予告なしに改定することがある。改定後は、グローバルチャットにて報告される。
  ・予告して改定した場合も、同じように改定後に報告する。
"""

bot.load_extension("cogs.apple_misc")
bot.load_extension("cogs.apple_onlinenotif")


@tasks.loop(minutes=1.0)
async def cRPC():
    global rpcct
    if rpcct == 7:
        rpcct = 0
    else:
        rpcct = rpcct+1
    await bot.change_presence(status=discord.Status.online, activity=discord.Game(name=rpcs[rpcct].format(len(bot.guilds), len(bot.users))))


async def repomsg(msg, rs, should_ban=False):
    ch = bot.get_channel(628929788421210144)
    e = discord.Embed(title="グローバルメッセージブロック履歴",
                      description=f"メッセージ内容:{msg.clean_content}", color=bot.ec)
    e.set_author(name=f"{msg.author}(id:{msg.author.id})",
                 icon_url=msg.author.avatar_url_as(static_format="png"))
    e.set_footer(text=f"サーバー:{msg.guild.name}(id:{msg.guild.id})",
                 icon_url=msg.guild.icon_url_as(static_format="png"))
    e.timestamp = msg.created_at
    e.add_field(name="ブロック理由", value=rs or "なし")
    await ch.send(embed=e)
    if should_ban:
        bot.cursor.execute(
            "UPDATE users SET gban = ? WHERE id = ?", (1, msg.author.id))
        bot.cursor.execute("UPDATE users SET gbanhist = ? WHERE id = ?",
                           ("予防グローバルチャットBAN: {}".format(rs), msg.author.id))


async def gsended(message, ch, embed):
    try:
        tmp = await ch.send(embed=embed)

        if not message.embeds[0] is None:
            await ch.send(embed=message.embeds[0])
        return tmp.id
    except:
        pass


async def gsendwh(message, wch, spicon, pf, ed, fls):
    try:
        for wh in await wch.webhooks():
            if wh.name == "sina_global":
                if not fls == []:
                    sdfl = []
                    for at in fls:
                        sdfl.append(discord.File(
                            f"globalsends/{at.filename}", filename=at.filename, spoiler=at.is_spoiler()))
                    tmp = await wh.send(content=message.clean_content, wait=True, username=f"[{spicon}]{pf['gnick']}", avatar_url=message.author.avatar_url_as(static_format='png'), embeds=ed, files=sdfl)
                else:
                    tmp = await wh.send(content=message.clean_content, wait=True, username=f"[{spicon}]{pf['gnick']}", avatar_url=message.author.avatar_url_as(static_format='png'), embeds=ed)
                return tmp.id
    except:
        pass


async def globalSend(message):
    try:
        if message.content.startswith("//"):
            return
        if message.author.id == bot.user.id:
            return
        if message.is_system():
            return
        bot.cursor.execute("select * from globalchs")
        gchs = bot.cursor.fetchall()
        gchn = None
        for sgch in gchs:
            if message.channel.id in sgch["ids"]:
                gchn = sgch["name"]
                gchs = sgch["ids"]
                break
        if gchn is None:
            return

        try:
            content_checker(bot, message)
        except MaliciousInput as err:
            await repomsg(message, err.reason, err.should_ban)
            return

        bot.cursor.execute("select * from users where id=?",
                           (message.author.id,))
        upf = bot.cursor.fetchone()
        if (datetime.datetime.now() - rdelta(hours=9) - rdelta(days=7) >= message.author.created_at) or upf["gmod"] or upf["gstar"]:
            if upf["gban"] == 1:
                dc = await ut.opendm(message.author)
                await dc.send(bot._(message.author, "global-banned", message.author.mention))
                await repomsg(message, "思惟奈ちゃんグローバルチャットの使用禁止")
                await message.add_reaction("❌")
                await asyncio.sleep(5)
                await message.remove_reaction("❌", bot.user)
            else:
                try:
                    if upf["sinapartner"] and message.author.activity:
                        if message.author.activity.type == discord.ActivityType.playing:
                            ne = discord.Embed(
                                title="", description=f"{message.author.activity.name}をプレイしています。", color=upf["gcolor"])
                        elif message.author.activity.type == discord.ActivityType.watching:
                            ne = discord.Embed(
                                title="", description=f"{message.author.activity.name}を視聴しています。", color=upf["gcolor"])
                        elif message.author.activity.type == discord.ActivityType.listening:
                            if message.author.activity.name == "Spotify":
                                ne = discord.Embed(
                                    title="", description=f"Spotifyで[{message.author.activity.title}](https://open.spotify.com/track/{message.author.activity.track_id})を聞いています。", color=upf["gcolor"])
                            else:
                                ne = discord.Embed(
                                    title="", description=f"{message.author.activity.name}を聞いています。", color=upf["gcolor"])
                        elif message.author.activity.type == discord.ActivityType.streaming:
                            ne = discord.Embed(
                                title="", description=f"{message.author.activity.name}を配信しています。", color=upf["gcolor"])
                        elif message.author.activity.type == discord.ActivityType.custom:
                            ne = discord.Embed(
                                title="", description=f"{message.author.activity.name}", color=upf["gcolor"])
                        else:
                            ne = discord.Embed(
                                title="", description="", color=upf["gcolor"])
                    else:
                        ne = discord.Embed(
                            title="", description="", color=upf["gcolor"])
                    ne.set_author(
                        name=f"{ut.ondevicon(message.author)},ユーザーのID:{str(message.author.id)}")
                    if message.guild.id in [i[0] for i in bot.partnerg]:
                        ne.set_footer(text=f"🔗(思惟奈ちゃんパートナーサーバー):{message.guild.name}(id:{message.guild.id}),{[i[2] for i in bot.partnerg if i[0]==message.guild.id][0]}", icon_url=message.guild.icon_url_as(
                            static_format="png"))
                    else:
                        ne.set_footer(text=f"{message.guild.name}(id:{message.guild.id})",
                                      icon_url=message.guild.icon_url_as(static_format="png"))
                    ne.timestamp = datetime.datetime.now() - rdelta(hours=9)
                    embed = discord.Embed(
                        title="本文", description=message.content, color=upf["gcolor"])
                    embed.set_footer(text=f"{message.guild.name}(id:{message.guild.id})",
                                     icon_url=message.guild.icon_url_as(static_format="png"))
                    if message.application is not None:
                        embed.add_field(
                            name=message.application["name"]+"へのRPC招待", value="RPC招待はグローバル送信できません。")

                    spicon = ""

                    if message.author.id == 404243934210949120:  # みぃてん☆
                        spicon = spicon + "🌈"
                    if message.author.id == 539787492711464960:  # きゃらちゃんさん
                        spicon = spicon + "❤"
                    if message.author.id in bot.team_sina:  # チーム☆思惟奈ちゃん
                        spicon = spicon + "🌠"
                    if message.author.bot:
                        spicon = spicon + "⚙"
                    if upf["sinapartner"]:
                        spicon = spicon + "💠"  # 認証済みアカウント
                    if message.author.id in [i[1] for i in bot.partnerg]:
                        spicon = spicon + "🔗"
                    if upf["gmod"]:
                        spicon = spicon + "🔧"
                    if upf["galpha"]:
                        spicon = spicon + "🔔"
                    if upf["gstar"]:
                        spicon = spicon + "🌟"
                    if spicon == "":
                        spicon = "👤"

                    embed.set_author(name=f"{upf['gnick']}({spicon}):{str(message.author.id)}",
                                     icon_url=message.author.avatar_url_as(static_format="png"))
                    if not message.attachments == []:
                        embed.set_image(url=message.attachments[0].url)
                        for atc in message.attachments:
                            temp = f"{atc.url}\n"
                        embed.add_field(name="添付ファイルのURL一覧", value=temp)
                except:
                    traceback.print_exc(0)
                    await message.add_reaction("❌")
                    await asyncio.sleep(5)
                    await message.remove_reaction("❌", bot.user)
                    return
                try:
                    await message.add_reaction(bot.get_emoji(653161518346534912))
                except:
                    pass
            if gchn.startswith("ed-"):
                tasks = []
                for cid in gchs:
                    ch = bot.get_channel(cid)
                    tasks.append(asyncio.ensure_future(
                        gsended(message, ch, embed)))
                bot.cursor.execute(
                    "select * from globalchs where name=?", (gchn.replace("ed-", ""),))
                nch = bot.cursor.fetchone()
                try:
                    if nch["ids"]:
                        for cid in nch["ids"]:
                            try:
                                if not cid == message.channel.id:
                                    wch = bot.get_channel(cid)
                                    tasks.append(asyncio.ensure_future(
                                        gsendwh(message, wch, spicon, upf, ne, [])))
                            except:
                                pass
                    if message.attachments == []:
                        await message.delete()
                except:
                    pass
                mids = await asyncio.gather(*tasks)
                try:
                    await message.remove_reaction(bot.get_emoji(653161518346534912), bot.user)
                except:
                    pass
            else:
                try:
                    sfs = False
                    fls = []
                    ed = []
                    if not message.attachments == []:
                        os.makedirs('globalsends/', exist_ok=True)
                        for at in message.attachments:
                            await at.save(f"globalsends/{at.filename}")
                            fls.append(at)
                        ed = ed + message.embeds + [ne]
                    else:
                        ed = ed + message.embeds + [ne]
                except:
                    traceback.print_exc(0)
                    await message.add_reaction("❌")
                    await asyncio.sleep(5)
                    await message.remove_reaction("❌", bot.user)
                    return
                try:
                    await message.add_reaction(bot.get_emoji(653161518346534912))
                except:
                    pass
                tasks = []
                for cid in gchs:
                    try:
                        if not cid == message.channel.id:
                            wch = bot.get_channel(cid)
                            tasks.append(asyncio.ensure_future(
                                gsendwh(message, wch, spicon, upf, ed, fls)))
                    except:
                        pass
                bot.cursor.execute(
                    "select * from globalchs where name=?", (f"ed-{gchn}",))
                och = bot.cursor.fetchone()
                try:
                    if nch["ids"]:
                        for cid in och["ids"]:
                            ch = bot.get_channel(cid)
                            tasks.append(asyncio.ensure_future(
                                gsended(message, ch, embed)))
                except:
                    pass
                mids = await asyncio.gather(*tasks)
                if not fls == []:
                    shutil.rmtree("globalsends/")
                try:
                    await message.remove_reaction(bot.get_emoji(653161518346534912), bot.user)
                except:
                    pass
            bot.cursor.execute("INSERT INTO globaldates(id,content,allid,aid,gid,timestamp) VALUES(?,?,?,?,?,?)", (int(time.time())+random.randint(1, 30), message.clean_content,
                                                                                                                   mids+[message.id], message.author.id, message.guild.id, str(message.created_at.strftime('%Y{0}%m{1}%d{2} %H{3}%M{4}%S{5}').format(*'年月日時分秒'))))
            await message.add_reaction(bot.get_emoji(653161518195539975))
            await asyncio.sleep(5)
            await message.remove_reaction(bot.get_emoji(653161518195539975), bot.user)
        else:
            await repomsg(message, "作成後7日に満たないアカウント")
    except Exception as e:
        traceback.print_exc()


@bot.event
async def on_member_update(b, a):
    global Donotif
    # serverlog
    try:
        e = discord.Embed(
            title="メンバーの更新", description=f"変更メンバー:{str(a)}", color=bot.ec)
        e.timestamp = datetime.datetime.now() - rdelta(hours=9)
        if not b.nick == a.nick:
            e.add_field(name="変更内容", value="ニックネーム")
            if b.nick:
                bnick = b.nick
            else:
                bnick = b.name
            if a.nick:
                anick = a.nick
            else:
                anick = a.name
            e.add_field(name="変更前", value=bnick.replace("\\", "\\\\").replace("*", "\*").replace(
                "_", "\_").replace("|", "\|").replace("~", "\~").replace("`", "\`").replace(">", "\>"))
            e.add_field(name="変更後", value=anick.replace("\\", "\\\\").replace("*", "\*").replace(
                "_", "\_").replace("|", "\|").replace("~", "\~").replace("`", "\`").replace(">", "\>"))
            bot.cursor.execute(
                "select * from guilds where id=?", (a.guild.id,))
            gpf = bot.cursor.fetchone()
            if gpf["sendlog"]:
                ch = bot.get_channel(gpf["sendlog"])
                if ch.guild.id == a.guild.id:
                    await ch.send(embed=e)
        elif not b.roles == a.roles:
            if len(b.roles) > len(a.roles):
                e.add_field(name="変更内容", value="役職除去")
                e.add_field(name="役職", value=list(
                    set(b.roles)-set(a.roles))[0])
            else:
                e.add_field(name="変更内容", value="役職付与")
                e.add_field(name="役職", value=list(
                    set(a.roles)-set(b.roles))[0])
            bot.cursor.execute(
                "select * from guilds where id=?", (a.guild.id,))
            gpf = bot.cursor.fetchone()
            if gpf["sendlog"]:
                ch = bot.get_channel(gpf["sendlog"])
                if ch.guild.id == a.guild.id:
                    await ch.send(embed=e)
    except:
        pass
    # online notif are now handled in apple_onlinenotif


async def nga(m, r):
    ch = m.guild.get_channel(631875590307446814)

    admins = m.guild.get_role(574494236951707668)
    tmpadmins = m.guild.get_role(583952666317684756)
    subadmins = m.guild.get_role(579283058394660864)
    giverole = m.guild.get_role(620911942889897984)
    tch = await ch.create_text_channel(f"認証待ち-{m.name}", overwrites={
        m: discord.PermissionOverwrite(read_messages=True, send_messages=True),
        m.guild.default_role: discord.PermissionOverwrite(read_messages=False),
        admins: discord.PermissionOverwrite(read_messages=True, send_messages=True),
        tmpadmins: discord.PermissionOverwrite(read_messages=True, send_messages=True),
        subadmins: discord.PermissionOverwrite(read_messages=True, send_messages=True),
        giverole: discord.PermissionOverwrite(
            read_messages=True, send_messages=True)
    }, topic=str(m.id))
    await tch.send(f"""{m.mention}さん！みぃてん☆のわいがや広場にようこそ！
あなたは{r}が理由で、思惟奈ちゃんによる自動認証が行われませんでした。
思惟奈ちゃんに関するお問い合わせ等の方は`思惟奈ちゃん`カテゴリー内のチャンネルをご利用ください。
不明点等ございましたら、このチャンネルをご利用ください。

その他のチャンネルを使う際には、メンバー役職が必要です。
まずはルールを確認してください!
<#574500456471199746> このチャンネルにルールがあります。
その後、そのことを報告してください。
みぃてん☆
    """)


@bot.event
async def on_member_join(member):
    if member.guild.id == 574170788165582849:
        if member.bot:
            await member.add_roles(member.guild.get_role(574494559946539009))
        else:
            uich = bot.get_channel(633651383353999370)

            e = discord.Embed(title=f"参加メンバー{member}について", color=bot.ec)
            e.add_field(name="共通サーバー数", value=len(
                [g for g in bot.guilds if g.get_member(member.id)]))
            e.add_field(name="ID", value=member.id)
            e.set_footer(text="アカウント作成タイムスタンプ")
            e.timestamp = member.created_at
            await uich.send(embed=e)
            mrole = member.guild.get_role(574494088837988352)

            bunotif = 0
            if len([g for g in bot.guilds if g.get_member(member.id)]) == 1:
                await nga(member, "思惟奈ちゃんとの共通のサーバーがほかにないこと")
            else:
                for g in bot.guilds:

                    try:
                        tmp = await g.bans()
                    except:
                        continue
                    banulist = [i.user.id for i in tmp]
                    if member.id in banulist:
                        bunotif = bunotif + 1
                if bunotif != 0:
                    await nga(member, "思惟奈ちゃんとの共通のほかサーバーでのban")
                    pass
                else:
                    if datetime.datetime.now() - rdelta(hours=9) - rdelta(days=4) < member.created_at:
                        await nga(member, "アカウントの作成から4日経過していないこと")
                        pass
                    else:
                        await nga(member, "本来認証していますが、現在は認証止めていること")
                        '''await member.add_roles(mrole)
                        ch = await ut.opendm(member)
                        try:
                            await ch.send(f"""{member.mention}さん！みぃてん☆のわいがや広場にようこそ！
    思惟奈ちゃん関連の用事の方は`思惟奈ちゃん`カテゴリー内のチャンネルをご利用ください。
    また、あなたは、いくつかの条件を満たしているため、自動的にメンバー役職が付与されましたので、サーバーで、ゆっくり過ごされてください。
    ですが、使用前にまずはルールを確認してください!
    https://gist.github.com/apple502j/1a81b1a95253609f0c67ecb74f38754b
    また、必要に応じて通知設定を「すべてのメッセージ」などに変更してください。(デフォルトは「@メンションのみ」です。)
                            """)
                        except:
                            ch = member.guild.get_channel(574494906287128577)
                            await ch.send(f"""{member.mention}さん！みぃてん☆のわいがや広場にようこそ！
    思惟奈ちゃん関連の用事の方は`思惟奈ちゃん`カテゴリー内のチャンネルをご利用ください。
    また、あなたは、いくつかの条件を満たしているため、自動的にメンバー役職が付与されましたので、サーバーで、ゆっくり過ごされてください。
    ですが、使用前にまずはルールを確認してください!
    https://gist.github.com/apple502j/1a81b1a95253609f0c67ecb74f38754b
    また、必要に応じて通知設定を「すべてのメッセージ」などに変更してください。(デフォルトは「@メンションのみ」です。)
                            """)
                        schs=[631815290044284938,574494906287128577]
                        for c in schs:

                            sch = bot.get_channel(c)
                            await sch.send(embed=ut.getEmbed("自動認証完了のお知らせ",f"{member.mention}さんが自動認証を済ませました。"))'''
    else:
        try:
            bot.cursor.execute(
                "select * from guilds where id=?", (member.guild.id,))
            gpf = bot.cursor.fetchone()
            ctt = gpf["jltasks"]
            if not ctt.get("welcome") is None:
                if ctt["welcome"]["sendto"] == "sysch":
                    await member.guild.system_channel.send(ctt["welcome"]["content"].format(member.mention))
                else:
                    dc = await ut.opendm(member)
                    await dc.send(ctt["welcome"]["content"].format(member.mention))
        except:
            pass
    e = discord.Embed(
        title="メンバーの参加", description=f"{len(member.guild.members)}人目のメンバー", color=bot.ec)
    e.add_field(name="参加メンバー", value=member.mention)
    e.add_field(name="そのユーザーのid", value=member.id)
    e.set_footer(
        text=f"アカウント作成日時(そのままの値:{(member.created_at + rdelta(hours=9)).strftime('%Y{0}%m{1}%d{2} %H{3}%M{4}%S{5}').format(*'年月日時分秒')},タイムスタンプ化:")
    e.timestamp = member.created_at
    bot.cursor.execute("select * from guilds where id=?", (member.guild.id,))
    gpf = bot.cursor.fetchone()
    try:
        if gpf["sendlog"]:
            ch = bot.get_channel(gpf["sendlog"])
            if ch.guild.id == member.guild.id:
                await ch.send(embed=e)
    except:
        pass
    # 他サーバーでのban通知
    isgban = False
    bot.cursor.execute("select * from users where id=?", (member.id,))
    upf = bot.cursor.fetchone()
    bunotif = 0
    if member.id in bot.team_sina:
        for ch in member.guild.channels:
            if ch.name == "sina-user-check":
                await ch.send(embed=discord.Embed(title=f"{member}の安全性評価", description=f"そのユーザーは、チーム☆思惟奈ちゃんのメンバーです。"))
    elif upf and upf["gban"] == 1:
        for ch in member.guild.channels:
            if ch.name == "sina-user-check":
                await ch.send(embed=discord.Embed(title=f"{member}の安全性評価", description=f"そのユーザーは、思惟奈ちゃんグローバルチャットbanを受けています。\n何らかの事情があってこうなっていますので十分に注意してください。"))
    else:
        for g in bot.guilds:

            try:
                tmp = await g.bans()
            except:
                continue
            banulist = [i.user.id for i in tmp]
            if member.id in banulist:
                bunotif = bunotif + 1
        if bunotif == 0:
            for ch in member.guild.channels:
                if ch.name == "sina-user-check":
                    await ch.send(embed=discord.Embed(title=f"{member}の安全性評価", description=f"そのユーザーは、思惟奈ちゃんのいるサーバーでは、banされていません。"))
        else:
            for ch in member.guild.channels:
                if ch.name == "sina-user-check":
                    await ch.send(embed=discord.Embed(title=f"{member}の安全性評価", description=f"そのユーザーは、思惟奈ちゃんのいる{bunotif}のサーバーでbanされています。注意してください。"))


@bot.event
async def on_member_remove(member):
    if member.guild.id == 574170788165582849:
        await member.guild.system_channel.send(f"{str(member)}さんがこのサーバーを退出しました。")
    else:
        try:
            bot.cursor.execute(
                "select * from guilds where id=?", (member.guild.id,))
            gpf = bot.cursor.fetchone()
            ctt = gpf["jltasks"]
            if not ctt.get("cu") is None:
                if ctt["cu"]["sendto"] == "sysch":
                    await member.guild.system_channel.send(ctt["cu"]["content"].format(str(member)))
                else:
                    dc = await ut.opendm(member)
                    await dc.send(ctt["cu"]["content"].format(str(member)))
        except:
            pass
    e = discord.Embed(title="メンバーの退出", color=bot.ec)
    e.add_field(name="退出メンバー", value=str(member))
    e.add_field(name="役職", value=[i.name for i in member.roles])
    # e.set_footer(text=f"{member.guild.name}/{member.guild.id}")
    e.timestamp = datetime.datetime.now() - rdelta(hours=9)
    bot.cursor.execute("select * from guilds where id=?", (member.guild.id,))
    gpf = bot.cursor.fetchone()
    if gpf["sendlog"]:
        ch = bot.get_channel(gpf["sendlog"])
        if ch.guild.id == member.guild.id:
            await ch.send(embed=e)
    """if member.guild.id == 611445741902364672:
        c = bot.get_channel(613629308166209549)
        await c.send(embed=e)"""


@bot.event
async def on_webhooks_update(channel):
    e = discord.Embed(title="Webhooksの更新", color=bot.ec)
    e.add_field(name="チャンネル", value=channel.mention)
    e.timestamp = datetime.datetime.now() - rdelta(hours=9)
    bot.cursor.execute("select * from guilds where id=?", (channel.guild.id,))
    gpf = bot.cursor.fetchone()
    if gpf["sendlog"]:
        ch = bot.get_channel(gpf["sendlog"])
        if ch.guild.id == channel.guild.id:
            await ch.send(embed=e)


@bot.event
async def on_guild_role_create(role):
    e = discord.Embed(title="役職の作成", color=bot.ec)
    e.add_field(name="役職名", value=role.name)
    e.timestamp = datetime.datetime.now() - rdelta(hours=9)
    bot.cursor.execute("select * from guilds where id=?", (role.guild.id,))
    gpf = bot.cursor.fetchone()
    if gpf["sendlog"]:
        ch = bot.get_channel(gpf["sendlog"])
        if ch.guild.id == role.guild.id:
            await ch.send(embed=e)


@bot.event
async def on_guild_role_delete(role):
    e = discord.Embed(title="役職の削除", color=bot.ec)
    e.add_field(name="役職名", value=role.name)
    e.timestamp = datetime.datetime.now() - rdelta(hours=9)
    bot.cursor.execute("select * from guilds where id=?", (role.guild.id,))
    gpf = bot.cursor.fetchone()
    if gpf["sendlog"]:
        ch = bot.get_channel(gpf["sendlog"])
        if ch.guild.id == role.guild.id:
            await ch.send(embed=e)


@bot.event
async def on_message_edit(before, after):
    if after.channel.id == 611117238464020490:
        if after.embeds and before.content == after.content:
            bot.cursor.execute(
                "select * from globalchs where name=?", ("防災情報",))
            chs = bot.cursor.fetchone()
            es = after.embeds
            sed = []
            for e in es:
                e.color = bot.ec
                e.title = f'💠{str(e.title).replace("Embed.Empty","防災情報")}'
                sed.append(e)
            for chid in chs["ids"]:
                try:
                    ch = bot.get_channel(chid)
                    for wh in await ch.webhooks():
                        try:
                            if wh.name == "sina_global":
                                await wh.send(embeds=sed)
                                await asyncio.sleep(0.2)
                                break
                        except:
                            continue
                except:
                    pass
    if not after.author.bot:
        if before.content != after.content:
            e = discord.Embed(title="メッセージの編集", color=bot.ec)
            e.add_field(name="編集前", value=before.content)
            e.add_field(name="編集後", value=after.content)
            e.add_field(name="メッセージ送信者", value=after.author.mention)
            e.add_field(name="メッセージチャンネル", value=after.channel.mention)
            e.add_field(name="メッセージのURL", value=after.jump_url)
            e.timestamp = datetime.datetime.now() - rdelta(hours=9)
            bot.cursor.execute(
                "select * from guilds where id=?", (after.guild.id,))
            gpf = bot.cursor.fetchone()
            if gpf["sendlog"]:
                ch = bot.get_channel(gpf["sendlog"])
                if ch.guild.id == after.guild.id:
                    await ch.send(embed=e)


@bot.event
async def on_guild_channel_delete(channel):
    bl = await channel.guild.audit_logs(limit=1, action=discord.AuditLogAction.channel_delete).flatten()
    e = discord.Embed(title="チャンネル削除", color=bot.ec)
    e.add_field(name="チャンネル名", value=channel.name)
    e.timestamp = datetime.datetime.now() - rdelta(hours=9)
    bot.cursor.execute("select * from guilds where id=?", (channel.guild.id,))
    gpf = bot.cursor.fetchone()
    if gpf["sendlog"]:
        ch = bot.get_channel(gpf["sendlog"])
        if ch.guild.id == channel.guild.id:
            await ch.send(embed=e)


@bot.event
async def on_reaction_clear(message, reactions):
    e = discord.Embed(title="リアクションの一斉除去", color=bot.ec)
    e.add_field(name="リアクション", value=[str(i) for i in reactions])
    e.add_field(name="除去されたメッセージ", value=message.content or "(本文なし)")
    e.timestamp = datetime.datetime.now() - rdelta(hours=9)
    bot.cursor.execute("select * from guilds where id=?", (message.guild.id,))
    gpf = bot.cursor.fetchone()
    if gpf["sendlog"]:
        ch = bot.get_channel(gpf["sendlog"])
        if ch.guild.id == message.guild.id:
            await ch.send(embed=e)


@bot.event
async def on_message_delete(message):
    if not message.author.bot:
        e = discord.Embed(title="メッセージ削除", color=bot.ec)
        e.add_field(name="メッセージ", value=message.content)
        e.add_field(name="メッセージ送信者", value=message.author.mention)
        e.add_field(name="メッセージチャンネル", value=message.channel.mention)
        e.add_field(name="メッセージのid", value=message.id)
        e.timestamp = datetime.datetime.now() - rdelta(hours=9)
        bot.cursor.execute("select * from guilds where id=?",
                           (message.guild.id,))
        gpf = bot.cursor.fetchone()
        if gpf["sendlog"]:
            ch = bot.get_channel(gpf["sendlog"])
            if ch.guild.id == message.guild.id:
                await ch.send(embed=e)


@bot.event
async def on_bulk_message_delete(messages):
    e = discord.Embed(title="メッセージ一括削除", color=bot.ec)
    e.add_field(name="件数", value=len(messages))
    e.timestamp = datetime.datetime.now() - rdelta(hours=9)
    for message in messages:
        if not message.author.bot:
            e.add_field(name="メッセージ", value=message.content)
            e.add_field(name="メッセージ送信者", value=message.author.mention)
            e.add_field(name="メッセージのid", value=message.id)
    bot.cursor.execute("select * from guilds where id=?",
                       (messages[0].guild.id,))
    gpf = bot.cursor.fetchone()
    if gpf["sendlog"]:
        ch = bot.get_channel(gpf["sendlog"])
        if ch.guild.id == messages[0].guild.id:
            await ch.send(embed=e)


@bot.event
async def on_guild_channel_create(channel):
    e = discord.Embed(title="チャンネル作成", color=bot.ec)
    e.add_field(name="チャンネル名", value=channel.mention)
    e.timestamp = datetime.datetime.now() - rdelta(hours=9)
    bot.cursor.execute("select * from guilds where id=?", (channel.guild.id,))
    gpf = bot.cursor.fetchone()
    if gpf["sendlog"]:
        ch = bot.get_channel(gpf["sendlog"])
        if ch.guild.id == channel.guild.id:
            await ch.send(embed=e)


@bot.event
async def on_guild_channel_update(b, a):
    e = discord.Embed(title="チャンネル更新", description=a.mention, color=bot.ec)
    e.timestamp = datetime.datetime.now() - rdelta(hours=9)
    if not b.name == a.name:
        if not a.guild.id == 461789442743468073:
            e.add_field(name="変更内容", value="チャンネル名")
            e.add_field(name="変更前", value=b.name)
            e.add_field(name="変更後", value=a.name)
            bot.cursor.execute(
                "select * from guilds where id=?", (a.guild.id,))
            gpf = bot.cursor.fetchone()
            if gpf["sendlog"]:
                ch = bot.get_channel(gpf["sendlog"])
                if ch.guild.id == a.guild.id:
                    await ch.send(embed=e)
    elif not b.changed_roles == a.changed_roles:
        e.add_field(name="変更内容", value="権限の上書き")
        e.add_field(name="確認:", value="チャンネル設定を見てください。")
        bot.cursor.execute("select * from guilds where id=?", (a.guild.id,))
        gpf = bot.cursor.fetchone()
        if gpf["sendlog"]:
            ch = bot.get_channel(gpf["sendlog"])
            if ch.guild.id == a.guild.id:
                await ch.send(embed=e)
    elif isinstance(b, discord.TextChannel):
        if not b.topic == a.topic:
            e.add_field(name="変更内容", value="チャンネルトピック")
            e.add_field(name="変更前", value=b.topic)
            e.add_field(name="変更後", value=a.topic)
            bot.cursor.execute(
                "select * from guilds where id=?", (a.guild.id,))
            gpf = bot.cursor.fetchone()
            if gpf["sendlog"]:
                ch = bot.get_channel(gpf["sendlog"])
                if ch.guild.id == a.guild.id:
                    await ch.send(embed=e)


@bot.event
async def on_guild_update(b, a):
    e = discord.Embed(title="サーバーの更新", color=bot.ec)
    e.timestamp = datetime.datetime.now() - rdelta(hours=9)
    if b.name != a.name:
        e.add_field(name="変更内容", value="サーバー名")
        e.add_field(name="変更前", value=b.name)
        e.add_field(name="変更後", value=a.name)
        bot.cursor.execute("select * from guilds where id=?", (a.id,))
        gpf = bot.cursor.fetchone()
        if gpf["sendlog"]:
            ch = bot.get_channel(gpf["sendlog"])
            if ch.guild.id == a.id:
                await ch.send(embed=e)
    elif b.icon != a.icon:
        e.add_field(name="変更内容", value="サーバーアイコン")
        bot.cursor.execute("select * from guilds where id=?", (a.id,))
        gpf = bot.cursor.fetchone()
        if gpf["sendlog"]:
            ch = bot.get_channel(gpf["sendlog"])
            if ch.guild.id == a.id:
                await ch.send(embed=e)
    elif b.owner.id != a.owner.id:
        e.add_field(name="変更内容", value="サーバー所有者の変更")
        e.add_field(name="変更前", value=b.owner)
        e.add_field(name="変更後", value=a.owner)
        bot.cursor.execute("select * from guilds where id=?", (a.id,))
        gpf = bot.cursor.fetchone()
        if gpf["sendlog"]:
            ch = bot.get_channel(gpf["sendlog"])
            if ch.guild.id == a.id:
                await ch.send(embed=e)


@bot.event
async def on_member_ban(g, user):
    guild = bot.get_guild(g.id)
    bl = await guild.audit_logs(limit=1, action=discord.AuditLogAction.ban).flatten()
    e = discord.Embed(title="ユーザーのban", color=bot.ec)
    e.add_field(name="ユーザー名", value=str(user))
    e.add_field(name="実行者", value=str(bl[0].user))
    # e.set_footer(text=f"{g.name}/{g.id}")
    e.timestamp = datetime.datetime.now() - rdelta(hours=9)
    bot.cursor.execute("select * from guilds where id=?", (g.id,))
    gpf = bot.cursor.fetchone()
    if gpf["sendlog"]:
        ch = bot.get_channel(gpf["sendlog"])
        if ch.guild.id == g.id:
            await ch.send(embed=e)


@bot.event
async def on_member_unban(guild, user):
    e = discord.Embed(title="ユーザーのban解除", color=bot.ec)
    e.add_field(name="ユーザー名", value=str(user))
    e.timestamp = datetime.datetime.now() - rdelta(hours=9)
    bot.cursor.execute("select * from guilds where id=?", (guild.id,))
    gpf = bot.cursor.fetchone()
    if gpf["sendlog"]:
        ch = bot.get_channel(gpf["sendlog"])
        if ch.guild.id == guild.id:
            await ch.send(embed=e)


@bot.event
async def on_guild_join(guild):
    e = discord.Embed(
        title=f"思惟奈ちゃんが{guild.name}に参加したよ！", description=f"id:{guild.id}", color=bot.ec)
    e.add_field(name="サーバー作成日時",
                value=f"{(guild.created_at+ rdelta(hours=9)).strftime('%Y{0}%m{1}%d{2} %H{3}%M{4}%S{5}').format(*'年月日時分秒')}")
    e.add_field(
        name="メンバー数", value=f"{len([i for i in guild.members if not i.bot])}ユーザー、{len([i for i in guild.members if i.bot])}bot")
    e.add_field(
        name="チャンネル数", value=f"テキスト:{len(guild.text_channels)}\nボイス:{len(guild.voice_channels)}\nカテゴリー{len(guild.categories)}")
    ch = bot.get_channel(693048937304555529)
    await ch.send(embed=e)


@bot.event
async def on_guild_remove(guild):
    ch = bot.get_channel(693048937304555529)
    await ch.send(f"`{guild.name}`(id:{guild.id})から退出しました。")


@bot.event
async def on_invite_create(invite):
    e = discord.Embed(title="サーバー招待の作成", color=bot.ec)
    e.add_field(name="作成ユーザー", value=str(invite.inviter))
    e.add_field(name="使用可能回数", value=str(invite.max_uses))
    e.add_field(name="使用可能時間", value=str(invite.max_age))
    e.add_field(name="チャンネル", value=str(invite.channel.mention))
    e.add_field(name="コード", value=str(invite.code))
    e.timestamp = datetime.datetime.now() - rdelta(hours=9)
    bot.cursor.execute("select * from guilds where id=?", (invite.guild.id,))
    gpf = bot.cursor.fetchone()
    if gpf["sendlog"]:
        ch = bot.get_channel(gpf["sendlog"])
        if ch.guild.id == invite.guild.id:
            await ch.send(embed=e)


@bot.event
async def on_invite_delete(invite):
    e = discord.Embed(title="サーバー招待の削除", color=bot.ec)
    e.add_field(name="作成ユーザー", value=str(invite.inviter))
    e.add_field(name="チャンネル", value=str(invite.channel.mention))
    e.add_field(name="コード", value=str(invite.code))
    e.timestamp = datetime.datetime.now() - rdelta(hours=9)
    bot.cursor.execute("select * from guilds where id=?", (invite.guild.id,))
    gpf = bot.cursor.fetchone()
    if gpf["sendlog"]:
        ch = bot.get_channel(gpf["sendlog"])
        if ch.guild.id == invite.guild.id:
            await ch.send(embed=e)


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
    bot.load_extension("jishaku")
    m10s_music.setup(bot)
    m10s_info.setup(bot)
    m10s_owner.setup(bot)
    m10s_settings.setup(bot)
    m10s_manage.setup(bot)
    m10s_levels.setup(bot)
    m10s_tests.setup(bot)
    m10s_gcoms.setup(bot)
    m10s_search.setup(bot)
    m10s_other.setup(bot)
    m10s_games.setup(bot)
    P143_jyanken.setup(bot)
    nekok500_mee6.setup(bot)
    syouma.setup(bot)
    pf9_symmetry.setup(bot)
    m10s_gban.setup(bot)
    m10s_bmail.setup(bot)
    m10s_auth_wiz.setup(bot)
    try:
        ch = bot.get_channel(595526013031546890)
        await ch.send(f"{bot.get_emoji(653161518531215390)}on_ready!")
    except:
        pass


@bot.event
async def on_message(message):
    if "cu:on_msg" in bot.features.get(message.author.id, []):
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
    # db.files_download_to_file( "guildsetting.json" , "/guildsetting.json" )
    # db.files_download_to_file( "profiles.json" , "/profiles.json" )
    tks = [
        domsg(message),
        globalSend(message),
    ]
    await asyncio.gather(*tks)
    # await domsg(message)
    # await globalSend(message)


async def domsg(message):
    global DoServercmd
    bot.cursor.execute("select * from users where id=?", (message.author.id,))
    pf = bot.cursor.fetchone()
    if not pf:
        bot.cursor.execute("INSERT INTO users(id,prefix,gpoint,memo,levcard,onnotif,lang,accounts,sinapartner,gban,gnick,gcolor,gmod,gstar,galpha,gbanhist) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                           (message.author.id, [], 0, {}, "m@ji☆", [], "ja", [], 0, 0, message.author.name, 0, 0, 0, 0, "なし"))
        try:
            dc = await ut.opendm(message.author)
            await dc.send(f"{bot.get_emoji(653161518153596950)}あなたの思惟奈ちゃんユーザープロファイルを作成しました！いくつかの項目はコマンドを使って書き換えることができます。詳しくはヘルプ(`s-help`)をご覧ください。\nまた、不具合や疑問点などがありましたら`mii-10#3110`にお願いします。")
        except:
            pass
        bot.cursor.execute("select * from users where id=?",
                           (message.author.id,))
        pf = bot.cursor.fetchone()

    bot.cursor.execute("select * from guilds where id=?", (message.guild.id,))
    gs = bot.cursor.fetchone()
    if not gs:
        guild_lang = bot.translate_handler.get_lang_by_guild(
            message.guild, False)
        bot.cursor.execute("INSERT INTO guilds(id,levels,commands,hash,levelupsendto,reward,jltasks,lockcom,sendlog,prefix,lang) VALUES(?,?,?,?,?,?,?,?,?,?,?)",
                           (message.guild.id, {}, {}, [], None, {}, {}, [], None, [], guild_lang))
        try:
            await message.channel.send(f"{bot.get_emoji(653161518153596950)}このサーバーの思惟奈ちゃんサーバープロファイルを作成しました！いくつかの項目はコマンドを使って書き換えることができます。詳しくはヘルプ(`s-help`)をご覧ください。\nまた、不具合や疑問点などがありましたら`mii-10#3110`にお願いします。\n思惟奈ちゃんのお知らせは`s-rnotify [チャンネルid(省略可能)]`で、コマンド等の豆知識は`s-rtopic [チャンネルid(省略可能)]`で受信する設定にできます。(Webhook管理権限が必要です。)")
        except:
            pass
        bot.cursor.execute("select * from guilds where id=?",
                           (message.guild.id,))
        gs = bot.cursor.fetchone()

    tks = [asyncio.ensure_future(dlevel(message, gs)), asyncio.ensure_future(
        gahash(message, gs)), asyncio.ensure_future(runsercmd(message, gs, pf))]
    await asyncio.gather(*tks)

    tpf = ["s-"]+pf["prefix"]+gs["prefix"]
    bot.command_prefix = tpf
    ctx = await bot.get_context(message)
    try:
        if ctx.command:
            if ctx.command.name in gs["lockcom"] and not ctx.author.guild_permissions.administrator and ctx.author.id != 404243934210949120:
                await ctx.send(ctx._("comlock-locked"))
            else:
                await bot.process_commands(message)
    except SystemExit:
        sys.exit()
    except Exception:
        print(traceback.format_exc(0))


async def runsercmd(message, gs, pf):
    # servercmd
    if "scom" not in gs["lockcom"]:
        if not message.author.id == bot.user.id and message.webhook_id is None:
            tpf = pf["prefix"]+gs["prefix"]
            tpf.append("s-")
            try:
                if not gs["commands"] is None:
                    cmds = gs["commands"]
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
                                        await message.channel.send(bot._(message.author, "scmd-notfound-role"))
                                    if role < message.author.top_role:
                                        if role in message.author.roles:
                                            await message.author.remove_roles(role)
                                            await message.channel.send(bot._(message.author, "scmd-delrole"))
                                        else:
                                            await message.author.add_roles(role)
                                            await message.channel.send(bot._(message.author, "scmd-addrole"))
                                    else:
                                        await message.channel.send(bot._(message.author, "scmd-notrole"))
                                break
            except:
                pass


async def gahash(message, gs):
    # hash
    if "s-noHashSend" in (message.channel.topic or ""):
        return
    if "hash" not in gs["lockcom"]:
        ch = gs["hash"]
        if ch is not []:
            menchan = message.channel_mentions
            for sch in menchan:
                if sch.id in ch:
                    if message.channel.is_nsfw():
                        embed = discord.Embed(title="", description=bot.l10n_guild(
                            message.guild, "hash-nsfw"), color=message.author.color)
                        embed.add_field(name=bot.l10n_guild(message.guild, "hash-from"),
                                        value=f'{bot.l10n_guild(message.guild,"hash-chmention")}:{message.channel.mention}\n{bot.l10n_guild(message.guild,"hash-chname")}:{message.channel.name}')
                        embed.add_field(name=bot.l10n_guild(
                            message.guild, "hash-link"), value=message.jump_url)
                        embed.set_author(name=message.author.display_name, icon_url=message.author.avatar_url_as(
                            static_format='png'))
                    else:
                        embed = discord.Embed(
                            title="", description=message.content, color=message.author.color)
                        embed.add_field(name=bot.l10n_guild(message.guild, "hash-from"),
                                        value=f'{bot.l10n_guild(message.guild,"hash-chmention")}:{message.channel.mention}\n{bot.l10n_guild(message.guild,"hash-chname")}:{message.channel.name}')
                        embed.add_field(name=bot.l10n_guild(
                            message.guild, "hash-link"), value=message.jump_url)
                        embed.set_author(name=message.author.display_name, icon_url=message.author.avatar_url_as(
                            static_format='png'))
                        if not message.attachments == [] and (not message.attachments[0].is_spoiler()):
                            embed.set_image(url=message.attachments[0].url)
                    await sch.send(embed=embed)


async def dlevel(message, gs):
    if "clevel" in gs["lockcom"]:
        return
    if message.author.bot:
        return
    if gs["levels"].get(str(message.author.id), None) is None:
        gs["levels"][str(message.author.id)] = {
            "level": 0,
            "exp": random.randint(5, 15),
            "lltime": int(time.time()),
            "dlu": True
        }
        bot.cursor.execute(
            "UPDATE guilds SET levels = ? WHERE id = ?", (gs["levels"], message.guild.id))
    else:
        if gs["levels"][str(message.author.id)]["dlu"]:
            if (int(time.time())-gs["levels"][str(message.author.id)]["lltime"]) >= 60:
                gs["levels"][str(message.author.id)
                             ]["lltime"] = int(time.time())
                gs["levels"][str(message.author.id)
                             ]["exp"] += random.randint(5, 15)
                if gs["levels"][str(message.author.id)]["exp"] >= gs["levels"][str(message.author.id)]["level"] ** 3 + 20:
                    gs["levels"][str(
                        message.author.id)]["exp"] -= gs["levels"][str(message.author.id)]["level"] ** 3 + 20
                    gs["levels"][str(message.author.id)]["level"] += 1
                    aut = str(message.author).replace("\\", "\\\\").replace("*", "\*").replace(
                        "_", "\_").replace("|", "\|").replace("~", "\~").replace("`", "\`").replace(">", "\>")
                    if gs["levelupsendto"]:
                        c = bot.get_channel(gs["levelupsendto"])
                        try:
                            m = await c.send(str(bot.get_emoji(653161518212448266))+bot._(message.author, "levelup-notify", aut, gs["levels"][str(message.author.id)]["level"]))
                            await asyncio.sleep(1)
                            await m.edit(content=str(bot.get_emoji(653161518212448266))+bot._(message.author, "levelup-notify", message.author.mention, gs["levels"][str(message.author.id)]["level"]))
                        except:
                            pass
                    else:
                        try:
                            m = await message.channel.send(str(bot.get_emoji(653161518212448266))+bot._(message.author, "levelup-notify", aut, gs["levels"][str(message.author.id)]["level"]))
                            await asyncio.sleep(1)
                            await m.edit(content=str(bot.get_emoji(653161518212448266))+bot._(message.author, "levelup-notify", message.author.mention, gs["levels"][str(message.author.id)]["level"]))
                        except:
                            pass
                    try:
                        if gs["reward"].get(str(gs["levels"][str(message.author.id)]["level"]), None):
                            rl = message.guild.get_role(
                                gs["reward"][str(gs["levels"][str(message.author.id)]["level"])])
                            await message.author.add_roles(rl)
                    except:
                        pass
                bot.cursor.execute(
                    "UPDATE guilds SET levels = ? WHERE id = ?", (gs["levels"], message.guild.id))


@commands.is_owner()
@bot.command()
async def ldb(ctx, name):
    bot.cursor.execute(f"select * from {name}")
    sddb = bot.cursor.fetchall()
    await ctx.send(f"{len(sddb)}")


@commands.is_owner()
@bot.command()
async def mentdb(ctx):
    bot.cursor.execute(f"select * from users")
    sddb = bot.cursor.fetchall()
    async with ctx.channel.typing():
        for ctt in sddb:
            if not (ctt["id"] in [i.id for i in bot.users]):
                bot.cursor.execute(f"delete from users where id = {ctt['id']}")
    await ctx.send("完了しました☆")


@bot.command()
async def vpc(ctx):
    await ctx.send(embed=ut.getEmbed("post count", str([f"{k}:{v}" for k, v in postcount.items()])))


@bot.command()
async def rnotify(ctx, ch: int=None):
    if ctx.author.guild_permissions.administrator or ctx.author.id == 404243934210949120:
        tchid = ch or ctx.channel.id
        tch = bot.get_channel(tchid)
        fch = bot.get_channel(667351221106901042)
        await fch.follow(destination=tch)
        await ctx.send("フォローが完了しました。")
    else:
        await ctx.send("サーバー管理者である必要があります。")


@bot.command()
async def rtopic(ctx, ch: int=None):
    if ctx.author.guild_permissions.administrator or ctx.author.id == 404243934210949120:
        tchid = ch or ctx.channel.id
        tch = bot.get_channel(tchid)
        fch = bot.get_channel(677862542298710037)
        await fch.follow(destination=tch)
        await ctx.send("フォローが完了しました。")
    else:
        await ctx.send("サーバー管理者である必要があります。")


bot.remove_command('help')


@bot.command()
async def ehelp(ctx, rcmd=None):
    # 英語ヘルプ用
    if rcmd is None:
        page = 1
        embed = discord.Embed(title=ctx._("help-1-t"),
                              description=ctx._("help-1-d"), color=bot.ec)
        embed.set_footer(text=f"page:{page}")
        msg = await ctx.send(embed=embed)
        await msg.add_reaction(bot.get_emoji(653161518195671041))
        await msg.add_reaction(bot.get_emoji(653161518170505216))
        await msg.add_reaction("🔍")
        while True:
            try:
                r, u = await bot.wait_for("reaction_add", check=lambda r, u: r.message.id == msg.id and u.id == ctx.message.author.id, timeout=30)
            except:
                break
            try:
                await msg.remove_reaction(r, u)
            except:
                pass
            if str(r) == str(bot.get_emoji(653161518170505216)):
                if page == 14:
                    page = 1
                else:
                    page = page + 1
                embed = discord.Embed(title=ctx._(
                    f"help-{page}-t"), description=ctx._(f"help-{page}-d"), color=bot.ec)
                embed.set_footer(text=f"page:{page}")
                await msg.edit(embed=embed)
            elif str(r) == str(bot.get_emoji(653161518195671041)):
                if page == 1:
                    page = 14
                else:
                    page = page - 1
                embed = discord.Embed(title=ctx._(
                    f"help-{page}-t"), description=ctx._(f"help-{page}-d"), color=bot.ec)
                embed.set_footer(text=f"page:{page}")
                await msg.edit(embed=embed)
            elif str(r) == "🔍":
                await msg.remove_reaction(bot.get_emoji(653161518195671041), bot.user)
                await msg.remove_reaction("🔍", bot.user)
                await msg.remove_reaction(bot.get_emoji(653161518170505216), bot.user)
                qm = await ctx.send(ctx._("help-s-send"))
                try:
                    msg = await bot.wait_for('message', check=lambda m: m.author == ctx.author and m.channel == ctx.channel, timeout=60)
                    sewd = msg.content
                except asyncio.TimeoutError:
                    pass
                else:
                    try:
                        await msg.delete()
                        await qm.delete()
                    except:
                        pass
                    async with ctx.message.channel.typing():
                        lang = ctx.user_lang() or "ja"
                        with open(f"lang/{lang}.json", "r", encoding="utf-8") as j:
                            f = json.load(j)
                        sre = discord.Embed(title=ctx._(
                            "help-s-ret-title"), description=ctx._("help-s-ret-desc", sewd), color=bot.ec)
                        for k, v in f.items():
                            if k.startswith("h-"):
                                if sewd in k.replace("h-", "") or sewd in v:
                                    sre.add_field(name=k.replace(
                                        "h-", ""), value=v.replace(sewd, f"**{sewd}**"))
                    await ctx.send(embed=sre)
        try:
            await msg.remove_reaction(bot.get_emoji(653161518195671041), bot.user)
            await msg.remove_reaction("🔍", bot.user)
            await msg.remove_reaction(bot.get_emoji(653161518170505216), bot.user)
        except:
            pass
    else:
        embed = discord.Embed(title=str(rcmd), description=ctx._(
            f"h-{str(rcmd)}"), color=bot.ec)
        if embed.description == "":
            await ctx.send(ctx._("h-notfound"))
        else:
            await ctx.send(embed=embed)


@bot.command()
async def help(ctx, rcmd=None):
    # ヘルプ内容
    if rcmd is None:
        page = 1
        embed = discord.Embed(title=ctx._("help-1-t"),
                              description=ctx._("help-1-d"), color=bot.ec)
        embed.set_footer(text=f"page:{page}")
        msg = await ctx.send(embed=embed)
        await msg.add_reaction(bot.get_emoji(653161518195671041))
        await msg.add_reaction(bot.get_emoji(653161518170505216))
        await msg.add_reaction("🔍")
        while True:
            try:
                r, u = await bot.wait_for("reaction_add", check=lambda r, u: r.message.id == msg.id and u.id == ctx.message.author.id, timeout=30)
            except:
                break
            try:
                await msg.remove_reaction(r, u)
            except:
                pass
            if str(r) == str(bot.get_emoji(653161518170505216)):
                if page == 16:
                    page = 1
                else:
                    page = page + 1
                embed = discord.Embed(title=ctx._(
                    f"help-{page}-t"), description=ctx._(f"help-{page}-d"), color=bot.ec)
                embed.set_footer(text=f"page:{page}")
                await msg.edit(embed=embed)
            elif str(r) == str(bot.get_emoji(653161518195671041)):
                if page == 1:
                    page = 16
                else:
                    page = page - 1
                embed = discord.Embed(title=ctx._(
                    f"help-{page}-t"), description=ctx._(f"help-{page}-d"), color=bot.ec)
                embed.set_footer(text=f"page:{page}")
                await msg.edit(embed=embed)
            elif str(r) == "🔍":
                await msg.remove_reaction(bot.get_emoji(653161518195671041), bot.user)
                await msg.remove_reaction("🔍", bot.user)
                await msg.remove_reaction(bot.get_emoji(653161518170505216), bot.user)
                qm = await ctx.send(ctx._("help-s-send"))
                try:
                    msg = await bot.wait_for('message', check=lambda m: m.author == ctx.author and m.channel == ctx.channel, timeout=60)
                    sewd = msg.content
                except asyncio.TimeoutError:
                    pass
                else:
                    try:
                        await msg.delete()
                        await qm.delete()
                    except:
                        pass
                    async with ctx.message.channel.typing():
                        lang = ctx.user_lang() or "ja"
                        with open(f"lang/{lang}.json", "r", encoding="utf-8") as j:
                            f = json.load(j)
                        sre = discord.Embed(title=ctx._(
                            "help-s-ret-title"), description=ctx._("help-s-ret-desc", sewd), color=bot.ec)
                        for k, v in f.items():
                            if k.startswith("nh-"):
                                if sewd in k.replace("nh-", "") or sewd in str(v):
                                    sre.add_field(name=k.replace(
                                        "nh-", ""), value=f"詳細を見るには`s-help {k.replace('nh-','')}`と送信")
                    await ctx.send(embed=sre)
        try:
            await msg.remove_reaction(bot.get_emoji(653161518195671041), bot.user)
            await msg.remove_reaction("🔍", bot.user)
            await msg.remove_reaction(bot.get_emoji(653161518170505216), bot.user)
        except:
            pass
    else:
        dcmd = ctx._(f"nh-{str(rcmd)}")
        if str(dcmd) == "":
            await ctx.send(ctx._("h-notfound"))
        else:
            embed = ut.getEmbed(dcmd[0], dcmd[1], bot.ec, *dcmd[2:])
            await ctx.send(embed=embed)


@bot.event
async def on_command(ctx):
    ch = bot.get_channel(693048961107230811)
    e = discord.Embed(title=f"{ctx.command.name}の実行",
                      description=f"実行文:`{ctx.message.clean_content}`", color=bot.ec)
    e.set_author(name=f"実行者:{str(ctx.author)}({ctx.author.id})",
                 icon_url=ctx.author.avatar_url_as(static_format="png"))
    e.set_footer(text=f"実行サーバー:{ctx.guild.name}({ctx.guild.id})",
                 icon_url=ctx.guild.icon_url_as(static_format="png"))
    e.add_field(name="成功したか", value=str(not ctx.command_failed))
    e.add_field(name="実行チャンネル", value=ctx.channel.name)
    e.timestamp = ctx.message.created_at
    await ch.send(embed=e)


@bot.event
async def on_command_error(ctx, error):
    # await ctx.send(f"{error}")
    # global DoServercmd
    """if isinstance(error, commands.CommandNotFound):
        if not DoServercmd:
            embed = discord.Embed(title=ctx._("cmd-error-t"), description=ctx._("cmd-notfound-d"), color=bot.ec)
            DoServercmd = False
            await ctx.send(embed=embed)
    el"""
    if isinstance(error, commands.CommandOnCooldown):
        # クールダウン
        embed = discord.Embed(title=ctx._("cmd-error-t"), description=ctx._(
            "cmd-cooldown-d", str(error.retry_after)[:4]), color=bot.ec)
        await ctx.send(embed=embed)
    elif isinstance(error, commands.NotOwner):
        # オーナー専用コマンド
        embed = discord.Embed(title=ctx._("cmd-error-t"),
                              description=ctx._("only-mii-10"), color=bot.ec)
        await ctx.send(embed=embed)
        ch = bot.get_channel(652127085598474242)
        await ch.send(embed=ut.getEmbed("エラーログ", f"コマンド:`{ctx.command.name}`\n```{str(error)}```", bot.ec, f"サーバー", ctx.guild.name, "実行メンバー", ctx.author.name, "メッセージ内容", ctx.message.content))
    elif isinstance(error, commands.MissingRequiredArgument):
        # 引数がないよっ☆
        embed = discord.Embed(title=ctx._("cmd-error-t"),
                              description=ctx._("pls-arg"), color=bot.ec)
        await ctx.send(embed=embed)
    else:
        # その他例外
        ch = bot.get_channel(652127085598474242)
        msg = await ch.send(embed=ut.getEmbed("エラーログ", f"コマンド:`{ctx.command.name}`\n```{str(error)}```", bot.ec, f"サーバー", ctx.guild.name, "実行メンバー", ctx.author.name, "メッセージ内容", ctx.message.content))
        await ctx.send(embed=ut.getEmbed(ctx._("com-error-t"), ctx._("cmd-other-d", error, bot.ec, "error id", msg.id)))


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
    pr=random.choice(bot.partnerg)
    if pr[3]!="":
        e=ut.getEmbed("思惟奈ちゃんパートナーサーバー紹介",f"{bot.get_guild(pr[0])}\n{pr[3]}\n参加: {pr[2]}")
        bot.cursor.execute("select * from globalchs where name=?",("main",))
        chs = bot.cursor.fetchone()
        for chid in chs["ids"]:
            try:
                ch = bot.get_channel(chid)
                for wh in await ch.webhooks():
                    try:
                        if wh.name == "sina_global":
                            await wh.send(embed=e)
                            await asyncio.sleep(0.2)
                            break
                    except:
                        continue
            except:
                pass

"""

apple_invite.setup(bot)
apple_foc.setup(bot)

# 通常トークン
bot.run(bot.BOT_TOKEN)

# テストトークン
# bot.run(bot.BOT_TEST_TOKEN)
