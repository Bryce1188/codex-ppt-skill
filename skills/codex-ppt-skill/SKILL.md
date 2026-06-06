---
name: codex-ppt-skill
description: 从一句话主题、文章、报告、论文、笔记、大纲、公开活动/画展信息或软件项目文件夹生成视觉统一的 PPT/PPTX。适用于基于 codex-ppt 流程的图片式整页幻灯片、需要联网调研画展/人物/品牌/事件等公开主题的资料型 PPT、需要识别项目代码和运行证据的项目汇报 PPT，以及需要 image2/imagegen 生成无文字背景图、再用 HTML/PPT 独立文字层方便后期编辑的演示文稿。
---

# Codex PPT Skill

## 概览

这个 skill 以 `ningzimu/codex-ppt-skill` 为主体，负责把来源材料做成视觉统一的 PowerPoint。默认模式是“图片式 PPT”：每一页先生成一张完整的 16:9 幻灯片图片，再用 `scripts/assemble_ppt.py` 组装成 `.pptx`。

本地版本额外保留了你原来 skill 的三个增强能力：

- **一句话主题识别**：当用户只给一句话，例如“生成某某画展 PPT”，先判断这不是项目目录，而是主题/活动/展览型任务。
- **联网调研**：对画展、活动、人物、品牌、地点、最新公开资料等不稳定信息，先联网搜索并交叉核验，再生成 PPT。
- **项目识别**：读取项目文件夹、README、配置、源码、测试、图片和可能的运行命令，先形成项目证据包，再写 PPT 故事。
- **运行证据优先**：优先使用真实运行截图、项目照片、终端输出、图表、notebook 导出、项目生成结果，而不是只用装饰图。
- **无文字背景 + 可编辑文字层**：当用户要求后期自己改文字时，用 image2/imagegen 生成无文字背景图，再用 HTML 或 PPT 原生文本框叠加文字。

## 使用模式

### 默认图片式 PPT

用于用户想要强视觉统一、接受“每页是一张完整图片”的 PPT。优点是画面一致、风格强、适合展示；缺点是图片里的文字和图形不是 PowerPoint 原生可编辑元素。

### 项目汇报 PPT

用于用户给出代码仓库、项目目录、运行截图、项目照片、README、notebook、日志或输出结果，希望 Codex 识别项目内容并总结成 PPT。

在这个模式下，先读：

- `docs/project-report-audit.md`
- `docs/project-visual-evidence.md`

并运行：

```bash
python scripts/analyze_project.py <project-root> --out <work-or-output-dir>
```

### 主题/画展/活动调研 PPT

用于用户只给一句话或一个主题，例如：

- 生成莫奈画展 PPT
- 做一个某某艺术展介绍
- 介绍某品牌发布会
- 生成某城市旅行分享 PPT
- 做某个人物/公司/技术趋势的汇报 PPT

这类输入通常不是本地项目。不要硬套项目识别流程，而要先联网调研。

在这个模式下，先读：

- `docs/topic-web-research.md`

并执行：

1. 判断主题类型：画展/艺术家/品牌/活动/人物/地点/技术趋势/课程分享/商业汇报等。
2. 联网搜索官方来源、主办方页面、博物馆/画廊页面、新闻报道、百科/数据库、图片来源和日期信息。
3. 优先使用官方来源；对时间、地点、展品、人物、主办方、票务、背景等事实做交叉核验。
4. 建立资料摘要和来源清单，不要编造不存在的展览、展品、数据或评价。
5. 再把资料转成 PPT 大纲、视觉方向和素材计划。

### 无文字背景模式

用于用户明确说：

- 用 image2/imagegen 生成背景图
- 图片里不要文字
- 文字后面自己加
- 用 HTML 把图作为背景
- PPT 文字要能编辑

在这个模式下，先读：

- `docs/textless-backgrounds-and-html.md`

需要 HTML 草稿时运行：

```bash
python scripts/create_background_html.py <bg-1.png> <bg-2.png> --out index.html
```

