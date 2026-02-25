from pathlib import Path
import re
from bs4 import BeautifulSoup, Comment, NavigableString

FILES = [
    Path(r"d:\howtobestusai1\HappyCapy\快速上手 3096ea0499868002bcddc67c919bd1d4.html"),
    Path(r"d:\howtobestusai1\HappyCapy\欢迎使用Happycapy 3096ea04998680118520f6984c65445d.html"),
    Path(r"d:\howtobestusai1\HappyCapy\联系我们 3096ea04998680e88619c30a159342f9.html"),
    Path(r"d:\howtobestusai1\HappyCapy\欢迎使用Happycapy\一句话案例\Vibe-Coding 3096ea049986819b87a4c7f527d82ef0.html"),
    Path(r"d:\howtobestusai1\HappyCapy\欢迎使用Happycapy\一句话案例\内容创作 3096ea04998681c68aa2e95ef10017fb.html"),
    Path(r"d:\howtobestusai1\HappyCapy\欢迎使用Happycapy\一句话案例\文档处理 3096ea049986817bb900c16d8e1674b0.html"),
    Path(r"d:\howtobestusai1\HappyCapy\欢迎使用Happycapy\一句话案例\股票分析 3096ea04998681c1b315f10506bee25d.html"),
]

TRANSLATIONS = {
    "快速上手": "Quick Start",
    "🚗Happycapy官网直通车：": "🚗HappyCapy Official Website:",
    "第一步：打开 HappyCapy": "Step 1: Open HappyCapy",
    "访问": "Visit",
    ",注册并登录后，你会看到如下界面": ", sign up and log in, and you will see the interface below.",
    "📂 左侧边栏": "📂 Left Sidebar",
    "💬 对话区": "💬 Chat Area",
    "输入框": "Input Box",
    "+ 上传": "+ Upload",
    "第一次对话：让 HappyCapy 帮你做点什么": "Your First Chat: Ask HappyCapy to Do Something",
    "别紧张，就像和朋友聊天一样。": "No need to be nervous—just chat as if you were talking to a friend.",
    "在中间的输入框里，试试这句话:": "In the input box in the center, try this sentence:",
    "按回车。": "Press Enter.",
    "或者": "Or",
    "HappyCapy 会根据你的要求调整。": "HappyCapy will adjust based on your request.",
    "你可以在outputs中看到这些图片 并可以下载 版权完全属于你": "You can see these images in outputs and download them. Full rights belong to you.",
    "- 上传文件放这里": "- Drop uploaded files here",
    "把你的文件拖进来，HappyCapy 就能看到": "Drag your files in, and HappyCapy can read them.",
    "支持几乎所有常见格式：图片、视频、PDF、Excel、Word...": "Supports almost all common formats: images, videos, PDF, Excel, Word...",
    "一次可以传多个文件": "You can upload multiple files at once.",
    "几个快速上手的例子": "A Few Quick-Start Examples",
    "通过两个简单案例，快速上手 HappyCapy。": "Use two simple cases to get started with HappyCapy quickly.",
    "📸 案例 1：生成图片并下载": "📸 Case 1: Generate an Image and Download It",
    "最简单的例子，10 秒上手。": "The simplest example—get started in 10 seconds.",
    "第 1 步：": "Step 1:",
    "在输入框说出你的需求": "Describe your request in the input box.",
    "第 2 步：": "Step 2:",
    "等待生成（约 10-15 秒）": "Wait for generation (about 10–15 seconds).",
    "图片会显示在对话区，自动保存在 outputs 文件夹。": "The image will appear in the chat area and be saved automatically in the outputs folder.",
    "第 3 步：": "Step 3:",
    "下载到本地": "Download to your local device.",
    "方法 1：右侧文件列表找到图片，右键下载": "Method 1: Find the image in the file list on the right and right-click to download.",
    "方法 2：直接说「把这张图片打包给我下载」": "Method 2: Simply say, “Package this image for download.”",
    "💡 不满意？直接说「再来一张，风格更卡通一点」，HappyCapy 会继续调整。": "💡 Not satisfied? Just say, “Generate another one with a more cartoon style,” and HappyCapy will keep refining.",
    "📂 案例 2：上传文件并处理": "📂 Case 2: Upload and Process Files",
    "学会上传文件，HappyCapy 能帮你处理各种文档。": "Once you learn file upload, HappyCapy can help you process all kinds of documents.",
    "上传文件（两种方式）": "Upload files (two methods)",
    "方法 1：": "Method 1:",
    "直接拖拽文件到对话窗口": "Drag files directly into the chat window.",
    "方法 2：": "Method 2:",
    "点击输入框左边的 + 号，选择文件": "Click the + icon on the left of the input box and choose files.",
    "告诉 HappyCapy 要做什么": "Tell HappyCapy what you want to do.",
    "等待处理完成": "Wait until processing is complete.",
    "HappyCapy 会读取文件、处理数据、生成新文件，并告诉你改了什么。处理好的文件会保存在 outputs 文件夹。": "HappyCapy will read files, process data, generate new files, and tell you what changed. Processed files will be saved in the outputs folder.",
    "📌 支持的文件：图片（JPG/PNG）、文档（PDF/Word/Excel）、视频（MP4）、数据（CSV/JSON）、代码（所有语言）。单个文件最大 100MB。": "📌 Supported files: images (JPG/PNG), documents (PDF/Word/Excel), video (MP4), data (CSV/JSON), code (all languages). Max size per file: 100MB.",
    "💡 快速提示": "💡 Quick Tips",
    "说清楚需求：": "State your request clearly:",
    "越具体越好": "The more specific, the better.",
    "分步说：": "Describe it step by step:",
    "边做边调整": "Adjust as you go.",
    "给例子：": "Provide examples:",
    "上传参考图，HappyCapy 会学习": "Upload reference images and HappyCapy will learn from them.",
    "不满意就说：": "If you're not satisfied, say it directly:",
    "直接指出问题": "Point out the issue directly.",

    "欢迎使用Happycapy": "Welcome to HappyCapy",
    "HappyCapy 官网直通车：": "HappyCapy Official Website:",
    "在这里，你可以看到机智可爱的 HappyCapy 如何成为你的 AI 伙伴，一起探索无限可能！": "Here, you can see how the smart and lovely HappyCapy becomes your AI partner to explore unlimited possibilities together!",
    "Happycapy是什么？": "What is HappyCapy?",
    "一台运行在浏览器里的 Agent 原生计算机。": "An Agent-native computer running in your browser.",
    "由 Claude Code 驱动，为所有人设计。": "Powered by Claude Code, designed for everyone.",
    "不需要配环境，不需要学命令行，不需要懂技术。打开浏览器，说出你的需求，看着它帮你完成工作。": "No environment setup, no command line, no technical background needed. Open your browser, describe what you need, and watch it complete the work for you.",
    "生成图片、剪辑视频、处理数据、做网页、写论文...以前需要学十几个软件才能做的事，现在只需要说出来。": "Generate images, edit videos, process data, build web pages, write papers... Tasks that once required learning many tools now only require saying what you want.",
    "过去一年，我们看到 AI Agent 能做的事越来越多。但大部分 Agent 工具都是为开发者设计的——要会用命令行，要懂得配置环境，要知道怎么处理安全问题。我们觉得，Agent 不应该只属于懂技术的人。所以我们做了 HappyCapy。": "Over the past year, we have seen AI Agents do more and more. But most Agent tools are designed for developers—you need command-line skills, environment setup knowledge, and security handling experience. We believe Agents should not belong only to technical users. So we built HappyCapy.",
    "💻传统电脑的逻辑：": "💻 Traditional computer logic:",
    "装软件 → 学软件 → 用软件完成任务": "Install software → Learn software → Use software to finish tasks",
    "🤖Agent 原生计算机的逻辑：": "🤖 Agent-native computer logic:",
    "说需求 → AI 调用工具 → 直接给结果": "State your needs → AI calls tools → Get results directly",
    "HappyCapy能做什么？": "What can HappyCapy do?",
    "打开 HappyCapy，说几句话就能：": "Open HappyCapy and with just a few sentences you can:",
    "生成图片和视频": "Generate images and videos",
    "- 海报、配图、短视频、动画": "- Posters, illustrations, short videos, animations",
    "处理文档和数据": "Process documents and data",
    "- Word、Excel、PPT、PDF、图表": "- Word, Excel, PPT, PDF, charts",
    "做网页和应用": "Build websites and apps",
    "- 设计界面、写代码、自动部署上线": "- Design interfaces, write code, deploy automatically",
    "写论文和报告": "Write papers and reports",
    "- 文献综述、学术论文、标准引用": "- Literature reviews, academic papers, standard citations",
    "自动化日常工作": "Automate daily work",
    "- 整理文件、发邮件、做表格、分析数据": "- Organize files, send emails, create spreadsheets, analyze data",
    "以前需要学十几个软件、在不同工具间反复切换的事，现在一个地方搞定。": "What used to require many tools and constant switching can now be done in one place.",
    "云端运行，零门槛": "Runs in the cloud, zero barrier",
    "不用安装软件或配环境": "No software installation or environment setup",
    "不用担心在本地乱改文件": "No worries about messing up local files",
    "内置沙盒，安全可靠": "Built-in sandbox, safe and reliable",
    "手机也能用": "Also works on mobile",
    "对话式操作，和屏幕背后勤劳的 HappyCapy 聊天": "Conversational operation—chat with the hardworking HappyCapy behind the screen",
    "不用学菜单、快捷键、代码。直接说需求：": "No need to learn menus, shortcuts, or code. Just describe your needs:",
    "一句话案例": "One-Line Use Cases",
    "名称": "Name",
    "创建时间": "Created At",
    "标签": "Tags",
    "内容创作": "Content Creation",
    "@2026年2月16日 13:28": "@Feb 16, 2026 13:28",
    "股票分析": "Stock Analysis",
    "文档处理": "Document Processing",
    "HappyCapy背后的故事": "The Story Behind HappyCapy",
    "我们自己先变成了 AI native 团队": "We first became an AI-native team ourselves",
    "2025 年 1 月，Claude Code 出来了。它改变了编码的模式——开发者可以用自然语言写代码，效率提升了好几倍。": "In January 2025, Claude Code arrived. It changed the coding model—developers could write code with natural language, improving efficiency by several times.",
    "我们团队用得很爽。但同时我们也在想：": "Our team loved using it. But we were also thinking:",
    "为什么 AI 的门槛还是这么高？": "Why is the barrier to using AI still so high?",
    "想用好 AI，要么懂命令行、会配环境、学提示词，要么就只能停留在聊天窗口里，很难发挥出 AI 的全部能力。为什么不能像用电脑一样简单？": "To use AI well, you either need command-line skills, environment setup, and prompt engineering, or you stay limited to chat windows and can hardly unlock AI's full capability. Why can't it be as simple as using a computer?",
    "AI 应该是平权的。": "AI should be equal for everyone.",
    "不管你是什么职业、什么背景——每个人都应该平等地享受 AI 带来的生产力提升。": "No matter your profession or background—everyone should equally enjoy the productivity gains brought by AI.",
    "所以我们给自己做了一个工具。用上之后，整个团队的工作方式改变了。不懂技术的人也能自己写代码、做网页、处理数据。每个人都能把想法变成现实。": "So we built a tool for ourselves. After using it, our team's way of working changed. Non-technical people could write code, build web pages, and process data on their own. Everyone could turn ideas into reality.",
    "每个人都成了超级个体。": "Everyone became a super individual.",
    "然后我们把这套工作方式产品化了，就是 HappyCapy。": "Then we productized this way of working—it became HappyCapy.",
    "为什么是Capy（卡皮巴拉-": "Why Capy (capybara—",
    "Capybara-水豚": "Capybara",
    "水豚温和、友善、与所有动物和谐相处。你能在网上看到水豚和猴子、鸟、鳄鱼、甚至猫狗都能玩在一起。": "Capybaras are gentle, friendly, and get along with all animals. Online, you can see capybaras hanging out with monkeys, birds, crocodiles, and even cats and dogs.",
    "这正是我们想要的：一个和所有人都能\"相处\"的 AI 工具。": "This is exactly what we want: an AI tool that can \"get along\" with everyone.",
    "Happy + Capy = 快乐的水豚 = AI应该使人 变得快乐而不是焦虑。": "Happy + Capy = a joyful capybara = AI should make people happier, not more anxious.",
    "我们希望大家用 HappyCapy 的时候，就像养一只卡皮巴拉一样——chill，没有焦虑，回归到生活本身。": "We hope using HappyCapy feels like having a capybara—chill, no anxiety, and back to life itself.",
    "我们的愿景": "Our Vision",
    "让所有人都用上 AI，自动化自己的工作流，减少人的重复性工作。": "Enable everyone to use AI, automate their workflows, and reduce repetitive human work.",
    "我们不觉得 AI 是用来取代人的。我们觉得 AI 是用来让人更像人的——把重复的、烦人的、消耗时间的事情交给 AI，把创意、判断、决策留给自己。": "We do not believe AI is for replacing people. We believe AI helps people be more human—hand repetitive, annoying, time-consuming tasks to AI, and keep creativity, judgment, and decisions for yourself.",
    "你只需要专注于做什么，而不是怎么做。": "You only need to focus on what to do, not how to do it.",
    "你不用纠结今天该用哪个模型，不用被每天 AI 新突破的新闻搞得焦虑。": "You don't need to struggle over which model to use today, or feel anxious about daily AI breakthrough news.",
    "生图用什么模型最好？视频该选哪个？这个任务适合 Claude 还是 GPT？": "Which model is best for image generation? Which one for video? Is this task better for Claude or GPT?",
    "别想了。HappyCapy 会帮你选。": "No need to overthink it. HappyCapy will choose for you.",
    "为了让你真正享受做事，我们提供了 Max plan——无限 token，完全没有焦虑。": "To help you truly enjoy getting things done, we provide the Max plan—unlimited token usage, no anxiety.",
    "不管你是创作者、开发者、学生、上班族、还是自由职业者——只要你有想法，HappyCapy 就能帮你把想法变成现实。": "Whether you're a creator, developer, student, office worker, or freelancer—as long as you have an idea, HappyCapy can help turn it into reality.",
    "开始使用 HappyCapy →": "Start using HappyCapy →",

    "联系我们": "Contact Us",
    "💬 加入我们的社区": "💬 Join Our Community",
    "有问题？想分享你的创意？或者只是想和其他 HappyCapy 用户聊聊天？": "Have questions? Want to share your ideas? Or just chat with other HappyCapy users?",
    "🎮 加入 Discord 社区": "🎮 Join the Discord Community",
    "在这里你可以：": "Here you can:",
    "• 获取即时帮助和技术支持": "• Get instant help and technical support",
    "• 分享你创建的 Skills 和自动化": "• Share the Skills and automations you created",
    "• 参与产品讨论和功能建议": "• Join product discussions and feature suggestions",
    "• 认识志同道合的 AI 爱好者": "• Meet like-minded AI enthusiasts",
    "👉 立即加入：": "👉 Join now:",
    "🐦 关注我们的 X (Twitter)": "🐦 Follow us on X (Twitter)",
    "• 获取产品更新和新功能发布": "• Get product updates and new feature releases",
    "• 第一时间了解 AI 行业动态": "• Stay on top of AI industry trends",
    "• 参与话题讨论和互动": "• Participate in discussions and interactions",
    "👉 立即关注：": "👉 Follow now:",
    "🎥 订阅 YouTube 频道": "🎥 Subscribe to our YouTube Channel",
    "• 观看详细的功能教程": "• Watch detailed feature tutorials",
    "• 学习 Skills 创建和使用技巧": "• Learn Skills creation and usage tips",
    "• 查看实战案例演示": "• See real-world case demonstrations",
    "👉 立即订阅：": "👉 Subscribe now:",
    "💬 加入微信群": "💬 Join the WeChat Group",
    "HappyCapy 中文社区": "HappyCapy Chinese Community",
    "• 与中文用户深度交流": "• Deep conversations with Chinese-speaking users",
    "• 分享使用经验和创意": "• Share usage experience and ideas",
    "• 获得中文支持和帮助": "• Get support in Chinese",
    "一起探索 AI 的无限可能！": "Let's explore AI's unlimited possibilities together!",
    "📮 其他联系方式": "📮 Other Contact Channels",
    "官方网站": "Official Website",
    "文档反馈": "Documentation Feedback",
    "：如果你在使用时发现问题或有改进建议，欢迎随时告诉我们": ": If you find issues or have suggestions while using it, feel free to tell us anytime.",
}

