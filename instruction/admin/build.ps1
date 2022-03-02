pandoc instruction-admin.md `
-o instruction-admin.pdf `
--standalone `
--listings `
--number-sections `
--filter pandoc-crossref `
--template eisvogel `
--pdf-engine lualatex