## 硬性约束

- 每个阶段都要先读对应的 `Reference Map` 文件；`SKILL.md` 只写总流程，细节规则在 `docs/` 和 `prompts/` 里。
- 遵守审批门。没有用户确认前，不要擅自生成最终 `deck_spec.json`、`speech.md`、整套图片、prompt jobs 或 `.pptx`。
- 先确认大纲，再确认视觉风格，再确认生图后端，再生成一页样张；样张通过后才能生成全套 PPT。
- 默认图片式 PPT 中，最终 `origin_image/slide_XX.png` 必须来自确认过的图片生成后端：Codex 内置图片生成工具或 `scripts/image_gen.py`。
- 默认图片式 PPT 中，不要用本地绘图、Pillow、SVG、HTML/CSS/canvas 截图、python-pptx、PptxGenJS 或手工叠层冒充最终幻灯片图片。
- 无文字背景模式例外：HTML 只能作为“图片背景 + 独立可编辑文字层”的草稿或编辑载体，不能把 HTML 截图当作默认图片式 PPT 的偷懒替代。
- 一旦确认图片生成后端，后续样张、子任务和整套幻灯片都要使用同一路径，不要为了方便临时换后端。
- 如果运行环境支持子 agent，样张确认后剩余页应尽量按页分发给子 agent 生成；主 agent 负责统筹、状态记录、QA、讲稿和组装。
- 任何缺失的子 agent、图片后端或必需素材都会影响质量时，要明确报告阻塞，不要用低质量替代品糊过去。

## 可见进度

非简单任务要维护一个用户可见 checklist，并且同一时间只让一个步骤处于进行中。

默认步骤：

1. 准备来源材料、大纲、风格和图片后端决策。
2. 生成并确认一页样张。
3. 准备每页生成任务和状态文件。
4. 分发幻灯片生成任务。
5. 记录已生成的幻灯片结果。
6. QA、修复、写讲稿并组装 PPT。

不要只因为聊天里说了“完成”就标记完成；要有实际文件或脚本状态作为证据。

## 默认工作流

1. 理解来源内容。
   - 识别主题、受众、目标、页数、风格/品牌约束、需要包含或排除的部分。
   - 如果用户没有指定页数，通常选择 8-12 页。
   - 如果用户只给一句话主题、画展、活动、地点、人物、品牌或最新公开信息，先按主题/画展/活动调研模式联网查资料。
   - 如果来源是项目文件夹，先按项目汇报模式审计项目证据。
   - 如果用户要可编辑文字层，先按无文字背景模式规划。

2. 规划 PPT 大纲。
   - 读 `docs/workflow-gates-and-progress.md` 和 `docs/outline-style-and-sample.md`。
   - 为每一页写清楚页码、标题、3-5 个要点、视觉想法、页面角色、必需素材。
   - 向用户确认大纲；确认前不要进入风格、后端、样张或整套生成。

3. 确认统一视觉风格。
   - 读 `docs/outline-style-and-sample.md`。
   - 如果用户没有明确风格，给 2-3 个具体方向并推荐一个。
   - 如果用户提供了图片、PDF、PPT/PPTX 作为风格参考，先渲染或查看实际页面图，再提取可用风格规则。
   - 使用 `references/` 里的风格作为灵感，不要机械套模板。

4. 确认图片生成后端。
   - 读 `docs/backend-selection.md`。
   - 优先使用 Codex 内置图片生成/编辑工具。
   - 只有内置后端不可用、缺能力，或用户明确要求 API/CLI 时，才使用 `scripts/image_gen.py`。
   - 如需 API/CLI fallback，再读 `docs/cli-api-fallback.md` 和必要的 `docs/image-model-configuration.md`。

5. 生成一页样张。
   - 样张必须在大纲、风格、后端确认后生成。
   - 优先选代表性内容页，不要只做封面。
   - 保存为目标页文件，例如 `origin_image/slide_03.png`。
   - 展示样张给用户确认视觉风格、版式密度、文字清晰度和中文质量。
   - 用户确认前不要生成全套 PPT。

