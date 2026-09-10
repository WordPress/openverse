# Codespell Configuration : spellcheck pre-commit hook

The main codespell configuration lives in the root directory's
[`pyproject.toml`](https://github.com/WordPress/openverse/tree/main/pyproject.toml).
Because the `skip` configuration variable does not support TOML arrays, in order
to make the configured skip directories and files more readable and
maintainable, they are configured as arguments to the command. However,
codespell configuration also relies on a variety of special, individual files to
configure ignores and special words. Those files are contained in this directory
in order to avoid increasing the number of random configuration files in the
project root. Each file is described below and uses a `.txt` extension to
disambiguate format.

Most of these files support arbitrary lines used as comments. For the sake of
convention, these lines should be prefixed with `;;` to designate a comment as
opposed to a `#`. `;;` is used because it is not significant in any of the
languages or configuration files we use, and it is thus extremely unlikely to
cause a false-positive.

## Limitations

Be aware of the following codespell limitations:

- Case-sensitive corrections are not available:
  https://github.com/codespell-project/codespell/pull/1880

## `ignore_lines.txt`

[`ignore_lines.txt`](https://github.com/WordPress/openverse/tree/main/.codespell/ignore_words.txt)
is used to configure the following setting:

```
  -x FILE, --exclude-file FILE
                        ignore whole lines that match those in the file FILE. The lines in FILE should match the to-be-excluded lines exactly
```

Pay special attention to the format of this file. Each line of the file must
match the target line to ignore _exactly_. In other words, if a line has leading
whitespace, that whitespace must be included. For example, if we need to ignore
the last line of the following:

```yaml
jobs:
  steps:
    - name: amazing step
      with:
        misspelled-action-argment: hello world!!!!!
```

The line in `ignore_lines.txt` must include all eight of the leading whitespace
characters to ignore the misspelled action argument. The following will not
work:

```
misspelled-action-argment: hello world!!!!!
```

It must be:

```
        misspelled-action-argment: hello world!!!!!
```

When documenting ignored lines, please include an explanation and the targeted
filename.

## `ignore_words.txt`

[`ignore_words.txt`](https://github.com/WordPress/openverse/tree/main/.codespell/ignore_words.txt)
is used to configure the following setting:

```
  -I FILE, --ignore-words FILE
                        file that contains words that will be ignored by codespell. File must contain 1 word per line. Words are case sensitive based on how they are written in the dictionary file
```

Despite the fact that codespell does not match misspelled words
case-sensitively, the words in this file must match the dictionary case. For
example, codespell will complain that the common `afterAll` Jest hook function
name should be changed to `after all`. The relevant dictionary entry is
`afterall->after all`. Therefore, the ignore words file must read `afterall`,
not `afterAll`.

Codespell's dictionaries can be found here:
https://github.com/codespell-project/codespell/tree/master/codespell_lib/data.