SKIP_TAGS = {"script", "style", "code", "pre", "svg", "noscript", "textarea"}
CJK_RE = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]")


def replace_keep_ws(raw: str, new_core: str) -> str:
    m = re.match(r"^(\s*)(.*?)(\s*)$", raw, flags=re.S)
    if not m:
        return new_core
    return f"{m.group(1)}{new_core}{m.group(3)}"


for source in FILES:
    html = source.read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "lxml")

    if soup.title and soup.title.string:
        raw_title = str(soup.title.string)
        key = raw_title.strip()
        if key in TRANSLATIONS:
            soup.title.string.replace_with(replace_keep_ws(raw_title, TRANSLATIONS[key]))

    for node in soup.find_all(string=True):
        if isinstance(node, Comment):
            continue
        if not isinstance(node, NavigableString):
            continue
        parent = node.parent
        if parent is not None and parent.name and parent.name.lower() in SKIP_TAGS:
            continue
        raw = str(node)
        key = raw.strip()
        if key in TRANSLATIONS:
            node.replace_with(replace_keep_ws(raw, TRANSLATIONS[key]))

    out_path = source.with_name(f"{source.stem}_en{source.suffix}")
    out_path.write_text(str(soup), encoding="utf-8")
    print(f"WROTE\t{out_path}")

# post-check for remaining Chinese in visible text/title
for source in FILES:
    out_path = source.with_name(f"{source.stem}_en{source.suffix}")
    soup = BeautifulSoup(out_path.read_text(encoding="utf-8"), "lxml")
    remains = []
    if soup.title and soup.title.string and CJK_RE.search(soup.title.string):
        remains.append(soup.title.string.strip())

    for node in soup.find_all(string=True):
        if isinstance(node, Comment):
            continue
        parent = node.parent
        if parent is not None and parent.name and parent.name.lower() in SKIP_TAGS:
            continue
        s = str(node).strip()
        if s and CJK_RE.search(s):
            remains.append(s)

    uniq = []
    seen = set()
    for s in remains:
        if s not in seen:
            seen.add(s)
            uniq.append(s)

    print(f"REMAIN\t{out_path.name}\t{len(uniq)}")
    for item in uniq[:8]:
        print(f"  - {item}")
