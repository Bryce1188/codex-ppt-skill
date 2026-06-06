# Codex PPT Skill

一个面向 Codex 的 PPT 生成 skill。它基于 `ningzimu/codex-ppt-skill` 的图片式 PPT 生产流程，并加入了更适合中文项目展示和资料调研的本地增强：

![Codex PPT Skill 效果预览](assets/showcase/slides_example.png)

- 一句话主题识别：例如“生成某某画展 PPT”，会先判断这是主题/展览/活动型任务，而不是本地项目。
- 联网资料调研：对画展、人物、品牌、地点、活动、公司、新闻、趋势等公开主题，先搜索官方和可靠来源，再生成大纲和 PPT。
- 项目证据扫描：对代码项目，读取 README、配置、源码、截图、输出结果和可能的运行命令，先生成证据清单，再写项目汇报。
- 无文字背景图：可以用 image2/imagegen 生成没有文字的背景图，再把文字放到 HTML 或 PPT 独立文字层，方便后期自己修改。
- 图片式 PPT 流程：先确认大纲、风格、图片后端和样张，再生成整套幻灯片图片并组装成 PPTX。

## 效果展示

下面是一组偏“高端科技演示风”的示例页面，用来展示这个 skill 可以生成的 PPT 观感。

| 多模式生成 | 画展调研 | 项目汇报 |
| --- | --- | --- |
| ![多模式生成](assets/showcase/slide_01.png) | ![画展调研](assets/showcase/slide_03.png) | ![项目汇报](assets/showcase/slide_04.png) |

| 无文字背景 | 稳定流程 | 输出结构 |
| --- | --- | --- |
| ![无文字背景](assets/showcase/slide_06.png) | ![稳定流程](assets/showcase/slide_07.png) | ![输出结构](assets/showcase/slide_10.png) |

## 适合什么场景

- 课程展示、项目答辩、毕业设计、比赛路演。
- 从一个代码仓库自动总结项目内容和亮点。
- 从一句话主题生成资料型 PPT，例如画展介绍、人物介绍、品牌发布会、旅行分享。
- 从文章、报告、论文、笔记、大纲生成视觉统一的演示文稿。
- 生成无文字背景图，让用户自己在 PPT 或 HTML 中加文字。

## 安装

推荐让 Codex 直接安装这个 GitHub 仓库：

```text
请帮我安装这个 Codex skill：https://github.com/Bryce1188/codx-ppt-skill ，skill 名称是 codex-ppt-skill
```

也可以手动安装到 Codex skills 目录：

```bash
npx -y skills@latest add Bryce1188/codx-ppt-skill \
  --skill codex-ppt-skill \
  --agent codex \
  --global
```

本地开发时，可以把仓库里的 skill 文件夹链接到 Codex：

```bash
mkdir -p ~/.codex/skills
ln -s /path/to/codx-ppt-skill/skills/codex-ppt-skill ~/.codex/skills/codex-ppt-skill
```

Windows 示例：

```powershell
New-Item -ItemType Junction `
  -Path "$env:USERPROFILE\.codex\skills\codex-ppt-skill" `
  -Target "D:\obsidian知识库\Skill文件\codex-ppt-skill"
```

## 使用示例

### 生成画展 PPT

```text
用 $codex-ppt-skill 生成一个莫奈画展介绍 PPT，8 页，中文，先联网查官方资料和可靠介绍，图片不要编造来源。
```

### 生成项目汇报 PPT

```text
用 $codex-ppt-skill 分析当前项目，结合运行截图，生成一个 10 页中文项目答辩 PPT。
```

### 生成无文字背景，方便后期加字

```text
用 $codex-ppt-skill 做一个项目展示 PPT，背景图用 image2 生成，但图片里不要出现文字，用 HTML/PPT 独立文字层方便我自己改。
```

### 从文章或报告生成 PPT

```text
用 $codex-ppt-skill 把这篇报告做成 12 页演示文稿，风格清爽专业，保留关键数据和来源。
```

## 工作模式

### 1. 默认图片式 PPT

每页生成一张完整 16:9 幻灯片图片，最后用脚本组装成 PPTX。适合追求视觉统一和强展示效果的场景。

### 2. 主题/画展/活动联网调研

当用户只给一句话主题时，skill 会先判断任务不是本地项目，而是主题型任务。它会搜索官方来源、主办方页面、博物馆/画廊页面、权威媒体和资料库，核验时间、地点、人物、展品、背景、图片来源等信息，再生成 PPT。

### 3. 项目汇报

当输入是项目目录或代码仓库时，skill 会运行 `scripts/analyze_project.py`，生成项目证据清单，并基于真实代码、README、截图、输出结果、测试和运行命令组织 PPT。

### 4. 无文字背景 + 可编辑文字层

当用户希望后期自己加字时，skill 会要求背景图 prompt 禁止文字、字母、数字、logo、水印和签名。文字用 HTML 或 PPT 文本框叠加，避免被烘焙进图片里。

## 输出结构

典型生成目录：

```text
{输出目录}/{PPT名称}/
├─ origin_image/
│  ├─ slide_01.png
│  ├─ slide_02.png
│  └─ ...
├─ prompts/
│  ├─ slide_01.json
│  └─ ...
├─ outline.md
├─ speech.md
├─ deck_spec.json
├─ slide_jobs.json
├─ slide_run_state.json
└─ {PPT名称}.pptx
```

其中 `speech.md` 会作为演讲备注写入 PPT。

## 主要文件

```text
skills/codex-ppt-skill/
├─ SKILL.md
├─ docs/
│  ├─ topic-web-research.md
│  ├─ project-report-audit.md
│  ├─ project-visual-evidence.md
│  └─ textless-backgrounds-and-html.md
├─ scripts/
│  ├─ assemble_ppt.py
│  ├─ image_gen.py
│  ├─ analyze_project.py
│  └─ create_background_html.py
├─ references/
└─ prompts/
```

## 配置说明

在 Codex 中优先使用内置图片生成/编辑工具。只有内置后端不可用、缺少能力，或用户明确要求 API/CLI 模式时，才使用 `scripts/image_gen.py`。

API/CLI fallback 支持这些环境变量：

```text
OPENAI_API_KEY
OPENAI_BASE_URL
CODEX_PPT_IMAGE_MODEL
CODEX_PPT_HOME
```

不要把 API key 写入仓库。

## 来源与致谢

主体 PPT 生成流程来自 [ningzimu/codex-ppt-skill](https://github.com/ningzimu/codex-ppt-skill)，遵循 MIT License。本仓库在此基础上加入了中文化说明、主题联网调研、项目证据扫描和无文字背景 HTML 工作流。

## License

MIT
