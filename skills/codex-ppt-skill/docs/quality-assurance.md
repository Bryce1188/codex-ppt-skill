# 最终质量检查

## 内容检查入口

先核对 `presentation-plan.json` 的每项要求是否出现在最终页中，缺口是否在正文可见。按 [Humanizer 接入](humanizer-integration.md) 对最终提取文字和讲稿做第二轮润色；有修改时重新导出并检查对应页。计划验证器只能检查结构关联，不能证明文字真实或任务全部完成。

## 三类证据

1. **内容与数据**：提取最终 PPTX 的文字，核对请求覆盖、页数、事实、单位、比例、图表数据和引用。给定模板检查遗留占位文案；真实数据不能仅凭数字看起来合理就通过。
2. **文件与对象**：运行 `scripts/validate_pptx.py` 检查 ZIP/XML、内部关系、页序与声明的原生文字/图表/表格/备注。运行宿主更完整的 PPTX 验证器（可用时）。图片页不能标成原生可编辑。
3. **实际渲染**：从最终 PPTX 渲染每页，逐页全尺寸查看中文断行、截断、重叠、标签、留白、图像裁切及字体。缩略总览只用于整套节奏，不替代单页检查。

```text
python scripts/validate_pptx.py final.pptx --expected-slides 6 --require-text 1 2 3 4 5 6 --require-chart 3 --require-table 5 --report work/qa.json
```

该脚本是只读结构检查，不能检测所有文字溢出、图表算术、旋转/组合对象越界或 PowerPoint/WPS 兼容性。`passed: true` 仅表示声明的结构检查通过。warnings 需要结合页面意图检查，不能机械修掉设计性出血。

渲染环境优先使用宿主提供的工具。在 Codex 桌面里，如使用 LibreOffice，只用 workspace dependencies 返回的 bundled 路径，不用用户桌面安装的版本；没有对应路径就选其他已有渲染器或说明未验证项目。未打开 PowerPoint/WPS，不要声称“在 PowerPoint/WPS 实测通过”。

修复后重新生成发生变化的产物，重新检查变更页及整套一致性。不存在的问题不用为了凑 QA 次数强行修改。无法消除的使用限制必须说明，但不把工具日志放进业务幻灯片。
