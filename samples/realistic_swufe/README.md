# SWUFE Realistic Anonymized Demo

这组样例来自本地真实“修改前 / 修改后”论文文件和西南财经大学研究生学位论文格式政策文件，但已经脱敏。

脱敏处理包括：

- 替换 Word XML 中的正文、页眉页脚、表格、元数据文本节点。
- 替换非页码/目录类字段指令中的文本。
- 替换外部链接目标。
- 替换图片和媒体二进制内容。
- 生成后用敏感词扫描做一次自检。

Files:

- `swufe_before_anonymized.docx`: format-preserving anonymized before sample.
- `swufe_after_anonymized.docx`: format-preserving anonymized after sample.
- `format_delta.json`: non-content formatting delta extracted from the two anonymized documents.
- `policy_rules_used.json`: policy-derived formatting rules encoded into `backend/app/rules/data/swufe_master.json`.

Regenerate:

```bash
python3.12 scripts/build_anonymized_real_demo.py \
  --before /path/to/before.docx \
  --after /path/to/after.docx \
  --policy /path/to/swufe-policy.doc
```
