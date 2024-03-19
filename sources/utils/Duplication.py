"""
    Utility functions to handle duplication and deduplications.
"""


def remove_duplicated_lines(text):
    """
        Removes duplicated lines from a multi-line string.
    """
    lines = text.split('\n')
    unique_lines = set(lines)
    cleaned_text = '\n'.join(unique_lines)
    return cleaned_text
