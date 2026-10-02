# AI 协作入口：thesis-format-fixer-demo

项目用途：DOCX 论文格式修复 demo、CLI 与 skill/plugin。

## 云端工作约定

1. 先读 `README.md`、本文件及目标目录的局部说明，再确认当前分支、工作区变化和任务范围。仓库文档与实际 manifest 不一致时以当前代码为准，并记录差异。
2. 不假设云端已有本机依赖、浏览器、全局 CLI、绝对路径或认证。按仓库锁文件和 manifest 安装；缺少能力时报告限制。
3. 用小范围分支和 PR 交付。PR 写清问题、修改、执行过的验证及仍待验证事项；文档存在不等于功能验证通过。
4. 保留无关工作区改动。修改公共接口时检查消费者，不顺手改部署配置或重构其他模块。
5. 密钥只从任务环境/secret 配置读取；日志脱敏。使用合成测试数据，不提交个人资料或运行输出。

## 项目地图

backend/app/、backend/tests/、samples/、skills/、plugins/、docs/。

## 环境与验证

Python >=3.11；python -m venv .venv；激活后 python -m pip install -e ".[dev]"。

```sh
python -m pytest backend/tests -q
python -m ruff check .
```

## 项目约束

LLM 只提结构标签，规则引擎决定修复；保持确定性计划和 pass/warn/fail 输出。只使用脱敏或合成论文；不要上传真实论文。skill/plugin 包装共享实现，改包装要检查两个入口。

## 云端验证边界

默认 heuristic + openxml 路径可离线测试；目录页码仍需 Word/兼容办公套件刷新。示例学校规则不等于学校审核认证。
