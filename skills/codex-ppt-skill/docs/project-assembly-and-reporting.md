# 组装与交付

以用户指定输出目录为准；宿主有 work/outputs 约定时遵守它。来源、构建数据、prompt、状态、预览、QA 留在工作目录，最终 PPTX 和有用的预览单独存放。

## 可编辑 / 混合

按 [可编辑构建](editable-production.md) 导出 draft，再运行宿主最终检查与 [质量检查](quality-assurance.md)。背景与正文必须是不同对象。编辑要求要在最终文件中核对，不仅看源 HTML。

## 图片式

保留目录与脚本兼容性：`{base_dir}/{deck_name}/origin_image/slide_01.png`，可选 `speech.md`，以及实际运行需要的 `deck_spec.json`、`prompts/`、`slide_jobs.json`、`slide_run_state.json`。

```text
python scripts/assemble_ppt.py <base_dir> <deck_name>.pptx --aspect-ratio 16:9
```

只读取正式 slide_N 图片，序号从 1 连续递增，不允许重复编号。所有图片存在后才能装配。现有运行状态应无未处理的 pending/dispatched/blocked；内部样页使用普通结果记录，用户确认样页才可标为 accepted。不能把未处理页静默漏掉。

图片式素材与画布比例应匹配；不能靠拉伸解决变形。不用强压缩牺牲中文或论文图清晰度，查看组装后最终 PPTX 的渲染。

## 讲稿与来源

用户需要讲稿时，`speech.md` 以 `## Slide N: 标题` 分页，语言跟随演示内容。讲稿解释证据与上下文，不机械复述文字。具体长度由发言时间与内容决定。

调研来源写相关页备注，保留日期、单位与条件；影响判断的限制在页内可见。可编辑构建器直接支持每页 `notes` 和 `sources`。

## 交付

给出 PPTX 与有用的预览，说明模式和影响使用的限制，例如“文字和图表可编辑，背景图仍是图片”。只在实际打开目标应用后才说已做应用内测试。中间状态和日志不默认交付。
