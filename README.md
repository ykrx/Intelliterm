# Intelliterm

> Chat with AI from your terminal!

> **Note**<br/>
> This is a side project I occasionally work on in my free time, [report](https://github.com/ykrx/Intelliterm/issues) any bugs and/or desired features. [Contributions are welcome!](#contributing)

## Features

-   **🧠 GPT-4** — Chat with any of [OpenAI's language models](https://platform.openai.com/docs/models)!
-   **👾 Code Execution** — Copy and run code [^1]
-   **⚙️ Configurations** — Quickly switch between models (mid-chat!) and manage multiple configurations
-   **📂 File Input** — Dump files into prompts!
-   **💬 Chat Manager** — Create, save [^2] and load chats!
-   **`!` Command Palette** — Do useful things with a variety of [built-in commands!](#-command-palette)
-   **✍️ Auto-completion** — Auto-complete commands with <kbd>tab</kbd> (and navigate history with <kbd>↑</kbd> / <kbd>↓</kbd>)

## Install

```shell
pip install intelliterm
```

## How to use

> **Note**<br/>
> Make sure you've set your `OPENAI_API_KEY` environment variable in `~/.zshrc` or `~/.bashrc`:
>
> ```shell
> export OPENAI_API_KEY='YOUR-API-KEY'
> ```

Basic usage:

```shell
ai

# or with a prompt
ai write a python program that prints a random chess position using emojis
```

Input a file:

```shell
ai -f file.py # -f or --file

# or via pipes
cat file.py | ai
git diff | ai
```

> **Note**<br/>
> Piping a **git diff** is a _special case_ for which Intelliterm one-shot generates a commit message in [conventional format](https://www.conventionalcommits.org/en/v1.0.0/), summarizing the diff (for better UX).

### Options

<table>
  <tr>
    <th>Short</th>
    <th>Long</th>
    <th>Description</th>
  </tr>
  <tr>
    <td><code>-f</code></td>
    <td><code>--file</code></td>
    <td>Pass a file as prompt</td>
  </tr>
  <tr>
    <td><code>-m</code></td>
    <td><code>--mini</code><br/><code>--oneshot</code></td>
    <td>Complete prompt without entering the Intelliterm CLI ("one-shot" usage)</td>
  </tr>
  <tr>
    <td><code>-c</code></td>
    <td><code>--copy</code></td>
    <td>Auto-copy entire response to clipboard</td>
  </tr>
  <tr>
    <td><code>-cc</code></td>
    <td><code>--copy-code</code></td>
    <td>Auto-copy code block to clipboard</td>
  </tr>
  <tr>
    <td><code>-h</code></td>
    <td><code>--help</code></td>
    <td>Show help message (this one)</td>
  </tr>
  <tr>
    <td><code>-v</code></td>
    <td><code>--version</code></td>
    <td>Show Intelliterm version</td>
  </tr>
</table>

## `!` Command Palette

> **Note**
> You must be in a chat to use **Command Palette** (start a chat via `ai` or `ai <prompt>`)

Intelliterm comes with a set of handy commands, triggered by entering `!` followed by:

<table>
  <tr>
    <th></th>
    <th>Command Aliases</th>
    <th>Command Options</th>
    <th>Command Description</th>
  </tr>
  <tr>
    <td>
      <strong>General</strong>
    </td>
    <td>
      <code>!help</code> <code>!h</code>
    </td>
    <td></td>
    <td>
      Show available commands
    </td>
  </tr>
  <tr>
    <td></td>
    <td>
      <code>!quit</code> <code>!q</code> <br/>
      or <kbd>Ctrl</kbd> + <kbd>c</kbd>
    </td>
    <td></td>
    <td>
      Quit Intelliterm
    </td>
  </tr>
  <tr>
    <td></td>
    <td>
      <code>!shell</code> <code>!os</code>
    </td>
    <td></td>
    <td>
      Run basic shell commands within Intelliterm<br/>
      <blockquote>
        <strong>usage:</strong> <code>!shell &lt;command&gt;</code>
        <br/><strong>example:</strong> <code>> !shell ls</code>
      </blockquote>
    </td>
  </tr>
  <tr>
    <td>
      <strong>Configuration</strong>
    </td>
    <td>
      <code>!cfg</code> <code>!use</code> <code>!config</code> <code>!switch</code>
    </td>
    <td>
      <code>edit</code> <code>reset</code>
    </td>
    <td>
      Manage Intelliterm configurations<br/>
      <blockquote>
        <code>!cfg</code> — Show active config<br/>
        <code>!cfg edit</code> — Edit configs file<br/>
        <code>!use &lt;name&gt;</code> — Switch to a config (case-<i>insensitive</i>)<br/>
        <blockquote>
          example: <code>!use gpt4</code>
        </blockquote>
      </blockquote>
      <blockquote>
        <code>!cfg reset</code> — Reset configs file to defaults (<code>GPT3</code> and <code>GPT4</code>, defaulting to <code>GPT3</code>)
      </blockquote>
    </td>
  </tr>
  <tr>
    <td>
      <strong>Chat</strong>
    </td>
    <td>
      <code>!new</code> <code>!n</code>
    </td>
    <td></td>
    <td>
      Start new chat / clear context
    </td>
  </tr>
  <tr>
    <td></td>
    <td>
      <code>!file</code> <code>!f</code>
    </td>
    <td></td>
    <td>
      Input a file as prompt<br/>
      <blockquote>
        <strong>usage:</strong> <code>!file &lt;path&gt; &lt;prompt&gt;</code>
        <br/><strong>example:</strong> <code>> !file file.py optimize this code</code>
      </blockquote>
    </td>
  </tr>
  <tr>
    <td></td>
    <td>
      <code>!info</code> <code>!i</code>
    </td>
    <td></td>
    <td>
      Show information about current chat
    </td>
  </tr>
  <tr>
    <td></td>
    <td>
      <code>!save</code> <code>!s</code>
    </td>
    <td></td>
    <td>
      Save chat (to: <code>&lt;DOCUMENTS_DIR&gt;/intelliterm/chats</code>
      </blockquote>
    </td>
  </tr>
  <tr>
    <td></td>
    <td>
      <code>!load</code> <code>!l</code>
    </td>
    <td></td>
    <td>Load chat</td>
  </tr>
  <tr>
    <td>
      <strong>Response</strong>
    </td>
    <td>
      <code>!copy</code> <code>!c</code>
    </td>
    <td>
      <code>code</code>
    </td>
    <td>
      Copy last response to clipboard<br/>
        <blockquote>
          <code>!copy</code> / <code>!c</code> — Copy all content<br/>
          <code>!copy code</code> / <code>!c code</code> — Copy code from content
        </blockquote>
        <blockquote>
          <strong>Note:</strong> to auto-copy every new response:<br/>
            <ol>
              <li>
                Quit Intelliterm (<code>!quit</code> / <code>!q</code> / <kbd>Ctrl</kbd> + <kbd>c</kbd>)
              </li>
              <li>
                Relaunch with:
                <ul>
                  <li>
                    <code>ai &lt;prompt&gt; --copy</code> or 
                  </li>
                   <li>
                    <code>ai &lt;prompt&gt; --copy code</code> 
                  </li>
                  <li>
                    <strong>Tip:</strong> <code>-c</code> (short alias)
              </li>
            </ul>
          </li>
        </ol>
      </blockquote>
    </td>
  </tr>
  <tr>
    <td></td>
    <td>
      <code>!run</code> <code>!r</code>
    </td>
    <td></td>
    <td>
      Run code block in last response<br/>
      <blockquote>
        <strong>Note:</strong> currently supports:<br/>
        <ul>
          <li>Python</li>
          <li>JavaScript</li>
          <li>TypeScript</li>
        </ul>
      </blockquote>
    </td>
  </tr>
</table>

## Contributing

Pull requests, suggestions and issue reports are _very welcome_ 👽

[^1]: Running generated code currently supported for **Python**, **JavaScript** and **TypeScript** code snippets.
[^2]: Intelliterm uses <a href="https://pypi.org/project/platformdirs">**platformdirs**</a> to determine the file paths where configurations and chats are saved to and loaded from. <code>CONFIG_DIR</code> and <code>DOCUMENTS_DIR</code> directory locations will thus vary based on your OS (Intelliterm displays them when saving/loading things).
