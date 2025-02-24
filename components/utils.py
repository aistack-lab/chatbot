from collections.abc import Callable
import sys
from typing import Any

from streamlit import runtime
from streamlit.web.cli import main


def run(fn: Callable[..., Any]):
    if runtime.exists():
        fn()
    else:
        sys.argv = ["streamlit", "run", sys.argv[0]]
        sys.exit(main())
