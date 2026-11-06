# 公开方案调研与本版取舍

2026-11-06 阅读以下项目当前公开的技能入口与说明。比较的是可见流程和实现边界，不是基于下载量或星数的质量排名。未复制其受限代码、模板或指令段落。

| 方案 | 可借鉴的方法 | 在本 skill 中的应用 |
| --- | --- | --- |
| [Anthropic PPTX](https://github.com/anthropics/skills/blob/main/skills/pptx/SKILL.md) | 原生创建、模板编辑、内容提取与渲染检查各有工具 | 将可编辑对象检查和最终逐页视觉检查分开，不用图片预览证明编辑能力 |
| [baoyu-slide-deck](https://github.com/JimLiu/baoyu-skills/blob/main/skills/baoyu-slide-deck/SKILL.md) | 内容大纲、风格维度、参考图与逐页生成 | 根据题材选背景，用相同内容做候选样页；保留图片式路线的风格控制 |
| [ningzimu/codex-ppt-skill](https://github.com/ningzimu/codex-ppt-skill) | 整页生图、样页参照、图片装配与风格复用 | 保留原有 MIT 图片路线，同时让课程/项目默认使用可编辑文字与数据 |
| [GordenPPTSkill](https://github.com/GordenSun/GordenPPTSkill/blob/main/SKILL.md) | 先看实际模板预览，沿用布局、字体层级与用户模板 | 提供自动、预览后选择、自带背景三种路径；不打包其第三方模板 |

Anthropic 目录标注专有许可证；Gorden 的模板与 skill 标注非商业限制。这里只使用方法层面的比较，本仓库未引入这些内容。baoyu 的图片式阅读分享定位也不能直接代替课堂现场讲述的页数与节奏设计。

本版针对课程项目补充了任务要求、证据状态、页码与缺口的对应，以及 Humanizer 两轮润色。这些是独立编写的流程、定位器、验证器与示例。

Humanizer 来自 [Bryce1188/humanizer](https://github.com/Bryce1188/humanizer)，按 MIT 许可证保存固定快照及原版权声明，详见 [来源记录](../references/humanizer/provenance.json)。

可编辑构建器使用宿主 `@oai/artifact-tool`。此次样稿在 Codex 桌面提供的运行环境中构建和验证，不把该运行时当作普通 npm 环境的默认依赖。

原有 2026-09-08 调研还参考了 [Dashi PPT](https://github.com/chuspeeism/dashi-ppt-skill/blob/main/skills/dashi-ppt/SKILL.md) 的内容与布局分离方法，未移植其 AGPL 实现或编辑器。

## 提示词、交互与背景补充调研

检索日期：2026-11-06。下面是方法参考，内置中文提示词为独立编写，并非复制商业工具的内部 prompt。

| 来源 | 参考点 | 落地位置 |
| --- | --- | --- |
| [Gamma Agent](https://help.gamma.app/en/articles/15002203-how-do-i-create-with-agent-in-gamma) | 从一句话开始，按需澄清，计划/直接初稿两种节奏，支持局部修改 | intake-and-superpowers、start-here、deck-brief |
| [Gamma 图像风格](https://help.gamma.app/en/articles/11047204-how-can-i-customize-ai-image-styles) | 图像内容和风格分开，主题层保持一致 | background-design、background-selection |
| [Google 图像提示指南](https://developers.googleblog.com/en/how-to-prompt-gemini-2-5-flash-image-generation-for-the-best-results/) | 描述主体、场景、构图、材质与光线，用参考图和局部迭代 | background-design；只借鉴通用方法，不替换当前生图后端。该文发表于 2025-08-28，不是最新模型推荐 |
| [Assertion–Evidence](https://www.assertion-evidence.com/) | 技术结果页以简短信息和视觉证据组织 | ai-ppt-repair、页级计划；定义页和指定章节名不强制改成结论 |
| [Microsoft 演示建议](https://support.microsoft.com/en-us/powerpoint/tips-for-creating-and-delivering-an-effective-presentation) | 文字精简、远处可读、图表标签清楚、背景低干扰 | quality-assurance、ai-ppt-repair |
| [Microsoft 无障碍指南](https://support.microsoft.com/en-us/accessibility/powerpoint/make-your-powerpoint-presentations-accessible-to-people-with-disabilities) | 图片替代文字、颜色之外的提示、阅读顺序 | 原生图片 alt、人工视觉检查；未声称已自动检查全部阅读顺序 |
| [Superpowers](https://github.com/obra/superpowers) | 按安装版本读取需求、计划和完成验证规则 | resolve_superpowers.py、intake-and-superpowers |

本机 Superpowers 核对版本为 v6.3.0（commit b36e0829c6d0140e93cfef2ca599b1b07d4a7797）。公开安装可能不同，定位器返回实际路径与散列；未自动升级或打包其实现。

“减少 AI 味”指减少套话、重复布局、无依据的拔高和不真实的素材；不声称可以判定作者身份或保证绕过检测。
