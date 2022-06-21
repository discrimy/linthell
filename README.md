# linthell 🔥
Universal flakehell alternative that works with almost any linter you like.

## Usage
All examples are shown with `flake8`, edit them for you case.

At first generate baseline file for every linter you use:
```bash
flake8 . | python linthell.py baseline -b baseline-flake8.txt -f <linter regex>
```

Then lint your project via `linthell`:
```bash
flake8 . | python linthell.py lint -b baseline-flake8.txt -f <linter regex>
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

Your regex should matchs all message related to an issue because 
unfiltered issues are printed by the whole match.

You can test your regex against linter output with [regexr](https://regexr.com/).