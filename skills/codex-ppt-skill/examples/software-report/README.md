# 软件项目汇报设计示例

本示例虚构一个仓储方案，用两页演示架构和数据库关系的原生可编辑排版，不代表任何用户项目已实现或测试成功。

示例设定：浏览器通过 Next.js 服务查询或更新库存，MySQL 保存数据，Socket.IO 推送库存变更通知。数据库核心子集为 warehouses、stocks、stock_moves；stocks 关联商品表 products，仓库与商品组合唯一，库存更新与流水记录处于同一事务。未附实现或性能数据。

## 生成与检查

在已提供 artifact-tool 的宿主环境，从 skill 根目录执行：

```text
node scripts/build_editable_deck.mjs --spec examples/software-report/deck.json --out work/software-draft.pptx --module-root <host-node_modules> --preview-dir work/software-previews
node --test tests/test_editable_builder.mjs
```

生成后按宿主流程完成最终包检查，导入最终 PPTX 并逐页渲染。仓库 README 的截图来自此示例最终文件的重新导入渲染。文字、节点和附着连接线是独立对象；移动节点后仍需检查独立文字和关系标签的位置。

功能页必须换成用户项目的真实截图，不能用此示例推导功能完成情况。软件汇报的素材、审计与视觉规则见 [软件项目汇报](../../docs/software-project-report.md)。
