$ sed -n '5p;29p' README.md
[![version](https://img.shields.io/badge/version-v0.63.0-blue)](https://github.com/randomgitsrc/agateon)
   curl -sSL https://raw.githubusercontent.com/randomgitsrc/agateon/main/install.sh | bash

$ grep -nE 'randomgitsrc/agate\b' README.md
OLD_URL_GREP_EXIT: 1

$ grep -n 'randomgitsrc/agateon' README.md
5:[![version](https://img.shields.io/badge/version-v0.63.0-blue)](https://github.com/randomgitsrc/agateon)
29:   curl -sSL https://raw.githubusercontent.com/randomgitsrc/agateon/main/install.sh | bash
NEW_URL_GREP_EXIT: 0
