# 软件项目汇报版式实例

四页独立虚构仓储方案，分别演示总体架构、一次业务流程、核心数据关系和设计取舍。文字、技术节点和附着连接线均为原生对象。示例没有实现代码、实测指标或用户项目资料。

## 示例设定

浏览器通过 Next.js 查询与修改库存，MySQL 保存数据，同一 Node.js 服务中的 Socket.IO 推送变更。一次变更先校验输入与权限，在同一事务中更新库存并写流水，提交后通知客户端刷新。仓库与商品组合唯一，库存关联变更流水。商品表和完整数据字典省略。选择流水方案的依据是追溯需求，没有性能提升数据。

## 生成与检查

在提供 artifact-tool 的宿主环境，从 skill 根目录执行：

```text
node scripts/design_profile.mjs --spec examples/software-report/deck.json
node scripts/build_editable_deck.mjs --spec examples/software-report/deck.json --out work/software-draft.pptx --module-root <host-node_modules> --preview-dir work/software-previews
node --test tests/test_editable_builder.mjs
```

生成后完成宿主最终包检查，再导入最终 PPTX 逐页渲染。README 展示图来自最终文件重新导入。示例共用 [项目汇报配置](../../references/design-profiles/project-report.json)，按角色继承字体、标题、底色和节点样式；修改主题时更新共享配置。

构图的选择与失败方式见 [版式实例](../../docs/layout-patterns.md)。这些布局可以调整，不是所有项目的固定四页。功能页应使用用户项目截图，按完整界面与局部放大组织，不能用虚构图推导功能已完成。
