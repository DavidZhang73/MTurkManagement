pandoc instruction-turker.md `
-o instruction-turker.pdf `
--standalone `
--listings `
--number-sections `
--template eisvogel `
--pdf-engine lualatex

pandoc instruction-turker.md `
-o instruction-turker.html `
--standalone

python ./post-process.py

prettier --write --loglevel silent ../../MTurkFrontend/index.html
