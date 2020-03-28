from functools import partial


def dramatic_title(title):
    border = "=" * len(title)
    print(border)
    print(title)
    print(border)
    print()


spacious_print = partial(print, end="\n\n")
