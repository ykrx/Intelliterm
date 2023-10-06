# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['intelliterm']

package_data = \
{'': ['*']}

install_requires = \
['emoji>=2.8.0,<3.0.0',
 'openai>=0.27.8,<0.28.0',
 'pick>=2.2.0,<3.0.0',
 'platformdirs>=3.8.0,<4.0.0',
 'prompt-toolkit>=3.0.38,<4.0.0',
 'pygments>=2.15.1,<3.0.0',
 'pyperclip>=1.8.2,<2.0.0',
 'rich>=13.4.2,<14.0.0',
 'setuptools>=68.0.0,<69.0.0',
 'tiktoken>=0.4.0,<0.5.0']

entry_points = \
{'console_scripts': ['ai = intelliterm.main:run',
                     'intelliterm = intelliterm.main:run']}

setup_kwargs = {
    'name': 'intelliterm',
    'version': '0.3.0',
    'description': 'Chat with AI from your terminal!',
    'long_description': '# Intelliterm\n\n> Chat with AI from your terminal!\n\n> **Note**<br/>\n> This is a side project I occasionally work on in my free time, there are bound to be bugs and/or missing features. [Contributions are welcome!](#contributing)\n\n## Features\n\n-   **🧠 GPT-4** — Chat with any of [OpenAI\'s language models](https://platform.openai.com/docs/models)!\n-   **👾 Code Execution** — Copy and run code [^1]\n-   **⚙️ Configurations** — Quickly switch between models (mid-chat!) and manage multiple configurations\n-   **📂 File Input** — Dump files into prompts!\n-   **💬 Chat Manager** — Create, save [^2] and load chats!\n-   **`!` Command Palette** — Do useful things with a variety of [built-in commands!](#-command-palette)\n-   **✍️ Auto-completion** — Auto-complete commands with <kbd>tab</kbd> (and navigate history with <kbd>↑</kbd> / <kbd>↓</kbd>)\n\n## Install\n\n```shell\npip install intelliterm\n```\n\n## How to use\n\n> **Note**<br/>\n> Make sure you\'ve set your `OPENAI_API_KEY` environment variable in `~/.zshrc` or `~/.bashrc`:\n>\n> ```shell\n> export OPENAI_API_KEY=\'YOUR-API-KEY\'\n> ```\n\nBasic usage:\n\n```shell\nai\n\n# or with a prompt\nai write a python program that prints a random chess position using emojis\n```\n\nInput a file:\n\n```shell\nai -f file.py # -f or --file\n\n# or via pipes\ncat file.py | ai\ngit diff | ai\n```\n\n> **Note**<br/>\n> Piping a **git diff** is a _special case_ for which Intelliterm one-shot generates a commit message in [conventional format](https://www.conventionalcommits.org/en/v1.0.0/), summarizing the diff (for better UX).\n\n### Options\n\n<table>\n  <tr>\n    <th>Short</th>\n    <th>Long</th>\n    <th>Description</th>\n  </tr>\n  <tr>\n    <td><code>-f</code></td>\n    <td><code>--file</code></td>\n    <td>Pass a file as prompt</td>\n  </tr>\n  <tr>\n    <td><code>-m</code></td>\n    <td><code>--mini</code><br/><code>--oneshot</code></td>\n    <td>Complete prompt without entering the Intelliterm CLI ("one-shot" usage)</td>\n  </tr>\n  <tr>\n    <td><code>-c</code></td>\n    <td><code>--copy</code></td>\n    <td>Auto-copy entire response to clipboard</td>\n  </tr>\n  <tr>\n    <td><code>-cc</code></td>\n    <td><code>--copy-code</code></td>\n    <td>Auto-copy code block to clipboard</td>\n  </tr>\n  <tr>\n    <td><code>-h</code></td>\n    <td><code>--help</code></td>\n    <td>Show help message (this one)</td>\n  </tr>\n  <tr>\n    <td><code>-v</code></td>\n    <td><code>--version</code></td>\n    <td>Show Intelliterm version</td>\n  </tr>\n</table>\n\n## `!` Command Palette\n\n> **Note**\n> You must be in a chat to use **Command Palette** (start a chat via `ai` or `ai <prompt>`)\n\nIntelliterm comes with a set of handy commands, triggered by entering `!` followed by:\n\n<table>\n  <tr>\n    <th></th>\n    <th>Command Aliases</th>\n    <th>Command Options</th>\n    <th>Command Description</th>\n  </tr>\n  <tr>\n    <td>\n      <strong>General</strong>\n    </td>\n    <td>\n      <code>!help</code> <code>!h</code>\n    </td>\n    <td></td>\n    <td>\n      Show available commands\n    </td>\n  </tr>\n  <tr>\n    <td></td>\n    <td>\n      <code>!quit</code> <code>!q</code> <br/>\n      or <kbd>Ctrl</kbd> + <kbd>c</kbd>\n    </td>\n    <td></td>\n    <td>\n      Quit Intelliterm\n    </td>\n  </tr>\n  <tr>\n    <td></td>\n    <td>\n      <code>!shell</code> <code>!os</code>\n    </td>\n    <td></td>\n    <td>\n      Run basic shell commands within Intelliterm<br/>\n      <blockquote>\n        <strong>usage:</strong> <code>!shell &lt;command&gt;</code>\n        <br/><strong>example:</strong> <code>> !shell ls</code>\n      </blockquote>\n    </td>\n  </tr>\n  <tr>\n    <td>\n      <strong>Configuration</strong>\n    </td>\n    <td>\n      <code>!cfg</code> <code>!use</code> <code>!config</code> <code>!switch</code>\n    </td>\n    <td>\n      <code>edit</code> <code>reset</code>\n    </td>\n    <td>\n      Manage Intelliterm configurations<br/>\n      <blockquote>\n        <code>!cfg</code> — Show active config<br/>\n        <code>!cfg edit</code> — Edit configs file<br/>\n        <code>!use &lt;name&gt;</code> — Switch to a config (case-<i>insensitive</i>)<br/>\n        <blockquote>\n          example: <code>!use gpt4</code>\n        </blockquote>\n      </blockquote>\n      <blockquote>\n        <code>!cfg reset</code> — Reset configs file to defaults (<code>GPT3</code> and <code>GPT4</code>, defaulting to <code>GPT3</code>)\n      </blockquote>\n    </td>\n  </tr>\n  <tr>\n    <td>\n      <strong>Chat</strong>\n    </td>\n    <td>\n      <code>!new</code> <code>!n</code>\n    </td>\n    <td></td>\n    <td>\n      Start new chat / clear context\n    </td>\n  </tr>\n  <tr>\n    <td></td>\n    <td>\n      <code>!file</code> <code>!f</code>\n    </td>\n    <td></td>\n    <td>\n      Input a file as prompt<br/>\n      <blockquote>\n        <strong>usage:</strong> <code>!file &lt;path&gt; &lt;prompt&gt;</code>\n        <br/><strong>example:</strong> <code>> !file file.py optimize this code</code>\n      </blockquote>\n    </td>\n  </tr>\n  <tr>\n    <td></td>\n    <td>\n      <code>!info</code> <code>!i</code>\n    </td>\n    <td></td>\n    <td>\n      Show information about current chat\n    </td>\n  </tr>\n  <tr>\n    <td></td>\n    <td>\n      <code>!save</code> <code>!s</code>\n    </td>\n    <td></td>\n    <td>\n      Save chat (to: <code>&lt;DOCUMENTS_DIR&gt;/intelliterm/chats</code>\n      </blockquote>\n    </td>\n  </tr>\n  <tr>\n    <td></td>\n    <td>\n      <code>!load</code> <code>!l</code>\n    </td>\n    <td></td>\n    <td>Load chat</td>\n  </tr>\n  <tr>\n    <td>\n      <strong>Response</strong>\n    </td>\n    <td>\n      <code>!copy</code> <code>!c</code>\n    </td>\n    <td>\n      <code>code</code>\n    </td>\n    <td>\n      Copy last response to clipboard<br/>\n        <blockquote>\n          <code>!copy</code> / <code>!c</code> — Copy all content<br/>\n          <code>!copy code</code> / <code>!c code</code> — Copy code from content\n        </blockquote>\n        <blockquote>\n          <strong>Note:</strong> to auto-copy every new response:<br/>\n            <ol>\n              <li>\n                Quit Intelliterm (<code>!quit</code> / <code>!q</code> / <kbd>Ctrl</kbd> + <kbd>c</kbd>)\n              </li>\n              <li>\n                Relaunch with:\n                <ul>\n                  <li>\n                    <code>ai &lt;prompt&gt; --copy</code> or \n                  </li>\n                   <li>\n                    <code>ai &lt;prompt&gt; --copy code</code> \n                  </li>\n                  <li>\n                    <strong>Tip:</strong> <code>-c</code> (short alias)\n              </li>\n            </ul>\n          </li>\n        </ol>\n      </blockquote>\n    </td>\n  </tr>\n  <tr>\n    <td></td>\n    <td>\n      <code>!run</code> <code>!r</code>\n    </td>\n    <td></td>\n    <td>\n      Run code block in last response<br/>\n      <blockquote>\n        <strong>Note:</strong> currently supports:<br/>\n        <ul>\n          <li>Python</li>\n          <li>JavaScript</li>\n          <li>TypeScript</li>\n        </ul>\n      </blockquote>\n    </td>\n  </tr>\n</table>\n\n## Contributing\n\nPull requests, suggestions and issue reports are _very welcome_ 👽\n\n[^1]: Running generated code currently supported for **Python**, **JavaScript** and **TypeScript** code snippets.\n[^2]: Intelliterm uses <a href="https://pypi.org/project/platformdirs">**platformdirs**</a> to determine the file paths where configurations and chats are saved to and loaded from. <code>CONFIG_DIR</code> and <code>DOCUMENTS_DIR</code> directory locations will thus vary based on your OS (Intelliterm displays them when saving/loading things).\n',
    'author': 'Yulian Kraynyak',
    'author_email': 'yulian@yulian.codes',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/ykrx/intelliterm',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.11,<4.0',
}


setup(**setup_kwargs)

