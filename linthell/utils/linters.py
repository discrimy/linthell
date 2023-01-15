import shlex
import subprocess
from typing import Tuple
from typing_extensions import Literal


def run_linter_and_get_output(
    linter_command: str,
    files: Tuple[str, ...],
    linter_output: Literal['stdout', 'stderr'],
) -> str:
    linter_process = subprocess.run(
        [*shlex.split(linter_command), *files],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True,
        check=False,
    )
    if linter_output == 'stdout':
        output = linter_process.stdout
    else:
        output = linter_process.stderr
    return output
