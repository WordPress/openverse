# All possible letters that can appear in a shortened URL path
URL_ALPHABET = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
# Inverted index of the alphabet
ALPHABET_INDEX = {c: idx for idx, c in enumerate(URL_ALPHABET)}


def get_next_shortened_path(last_url):
    """
    Produce a short URL. Each URL is guaranteed to be the shortest possible
    path available.
    :param last_url: The last allocated URL.
    :return: A short URL path, such as '9abx'
    """

    def get_next_char(c):
        c_idx = ALPHABET_INDEX[c]
        next_char_idx = (c_idx + 1) % len(URL_ALPHABET)
        return URL_ALPHABET[next_char_idx]

    if last_url is None:
        return URL_ALPHABET[0]

    last_character = last_url[-1]
    next_character = get_next_char(last_character)

    temp_path = last_url
    if next_character == URL_ALPHABET[0]:
        # Iterate backwards to carry the last digit.
        carry = True
        idx = len(temp_path) - 1
        while idx >= 0 and carry:
            c = temp_path[idx]
            if c == URL_ALPHABET[-1]:
                if idx == 0:
                    # Overflowed; add a new digit
                    temp_path = temp_path + URL_ALPHABET[0]
            else:
                carry = False
            temp_path = temp_path[:idx] + get_next_char(c) + temp_path[idx + 1 :]
            idx -= 1
        next_path = temp_path
    else:
        # Increment the last digit.
        next_path = temp_path[:-1] + next_character
    return next_path
