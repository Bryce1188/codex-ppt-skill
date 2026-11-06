# 可编辑 PPTX 构建

## 使用条件

本目录的 `scripts/build_editable_deck.mjs` 使用宿主提供的 `@oai/artifact-tool`，不会自动安装依赖或调用收费 API。Codex 桌面中先查 workspace dependencies，使用返回的 Node 和 node_modules 路径。有宿主 presentations 技能时先读取它的实现与交付要求，包括操作标记、最终检查和渲染。

它是新建 PPTX 的构建器，支持原生文字、原生数据图表、原生表格、独立图片，以及由原生节点和附着连接线组成的简单技术图示；不做复杂模板编辑、自动图布局、任意关系图、动画或 HTML 转 PPTX。需要这些能力时使用宿主相应 API，不要声称本构建器已支持。环境无 artifact-tool 时选择环境已有且用户允许的原生 PPTX 工具，或说明具体缺失，不能静默输出图片式文件替代编辑要求。

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
- `elements[].type` 为 `text`、`chart`、`table`、`image` 或 `shape`。
- 每项 `position` 为 `left/top/width/height`，禁止不明原因出画布。
- 图表 `data` 使用 `categories` 与 `series[{name,values,fill}]`，类别与数值个数一致。图表 `options` 用宿主 artifact-tool 的真实参数，不能把数据偷偷放入 options。
- 表格 `data` 使用 `values` 矩阵，保持所有需要的行列。
- 图片需 `path` 和 `alt`；证据图写 `role: evidence` 并用 `contain`，不得强行拉伸或裁掉标签。
- `requireEditableText`、`requireNativeChart`、`requireNativeTable` 可声明页级要求；构建与最终包都应核对。
- `notes` 与 `sources` 写进对应页备注，来源是 URL 或可定位的本地材料说明。

先试最有代表性的内容页。导出后检查实际 PPTX 中的文字、chart/table 对象，再导入最终文件渲染。源数据与图的形状保持同步，不对图片中的图表做数据可编辑承诺。不要把浏览器 `contenteditable` 等同于 PPTX 原生文字，也不要把导出前预览等同于最终 PPTX 渲染。

## 可编辑技术图示与表格样式

`shape` 用于架构节点、ER 实体等技术证据，不用于拼装装饰插画。每个节点有唯一的 `id`，`geometry` 支持 `rect/roundRect/ellipse`，样式为 `fill/lineColor/lineWidth/lineStyle`。节点文字用独立 `text` 元素放入相同区域；`insets` 可设置文字内边距。

页面的 `connectors` 引用节点：

```json
{"from":"browser","to":"service","fromSide":"right","toSide":"left","kind":"straight","color":"#5B8276","width":2}
```

默认箭头指向 `to`，`arrow:false` 表示无向关系。连接类型支持 `straight/elbow`，锚点为 `left/right/top/bottom`；禁止不存在的端点和自身连接。标签用附近的原生文字表示。连接线附着节点，独立标签仍需随布局检查。不要根据 API 的 head/tail 名称猜方向：此构建器将箭头写在 tail，对最终导出方向做了检查。

表格支持 `borderColor/borderWidth`、`headerColor/bodyColor`、`headerFill/bodyFill`，以及 `cellPadding:{left,right,top,bottom}`（CSS px）。用浅细边框和合适内边距改善阅读，不通过压缩字体塞入整库字典。

宿主提供 artifact-tool 与 Python 时可运行：

```text
node --test tests/test_editable_builder.mjs
```

设置 `RUNTIME_NODE_MODULES` 指向宿主模块目录；`RUNTIME_PYTHON` 可指定 Python。该检查覆盖无效连接和最终 PPTX 的节点附着、箭头方向、原生表格与内边距。它不评判图示语义或视觉效果，也不属于无宿主运行时的 GitHub CI。
