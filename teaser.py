""" Teaser for telling 93 (Ninety-three) is a very special year!

~/anaceo/aggregates/python-titlecase contains the full fledged (complicated) version.
"""

def main():
  tc1 = TitleCase("Ninety-three Is a Special Year")
  print(f"Is '{tc1}' correct? {tc1.correct()}")
  tc2 = TitleCase("Ninety-three is a Special Year")
  print(f"Is '{tc2}' correct? {tc2.correct()}", repr(tc2.code_str()))


class TitleCase:
    """ TitleCase short class. """
    def __init__(self, astr, context="", name="TC"):
        self.name = name
        self._context, self._original = context, astr
        self._cached = (None, "")

    def string(self):
        return self._original
    
    def __str__(self):
        return self.string()

    def __repr__(self):
        return repr(self.string())

    def correct(self):
        """ Parse if necessary, and return True if it is correctly titled-case. """
        if self._cached[0] is None:
            self._cached = check_title_case(self._original)
        return self._cached[0]

    def code_str(self) -> str:
        if self._cached[0] is None:
            self._cached = check_title_case(self._original)
        return self._cached[1]


def check_title_case(title):
    """ Checks TitleCase independently.
    """
    # Standard lowercase words in titles
    minor_words = {
        'a', 'an', 'the', 'and', 'but', 'for', 'or', 'nor', 'in', 'on', 'at', 'to', 'from', 'by', 'with',
    }
    words = title.split()
    for i, word in enumerate(words):
        # Always capitalize the first and last word
        if i == 0 or i == len(words) - 1:
            if not word[0].isupper():
                return False, "F001"
        # Check if minor words are lowercase
        elif word.lower() in minor_words:
            if not word.islower():
                return False, "F002"
        # All other words should be capitalized
        else:
            if not word[0].isupper():
                return False, "F003"
    return True, ""


if __name__ == "__main__":
    main()
