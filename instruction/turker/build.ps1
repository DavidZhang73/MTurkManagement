pandoc instruction-turker.md `
-o instruction-turker.pdf `
--standalone `
--listings `
--number-sections `
--filter pandoc-crossref `
--template eisvogel `
--pdf-engine lualatex
