def get_version() -> str:
    """
    Get the version from graphy
    :return: the version of graphy
    """
    from graphy import __version__
    return __version__


def remove_duplicate_spaces(string: str) -> str:
    """
    Remove duplicate spaces from a string
    :param string: the string to remove the duplicate spaces from
    :return: a string with no double spaces.
    """
    return " ".join(string.split())
