# Project Audit

Use this checklist to understand a project before writing the deck story.

## Source Order

Inspect in this order:

1. User prompt and any attached screenshots or project notes.
2. `README*`, `docs/`, reports, requirements, notebooks, and demo scripts.
3. Manifests: `package.json`, `pyproject.toml`, `requirements*.txt`, `pom.xml`, `build.gradle`, `Cargo.toml`, `go.mod`, `composer.json`, `Dockerfile`, `docker-compose*`.
4. Entry points: `src/`, `app/`, `pages/`, `components/`, `main.*`, `index.*`, `server.*`, `api/`, `routes/`, `notebooks/`.
5. Tests, sample data, deployment config, CI files, and generated outputs.

## Extract

Capture these facts with file evidence when possible:

- Project name and one-sentence purpose.
- Target users and the problem it solves.
- Main features and workflows.
- Technical architecture: frontend, backend, data layer, model/AI layer, integrations, deployment.
- Important algorithms, models, APIs, data sources, or design choices.
- Completed implementation evidence: tests, screenshots, generated outputs, logs, commits, demo pages.
- Differentiators: what is hard, novel, useful, polished, or worth presenting.
- Gaps and caveats: incomplete features, missing env vars, failed runs, placeholder content.

## Evidence Discipline

- Cite exact filenames in internal notes so the final story is traceable.
- Treat code as stronger evidence than aspirational README text.
- Treat screenshots from a running app as stronger evidence than mockups.
- Do not turn TODOs, commented-out code, or planned roadmap items into completed features.
- Record evidence as documented, implemented, verified, or missing. A plausible verb is not evidence. State exactly what was read or run and the remaining limit; do not call a planned feature supported.
- For teacher assignments, use assignment-to-deck.md to map every requested topic to evidence and final slide numbers.
- Inspect data_files from the scanner for actual CSV/JSON/table results. scan_limit_reached means more files may remain; it is not a full audit.

## Common Project Types

- Web/app project: emphasize user journey, screens, state/data flow, and deployment readiness.
- AI/data project: emphasize dataset, pipeline, model/method, evaluation, outputs, and limitations.
- Backend/API project: emphasize architecture, endpoints, data model, reliability, security, and integration proof.
- Hardware/IoT project: emphasize system diagram, sensor/control loop, demo evidence, and real-world constraints.
- Design/product prototype: emphasize user problem, information architecture, interaction flow, and visual proof.

## 本次对象包含代码与论文时

先读 [内容理解](source-understanding.md)。README 的目标、当前代码实现、论文中的作者结论和本项目实测分别记录，不用“源码更可靠”把不同问题混在一起。远程仓库的证据固定到实际 commit；关键 PDF 图表、公式和指标回到物理原页核对。
