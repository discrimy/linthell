# linthell 🔥
Universal flakehell alternative that works with almost any linter you like.

## How it works
linthell identifies each linter error as 
`(<file path>, <code at specific line>, <error message>)`, so it keep track
of old errors even you add/delete some line from the same file. linthell
stores there triplets inside baseline file.

At setup phase, you generate baseline file which identifies old errors.
After that, linthell filters such errors and shows new only.

If you modify old code, then you should either fix these errors (refactor)
or regenerate baseline. The tool's philosophy is that baseline should 
be sharnk only, but how to deal with it is up to you.

## Usage
All examples are shown with `flake8`, edit them for you case.

At first generate baseline file for every linter you use:
```bash
flake8 . | linthell baseline -b baseline-flake8.txt -f <linter regex>
```

Then lint your project via `linthell`:
```bash
flake8 . | linthell lint -b baseline-flake8.txt -f <linter regex>
```

## Custom linter format
If you use another linter then you must provide custom regex string
string to parse it's output. Default format is `flake8` default format.
Some premade formats for linters:
- `flake8`: `(?P<path>[a-zA-Z0-9\._-]+(?:[\\/][a-zA-Z0-9\._-]+)*):(?P<line>\d+):\d+: (?P<message>[^\n]+)`
- `pydocstyle`: `(?P<path>[a-zA-Z0-9\._-]+(?:[\\/][a-zA-Z0-9\._-]+)*):(?P<line>\d+).+\n\s+(?P<message>[^\n]+)`
- `pylint`: `(?P<path>[a-zA-Z0-9\._-]+(?:[\\/][a-zA-Z0-9\._-]+)*):(?P<line>\d+):\d+: (?P<message>[^\n]+)`

### Create your own format regex
You can use your custom format regex. Suitable regex must
contains 3 named [python-like](https://docs.python.org/3/howto/regex.html#:~:text=The%20syntax%20for%20a%20named%20group%20is%20one%20of%20the%20Python%2Dspecific%20extensions%3A%20(%3FP%3Cname%3E...).%20name%20is%2C%20obviously%2C%20the%20name%20of%20the%20group) capturing groups: 
- `path` - relative file path 
- `line` - line number
- `message` - linter message

Your regex should matches all message related to an issue because 
unfiltered issues are printed by the whole match.

You can test your regex against linter output with [regexr](https://regexr.com/).

## pre-commit support
linthell can be used as [pre-commit](https://pre-commit.com/) hook. Tested with
flake8, pydocstyle, pylint, black linters.

## Config file
`linthell` can inject params from config file (`linthell --config path/to/config.ini`). 
`common` section applies for all commands, command specific config 
are specified by their name section, for example `[lint]`.
Nested commands are specified via dot. For example `linthell pre-commit lint`
reads config from `[pre-commit.lint]` section.

Keys must have same name as argument name of their command function. 
For example, `baseline_file` and `lint_format`.


## How to adapt linthell in project with pre-commit
1. Create linthell config:
```ini
[common]
baseline_file=baseline.txt
lint_format=(?P<path>[a-zA-Z0-9\._-]+(?:[\\/][a-zA-Z0-9\._-]+)*):(?P<line>\d+):\d+: (?P<message>[^\n]+)

[pre-commit.lint]
linter_command=flake8

[pre-commit.baseline]
linter_command=flake8
```
2. Create a linthell hook inside `.pre-commit-config.yaml` file:
```yaml
repos:
  - repo: local
    hooks:
      - id: linthell
        name: linthell flake8
        entry: linthell --config linthell.ini pre-commit lint
        language: system
        types: [python]
```
3. Generate baseline file based on pre-commit hook definition and linthell config:
```shell
linthell --config linthell.ini pre-commit baseline --hook-name "linthell flake8"
```
4. Validate new hook against generated baseline file
```shell
pre-commit run --all linthell
```