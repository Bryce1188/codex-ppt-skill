# 课程任务与项目的完整示例

这是一个可复现的演示案例。任务书是虚构示例，12 条成绩是人工构造数据，不对应真实学生；统计结果由附带代码实际计算。

- [assignment.md](assignment.md)：老师任务书示例，要求 6 页、约 5 分钟。
- [project/](project/)：CSV、统计代码、单元测试与计算结果。
- [presentation-plan.json](presentation-plan.json)：4 项要求与 6 页内容的对应。
- [deck.json](deck.json)：原生文字、图表、表格与讲稿的构建数据。

## 复现

在本示例目录运行：

```text
python project/analyze_scores.py project/scores.csv
python -m unittest discover -s project -p "test_*.py" -v
python ../../scripts/validate_plan.py presentation-plan.json
python ../../scripts/resolve_humanizer.py
```

使用宿主提供的 Node 与 `@oai/artifact-tool` 构建：

```text
node ../../scripts/build_editable_deck.mjs --spec deck.json --out work/course-report-draft.pptx --module-root <宿主node_modules目录> --preview-dir work/previews
python ../../scripts/validate_pptx.py work/course-report-draft.pptx --expected-slides 6 --require-text 1 2 3 4 5 6 --require-chart 4 --require-table 5 --require-notes 1 2 3 4 5 6
```

先检查 Microsoft YaHei 是否可用；换字体时更新 `fontFamily` 并重做排版检查。生成的是待检查稿，还需要按宿主流程校验、从最终 PPTX 渲染并逐页查看。前置 JSON 和结构检查不保证视觉效果。

新任务可对 Agent 说：

```text
用 codex-ppt-skill 读取 assignment.md 和 project/，重新做一份 6 页中文课程汇报。背景自动选，文字和图表可编辑，按规则自动使用 Humanizer。
```

`deck.json` 是这次实际示例的排版结果，不是要求所有项目套用的模板。用户选背景时，用同一份内容生成实际样页再等待选择。

## 背景与预览

封面采用内置 image_gen 实际生成的无文字背景，文字为独立原生文本。内容页使用原生图表与表格。[背景提示词](assets/cover-background-prompt.txt) 随示例保存。

需要复现三种配色预览时，在当前目录运行：

```text
node build-style-previews.mjs --module-root <宿主node_modules目录> --out work/styles
```

这三张样页使用相同数据，仅改变配色，便于比较可读性。

[验证范围与结果](verification.md)记录本次实际检查。可运行 `python ../../scripts/validate_assets.py asset-manifest.json --pptx <最终PPTX路径>` 核对封面原图嵌入。
