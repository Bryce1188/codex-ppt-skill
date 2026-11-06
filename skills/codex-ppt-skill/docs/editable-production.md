# 可编辑 PPTX 构建

## 使用条件

本目录的 `scripts/build_editable_deck.mjs` 使用宿主提供的 `@oai/artifact-tool`，不会自动安装依赖或调用收费 API。Codex 桌面中先查 workspace dependencies，使用返回的 Node 和 node_modules 路径。有宿主 presentations 技能时先读取它的实现与交付要求，包括操作标记、最终检查和渲染。

它是新建 PPTX 的构建器，支持原生文字、原生数据图表、原生表格和独立图片；不做复杂模板编辑、任意关系图、动画或 HTML 转 PPTX。需要这些能力时使用宿主相应 API，不要声称本构建器已支持。环境无 artifact-tool 时选择环境已有且用户允许的原生 PPTX 工具，或说明具体缺失，不能静默输出图片式文件替代编辑要求。

## 命令

```text
node scripts/build_editable_deck.mjs --spec deck.json --out work/draft.pptx --module-root <host-node_modules> --preview-dir work/previews
python scripts/validate_pptx.py work/draft.pptx --expected-slides 1 --require-text 1 --require-chart 1 --require-notes 1 --report work/qa.json
```

路径含空格时使用所属 shell 的正确引用。`--module-root` 在宿主可直接解析包时可省略。所有素材相对 JSON 所在目录解析；输出不得覆盖已有文件。生成的文件先是 draft，必须继续做宿主最终验证和逐页视觉检查。

## JSON 示例

完整可执行示例见 [editable-example.json](editable-example.json)。所有 geometry 与 `fontSize` 用 CSS px。数据集中在 `data`，图表/表格用 `dataKey` 引用，文本可用 `copy` + `textKey` 复用。背景可以是纯色；添加图片背景时把 image 放在 elements 第一项，再放独立文本。

- `fontFamily` 必填且应验证字体可用。
- `slideSize` 默认 1280×720；`expectedSlideCount` 可声明需要的总页数。
- `elements[].type` 为 `text`、`chart`、`table` 或 `image`。
- 每项 `position` 为 `left/top/width/height`，禁止不明原因出画布。
- 图表 `data` 使用 `categories` 与 `series[{name,values,fill}]`，类别与数值个数一致。图表 `options` 用宿主 artifact-tool 的真实参数，不能把数据偷偷放入 options。
- 表格 `data` 使用 `values` 矩阵，保持所有需要的行列。
- 图片需 `path` 和 `alt`；证据图写 `role: evidence` 并用 `contain`，不得强行拉伸或裁掉标签。
- `requireEditableText`、`requireNativeChart`、`requireNativeTable` 可声明页级要求；构建与最终包都应核对。
- `notes` 与 `sources` 写进对应页备注，来源是 URL 或可定位的本地材料说明。

先试最有代表性的内容页。导出后检查实际 PPTX 中的文字、chart/table 对象，再导入最终文件渲染。源数据与图的形状保持同步，不对图片中的图表做数据可编辑承诺。不要把浏览器 `contenteditable` 等同于 PPTX 原生文字，也不要把导出前预览等同于最终 PPTX 渲染。
