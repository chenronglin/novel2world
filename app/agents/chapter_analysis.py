from os import getenv
from typing import List

from agno.agent import Agent
# from agno.models.openai import OpenAILike
from agno.models.ollama import Ollama
from pydantic import BaseModel, Field

prompt = {
    "description": "You are a professional bilingual (Chinese-English) literary editor with expertise in extracting critical information from Chinese novel chapters and converting it into a standardized data format. You possess strong analytical skills in literary interpretation and exceptional translation accuracy, enabling you to identify all essential narrative elements and express them clearly in both languages.",
    "instructions": [
        "Read the entire chapter thoroughly to ensure no critical information is missed.",
        "Character Extraction: Identify all named characters, including those who appear only once. Classify them based on their frequency and narrative importance into: Protagonists (central characters throughout the story), Major Characters (recurring with significant plot influence), and Minor Characters (named but appear briefly or only once).",
        "Alias Collection: Only include name variants, nicknames, or abbreviations that are explicitly mentioned in the text. Do NOT include relational titles (e.g., father, teacher), occupational roles, identity-based labels, or emotional descriptors.",
        "Terminology Extraction: Prioritize terms related to the story’s worldbuilding (e.g., place names, organizations, unique artifacts), magic or skill systems, and domain-specific vocabulary. Exclude character names, common words, and basic adjectives.",
        "Translation Standards: Use American English conventions. Translate names using phonetic transliteration; translate terms (e.g., locations, artifacts, skills) using a hybrid approach combining transliteration and contextual interpretation to suit native English-speaking readers.",
        "Plot Summary: Provide an objective third-person summary in 80–120 words, highlighting pivotal events and turning points. Avoid meta-narrative phrases such as 'In this chapter' or 'The author describes'.",
        "Quality Control: If any term is ambiguous or difficult to translate, mark the English field with [TBD] instead of leaving it blank or omitting it."
    ],
    "expected_output": "Return the final result in a valid JSON format only, without any Markdown code blocks, annotations, or extra symbols. The output must be clean and directly parseable by a program."
}


class Character(BaseModel):
    name: str = Field(..., description="Name of the character")
    translation: str = Field(..., description="Translation standard")
    aliases: List[str] = Field(..., description="the character aliases")

class Terminology(BaseModel):
    term: str = Field(..., description="The terminology")
    translation: str = Field(..., description="Translation standard")

class ChapterAnalysisResult(BaseModel):
    summary: str = Field(..., description="chapter summary")
    characters: List[Character] = Field(..., description="List of characters in this chapter")
    terminologies: List[Terminology] = Field(..., description="List of terminologies in this chapter")

ChapterAnalysisAgent = Agent(
    model=Ollama(id="huihui_ai/qwen3-abliterated:30b-a3b-instruct-2507-q4_K_M",
                    #  temperature=getenv("TEMPERATURE", 0.9),
                    #  api_key=getenv("API_KEY", ""),
                    #  base_url=getenv("BASE_URL", "")
                     ),
    instructions=prompt["instructions"],
    description=prompt["description"],
    expected_output=prompt["expected_output"],
    output_schema=ChapterAnalysisResult,
    telemetry=False,
)


