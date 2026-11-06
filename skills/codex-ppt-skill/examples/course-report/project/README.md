# 课程成绩分析工具（演示项目）

输入 CSV 中的匿名编号与分数，输出人数、平均分、及格人数、及格率与分数段人数。及格线为 60 分，合法范围为 0–100 分。

scores.csv 中的 12 条记录全部是人工构造的演示数据，不对应真实学生。工具只做统计，没有用户界面、登录、数据库或真实学校接入。

运行：`python analyze_scores.py scores.csv`。测试：`python -m unittest discover -s . -p "test_*.py"`。

results.json 由该命令实际生成。样本用于演示数据流与 PPT 构建，不能据此推断教学质量或班级总体表现。