6. 创建项目目录。
   - 读 `docs/project-assembly-and-reporting.md`。
   - 如果用户没有指定输出目录，用当前工作目录或来源文件所在目录。
   - 项目目录应包含 `origin_image/`、`prompts/`、`outline.md`、`speech.md`、`deck_spec.json`、状态文件和最终 `.pptx`。

7. 准备用户素材。
   - 读 `docs/user-supplied-assets.md`。
   - 对论文图、实验结果图、架构图、截图、logo、项目照片等严格素材，先确认它们对应哪一页、承担什么角色。
   - 项目汇报中，真实运行截图和项目输出优先于装饰性生成图。

8. 生成全部幻灯片图片。
   - 读 `docs/slide-generation-and-subagents.md`。
   - 用 `scripts/prepare_slide_prompts.py` 或保存好的 `prompts/slide_XX.json` 准备每页任务。
   - 每页最终图片必须记录来源和状态。

9. 分发子 agent。
   - 运行环境支持时，样张通过后每个剩余 slide job 尽量交给一个子 agent。
   - 子 agent 只负责自己的 `prompts/slide_XX.json`，返回图片路径、后端和 QA 备注。
   - 主 agent 负责记录结果、修复、组装和最终报告。

10. QA 和修复。
    - 读 `docs/project-assembly-and-reporting.md`。
    - 检查每页是否符合大纲、文字是否清晰、是否截断、风格是否一致、素材是否正确、元素是否重叠。
    - 严重问题要重新生成；局部问题可用图片编辑能力修复。
    - 无文字背景模式下，额外检查背景图不能出现文字、字母、数字、logo、水印或签名。

11. 写演讲稿并组装 PPT。
    - `speech.md` 使用 `Slide N` 标题，便于脚本写入 PowerPoint 备注区。
    - 中文 PPT 的讲稿也写中文，避免机械复述页面文字。
    - 组装前确认 `slide_jobs.json` 和 `slide_run_state.json` 没有 pending、dispatched 或 blocked 状态。
    - 使用 `scripts/assemble_ppt.py` 生成最终 `.pptx`。

12. 汇报结果。
    - 给出项目目录、PPT 文件、图片目录、大纲、讲稿、状态文件路径。
    - 说明页数、使用的图片后端、是否写入演讲备注、是否有阻塞或限制。
    - 项目汇报要说明证据来自哪些项目文件、截图或运行输出。

13. 保存可复用风格。
    - 用户要求保存风格时，读 `docs/style-library.md`。
    - 可把满意的风格沉淀到 `references/`，以后继续复用。

## 项目汇报增强流程

当用户要求“识别这个项目并做 PPT”时，按下面做：

1. 把当前工作区或用户指定目录作为项目根目录。
2. 读高信号文件：`README*`、`docs/`、`package.json`、`pyproject.toml`、`requirements*.txt`、入口文件、测试、部署配置、输出目录。
3. 运行 `scripts/analyze_project.py` 生成 `project-ppt-evidence.json` 和 `project-ppt-evidence.md`。
4. 提取项目名称、目标用户、解决的问题、核心功能、技术架构、关键实现、运行证据、限制和后续计划。
5. 只把有证据支持的内容写进 PPT；不要把 TODO、注释、计划中的功能说成已完成。
6. 优先使用真实截图、项目照片、终端输出、模型/数据结果、图表或代码推导的架构图。

## 主题调研增强流程

当用户给的是一句话主题，而不是项目文件夹时，按下面做：

1. 判断它是否需要联网。
   - 画展、展览、活动、门票、地点、人物近况、公司、品牌、新闻、产品、趋势、公开数据，都要联网核验。
   - 用户明确给出的完整文章、报告或本地文件，可以先读本地材料；缺背景或需要最新信息时再联网。
