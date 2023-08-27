from typing import Any, List, Mapping, Optional, Tuple

import click


class Mutex(click.Option):
    """Option subclass which can block usage of other options.

    Such options are listed in 'not_required_if'.
    """

    def __init__(self, *args: Any, **kwargs: Any):  # noqa: D107
        not_required_if: Optional[List[str]] = kwargs.pop("not_required_if")
        assert not_required_if, "'not_required_if' parameter required"
        self.not_required_if = not_required_if

        kwargs["help"] = (
            kwargs.get("help", "")
            + " Option is mutually exclusive with "
            + ", ".join(self.not_required_if)
            + "."
        ).strip()
        super(Mutex, self).__init__(*args, **kwargs)

    def handle_parse_result(
        self, ctx: click.Context, opts: Mapping[str, Any], args: List[str]
    ) -> Tuple[Any, List[str]]:  # noqa: D102
        current_opt: bool = self.name in opts
        for mutex_opt in self.not_required_if:
            if mutex_opt in opts:
                if current_opt:
                    raise click.UsageError(
                        "Illegal usage: '"
                        + str(self.name)
                        + "' is mutually exclusive with "
                        + str(mutex_opt)
                        + "."
                    )
                else:
                    self.prompt = None
        return super(Mutex, self).handle_parse_result(ctx, opts, args)
