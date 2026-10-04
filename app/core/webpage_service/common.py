import logging
import tomllib
from pathlib import Path

import numpy as np

logger = logging.getLogger(__name__)


def parse_version():
    """Parses a .toml file for app version number"""

    TOML_PATH = Path("pyproject.toml")

    try:
        with open(TOML_PATH, "rb") as f:
            toml = tomllib.load(f)
            version = toml["project"]["version"]

        return version

    except (FileNotFoundError, OSError) as e:
        logger.warning(f"{e} in 'parse_version'")
        return "0.0.0"


VERSION = parse_version()


def softmax(input, axis=None):
    """An implementation of the softmax function"""

    x = np.array(input)
    e_x = np.exp(x - np.max(x, axis=axis, keepdims=True))
    return e_x / np.sum(e_x, axis=axis, keepdims=True)
