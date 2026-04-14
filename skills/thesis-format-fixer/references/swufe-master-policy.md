# SWUFE Master Policy Notes

Source: `附件8西南财经大学关于研究生学位论文形式与格式的基本要求.doc`.

Encoded profile: `swufe_master`.

Key encoded rules:

- Paper: A4.
- Body: 宋体，小4号, multiple line spacing 1.37.
- Margins: top 3.9cm, bottom 3.4cm, left 3.45cm, right 3.45cm.
- Header/footer distance: header 2.8cm, footer 2.5cm.
- Heading 1: 2号小标宋, centered.
- Heading 2: 小3号黑体.
- Heading 3: 小4号黑体.
- Figure/table captions: 5号; table title 黑体, table body 宋体; table note 小5号宋体.

Current engine behavior:

- Sets margins and header/footer distance with Open XML.
- Ensures footer PAGE field.
- Adds page-number restart metadata.
- Adds next-page section break before detected level-1 headings.
- Marks TOC field dirty so Word can refresh it when opened.
