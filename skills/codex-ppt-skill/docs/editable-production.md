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

## 共享设计与后续修改

新稿使用 designProfile 指向本次的设计配置。位置仍为 CSS px，文字/形状的 styleRole 引用配置角色；title 等角色可连位置一起继承，图表、表格与连接线自动继承对应样式。所有普通内页使用同一 content 背景。局部例外写 designException，并在最终预览核对；全局换配色/字级优先修改共享配置并更新版本。

可以先运行 node scripts/design_profile.mjs --spec deck.json 独立检查，不需要 artifact-tool。无 designProfile 的旧构建文件继续支持，但不能据此声称已受统一视觉配置约束。完整字段和风格保存方法见 [风格复用](style-library.md)。

交付修改源时包括 deck.json、copy/data、实际使用的设计配置和素材；用相对路径组织，不依赖作者电脑的绝对路径。不包含密钥、依赖目录或私有外部链接凭证。

- 改文字或数据：改对应 copy/data 或页面元素，保持其他页面与 profile 版本，然后另存导出。
- 改某页图片：替换独立 image，保留 contain 与原图来源，更新素材清单和散列。
- 全局改视觉：编辑一份共享 profile 并更新 version，检查所有页面。不要逐页手工改出不同字号或图示边框。
- 改已有外部 PPTX：先识别原生文字、图片、表格与图表，再用宿主支持的原生编辑方式修改，另存新稿。对导入后退化为图片的对象明确说明；不能把所有页面截成图冒充编辑。

PowerPoint/WPS 兼容性按实际检查记录：包结构、原生对象、宿主导入渲染、在目标应用打开与编辑是不同层次。只完成前三项时如实报告，不写“已通过 PowerPoint/WPS 编辑测试”。复杂母版、公式、动画和特殊字体仍需按目标应用逐项确认。用户只需基础可编辑 PPTX 时，不擅自加装另一套导出引擎。

## 原生图片裁切与局部放大

截图先核对真实格式与像素尺寸，不能仅按扩展名推断。`image.crop` 使用四边裁去的比例，字段为 `left/top/right/bottom`，均在 0 到 1 之间，每对相反边之和小于 1。像素区域 `(x,y,w,h)` 对原图 `(W,H)` 的比例为 `x/W, y/H, 1-(x+w)/W, 1-(y+h)/H`。

证据图保持 `fit: contain`。局部图需写 `cropReason`，说明放大目的、完整上下文所在页和裁切未改变的证据范围。原图仍作为图片对象嵌入，裁切写入 PPTX，可用编辑器恢复或调整；不要预先覆盖原图。构建器检查比例和理由，是否存在上下文、是否误导仍需人工核对。最终导入渲染检查按钮、标签和边缘，不能只看导出前预览。