2. 搜索顺序：
   - 官方网站、博物馆/画廊/主办方页面、艺术家/机构页面。
   - 权威媒体、新闻稿、出版社/数据库、百科或可信资料库。
   - 图片来源、海报、展品图、场馆图；记录来源和可用性。
3. 建立资料卡：
   - 主题名称、时间、地点、主办方/相关人物、核心看点、背景脉络、受众价值、关键图片/素材、引用来源。
4. 写 PPT 之前先区分：
   - 已确认事实
   - 多来源一致但非官方的信息
   - 只有单一来源的信息
   - 找不到来源、不能写死的信息
5. 生成 PPT 时把重点放在“故事线”上，不要把搜索结果堆成资料页。
6. 最终汇报要说明主要资料来源；如果某些关键信息无法核验，要明确写限制。

## 无文字背景增强流程

当用户要求“图片不要带字，后面我自己加文字”时，按下面做：

1. 每个背景图 prompt 都明确包含：

```text
16:9 presentation slide background, no text, no letters, no numbers,
no captions, no UI labels, no logo, no watermark, no signature,
clean empty space for editable text
```

2. 背景图只负责画面氛围、隐喻、项目场景、空间和视觉层次。
3. 所有标题、正文、标签、说明、页码都用 HTML 或 PPT 原生文字层添加。
4. 检查生成图，如果出现疑似文字、乱码字、logo 或水印，直接重生成，不要遮盖。
5. 需要 HTML 草稿时，用 `scripts/create_background_html.py` 生成每页图片作为 CSS background 的 HTML。
6. 需要 PPT 时，把背景图放在底层，文字框放在上层，保持可编辑。

## 验收标准

- 最终输出是有效 `.pptx`。
- 默认图片式 PPT 中，每页最终图片存在于 `origin_image/slide_XX.png`。
- 大纲、样张、风格、图片后端和整套生成都符合审批流程。
- `outline.md` 反映用户确认后的最终大纲。
- 需要讲稿时，`speech.md` 存在，并写入 PPT 备注区。
- 项目汇报 PPT 的故事基于真实项目证据，不虚构功能、指标或运行结果。
- 主题/画展/活动 PPT 的事实基于联网来源或用户提供材料；时间、地点、人物、展品、机构、数据等关键信息有来源支撑。
- 无文字背景模式下，背景图没有可读文字、字母、数字、logo、水印或签名；用户可见文字保持为 HTML/PPT 可编辑层。
- 必需素材被正确使用；如果无法使用，明确说明阻塞原因和证据路径。

## Reference Map

- `docs/workflow-gates-and-progress.md`：审批门、进度、完成证据。
- `docs/backend-selection.md`：图片后端选择和确认规则。
- `docs/outline-style-and-sample.md`：大纲、风格、样张规则和 prompt 示例。
- `docs/user-supplied-assets.md`：用户素材和必需图片处理规则。
- `docs/slide-generation-and-subagents.md`：任务、分发、结果记录、阻塞和后端来源。
- `docs/cli-api-fallback.md`：API/CLI fallback、生成/编辑命令和故障排查。
- `docs/image-model-configuration.md`：API key、base URL、模型名和 `.env` 配置。
- `docs/project-assembly-and-reporting.md`：项目目录、讲稿、组装和最终报告。
- `docs/style-library.md`：保存和复用风格。
- `docs/topic-web-research.md`：本地增强，一句话主题、画展、活动、人物、品牌等公开资料的联网调研流程。
- `docs/project-report-audit.md`：本地增强，项目识别和证据审计。
- `docs/project-visual-evidence.md`：本地增强，项目截图、运行照片和证明材料选择。
- `docs/textless-backgrounds-and-html.md`：本地增强，无文字背景图和 HTML/PPT 独立文字层。
- `prompts/slide-worker.md`：幻灯片子 agent 交接模板。
- `references/*.md`：视觉风格参考。

## 来源

主体流程来自 `ningzimu/codex-ppt-skill`，本地版本合入了项目识别、运行证据、联网主题调研和无文字背景 HTML 工作流。