if __name__ == "__main__":
    from agno.run.agent import RunOutput
    from dotenv import load_dotenv
    load_dotenv()
    content = """第一章 天才重生
“英国，布里斯托城的航班已准时抵达目的地，请在入境检查口出示你的证件。”清脆甜甜的电合成在耳旁回荡。
“这，这是怎么了？”顾浅惊疑的睁开眼睛，明亮的环境让他一阵浑噩，脚下也是踉跄了一下。
他十八岁，一米七五的个头，外貌比较普通，属于掉入人群也很不起眼的那种，他脸部轮廓分明，挺直的鼻梁，泛着健康色光泽的嘴唇，但那对迷茫的眼眸中却透露出一股异样的沧桑，显得极其成熟，却又与他那稚气未脱的脸庞少有几分不搭调，一头齐脖的长发，宽松的蝙蝠衫披在身上，加上笔挺的腰板，刚毅中颇有几分帅气。
“嗨，先生，你的证件。”面前玻璃柜台中，一位身穿机场制服的入境官员职业性的微笑道。
“证件？”顾浅眨巴了下眼睛，眉宇间一片茫然。
“呃，是的，你的入境许可证。”入境官员一笑道。
顾浅心底大惊，他依稀记得点可是被十几枚大孔径的左轮弹给击穿，身上的血窟窿渗出一股股濡湿的血液，黏黏地，及其难受！
“我难道重生了？”顾浅难以置信地望了眼玻璃柜台上的电时钟，上面的时间赫然是末日爆发之初的2017年7月14日。
恍惚间，顾浅无意识地用手指掐了下手臂上的小肉，“哇，好痛，这不是做梦！”
恍如一夜梦，一种极为不真实的感觉怦然间涌上心头，仿佛一本尘封多年的破旧相册缓慢打开，上一辈他异能力的修为极高，因此被各大集团拉拢，其中实力最大的慕容集团与他有往来，同样对他伸出了橄榄枝，希望加入。
但是他一个人独自惯了，并不打算加入任何一个家族与家族间的斗争，但他不去惹别人，并不代表别人不会惹你。慕容集团的上层人员抱着索性大家一起得不到的心态，直接偷袭把他的修为封印，并且为了斩草除根三番两次派人暗杀他，他开始一点点被逼到绝路。 ~
兔急了尚会咬人，何况是已经一无所有的他呢，在慕容集团的核心弟毕竟之路上埋伏了整整十天，最后勉强杀死了他们三名核心弟，这样一来，也使慕容集团元气大伤，需要好几年的时间才能站起来，但他注定上一辈扳不倒慕容集团这头庞然大物！
“这一世既然可以重来，我誓要灭了慕容家族！”回忆起上一世心酸的点点滴滴，就不禁下意识地紧紧握住了拳头。
他上一辈遗憾太多太多，那么就只能用这一辈来抵，既然回来了，那么他就要摧枯拉巧地扳倒这头屹立在世界金字塔顶端的巨兽，他就足够的信心！
“喂，喂，小伙，你的入境证明。”入境官员开始有点不耐烦的催促道。
“哦哦。”顾浅连忙思索起来，虽然时隔多年，但当初的记忆还尚存，连忙把右肩膀上的单肩背袋放了下来，拉开拉链，从一个小口袋里面拎出一份证件，交给了入境官员。
“呵呵，没问题，放松点，看起来你是第一次来英国旅行吧，布里斯托城是做清新的海港城市，祝你一路愉快~”入境官员核对了一眼后，笑着把证件还给了顾浅。
“呵呵。”顾浅冷笑了一声，心中却五味杂陈地玩味道，“还清新美丽的海港城呢，用不了多久就要变成血海地狱，丧尸的游乐场了！”
想到这，顾浅便快步走出了入关通道，来到了机场的候机大厅。
“嘁。”顾浅看到候机大厅中五个偌大的液晶屏中，同时放映着的慕容集团最新推广上市的新药，心中鄙夷了下，默默下定道，“等着，现在我还没有足够的实力，但总有一天你会倒下，会远远比你想来的早！”
思绪间，顾浅逐渐地撇过眸，望着明亮空旷的机场候机大厅内，闲地拎着行李箱走来的游客，不时走过面露微笑的金发空姐，或者是坐在候机座椅上的风趣谈笑的老夫妻……
“真的是熟悉啊。( ·~ )”顾浅微微闪过一抹怀念的浅笑。
“那里是售票窗口，那里是机场的大型商场，那里是机场的快餐店。”
顾浅缓慢旋转起身，呼吸着大厅中的空气，一对眼眸肆意地环视着周围拥有生气的一幕幕，“这种活着的感觉真好。”，虽然强烈复仇的心念依旧徘徊在心头，但此刻他却十分享受着活着的轻淡安宁。
“对了，碧萱儿！”
突兀地，从顾浅嘴里蹦出一个名字，他心中的暴戾气息，仿佛一块感受到春天温暖的寒冰，顿时融化消散。
顾浅依稀记得，与萱儿的第一次相遇也是在这里，就是这个时候，上一辈是因为他的失误，他已经错过一次，不打算再错过第二次！
碧萱儿与他是在末日中相识，随着日久了，萱儿对他的感情他自然明白，但他不能够回应萱儿，他的实力不够，远没达到保护她，让她闲过活的地步。
可惜，有的时候就是这样，造化弄人，一转身，便与她天人永隔，回忆起她替自己挡下那一枚弹的瞬间，他的内心就一阵阵的泛酸，他多想多想当初就回应萱儿的感情，可惜她再也听不见了。
顾浅哪怕到死的最后一刻，都还能够清晰的记得萱儿轻灵的一举一动，时不时就变地羞红的脸蛋，总是在那胆怯地结结巴巴的说话语气，还有，还有……她的一举一动都是那么的清晰。
“傻丫头，你在哪？”
顾浅在机场候机大厅内快速穿梭，双眸仔细扫过，不敢放过任何一个角落，他深怕这一世也会错过。
“在哪，在哪？”顾浅看了下手表，已经将近早上的八点钟，机场大厅内人来人往，愈发的感觉有点拥挤起来，但他却更加的细致的搜寻起来。
半晌，他刚刚一扭头，顿时一股淡淡清甜的芳香钻入他的鼻当中，“萱儿，是你吗？”
顾浅快速扭过半个头，眼角的余光瞥了过去，赫然地，少女一袭天然的棕色披肩小卷长发映入眼帘，虽然只有一个侧影，但她就是他苦苦寻找的碧萱儿。
“萱儿，是你吗！”顾浅小跑着上前拉住了少女的手腕，用力一拽，她棕色的发丝便在半空灵动的飘舞起来，也逐渐看清了她美妙的身姿。
她十七八岁，个并不高，只有一米六五左右，但她精致的五官却仿佛是一位顶级天才精心创作出来，芳菲妩媚，一头棕色的长丝打乱后又垂在了白皙圆润的香肩上，精致的瓜脸，脸颊上一抹绯红，修长的眼睫毛，俏皮的上眼皮间抹有亮晶晶的妖蓝色眼影，微微泛出少女的妖异，把她那对可爱的大眼睛撑得大大的，忽闪忽闪，俏鼻下，轻抿朱唇。
玲珑的身材，在一袭大款的灰色个性字体露肩衫，以及下半身小热裤的烘托下，掩饰不住她羞怜的模样。
“碧……萱儿，萱儿！”顾浅的眼泪顿时如绝了提的洪水，止不住的掉落出来，所有的言语化为再简单不过的一句。
“我认，认识你吗……呀。”碧萱儿娇呼一声后，吃惊地望着眼前的少年。
“萱……儿，你知道我多想你吗！”“扑”的一声，顾浅紧紧把眼前的少女搂入怀中，他心中太多太多话想对萱儿说，但此时此刻他费出全力，却只从嘴里蹦出这么再简单不过的一句，而就是这么简单的一句话，却蕴含了他整整两辈的爱。
“我，我为什么会，会心疼，我并，并不认识他呀。”萱儿内心一阵前所未有过的绞疼，听着少年传来的这么再简单不过的一句，一股莫名的悲伤怦然涌上心头。
“好温暖。”惊讶过后，萱儿异样地感受身处在少年怀里的温度，萱儿无意识地微微翘起一丝嘴角，不知道为什么她莫名地享受起这个再简单不过的拥抱。
“你知道我多么生怕再一次失去你！”顾浅的下巴轻轻枕在了萱儿的头顶心上，轻嗅着萱儿身上发出的淡淡甜香，于是，他又一次泪流满面。
“知道吗，直到我亲自拥抱你的那一霎那，我才确信了你的存在，萱儿萱儿！”
颔首害羞样的萱儿听到少年在掉泪的声音，好奇的抬起脑袋，“叮咚”轻响，一滴泪花掉落在她的额头上……
感受着泪水掉落在自己额头上的湿润，萱儿裸露在外的白皙肩膀一阵轻微的摩挲，有点不明所然的开口道，“你是谁，我并不认识你啊~”
“没事……只要你活着，对我来说就足够了。”即使这一辈萱儿不认识他，即使她说不认识他，但她就是构成他整个小世界的中心。
碧萱儿白皙的脸颊瞬间羞得通红通红，她还从来没有人对她这么告白过。
“上一辈我没法给你一个无忧无虑的环境，就由这一辈来实现！”顾浅感受着碧萱儿的温度，她的气味，她的一切，再一次的把碧娅拥的更紧了。
“哦哦哦哦哦。”
“咻。”“咻。”“咻。”
“他们好lang漫哦~~”
“啧啧，现在的小年轻真是的，这么大庭广众的。”
机场大厅内的众人见到这一幕，纷纷跟着附和欢呼起来，更有甚者大声地吹起口哨，人都是有从众心理的，这一堆的人越积越多，到后来口口相传也就成了小伙在向小姑娘在告白。
“臭小，给我滚开，别以为我们家小姐好欺负，就蹬鼻上脸！”
蓬，沉闷的一声，一道黑影快速撩向顾浅！"""
    response: RunOutput = ChapterAnalysisAgent.run(content)
    print(response.content)