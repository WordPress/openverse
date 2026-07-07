/**
 * Matches a URL first-segment that looks like a locale code: two letters,
 * optionally followed by a hyphenated region (e.g. `cn`, `es-ar`).
 */
const LOCALE_LIKE = /^[a-z]{2}(-[a-z]{2,4})?$/i

/**
 * Given a path and the set of supported locale codes, decide whether the path
 * starts with an *unsupported* locale-shaped prefix (e.g. `/cn`) and, if so,
 * return the path with that prefix stripped. Since the default locale is
 * English, the stripped path is the English equivalent of the original path.
 *
 * Returns `null` when the path should be left alone (not locale-shaped, or the
 * prefix is a supported locale).
 *
 * @param path - the incoming path, e.g. `/cn/search`.
 * @param supportedCodes - configured locale codes, e.g. `["en", "es"]`.
 */
export function getUnsupportedLocaleRedirect(
  path: string,
  supportedCodes: string[]
): string | null {
  const firstSegment = path.split("/")[1] ?? ""

  if (!LOCALE_LIKE.test(firstSegment)) {
    return null
  }
  if (supportedCodes.includes(firstSegment)) {
    return null
  }

  const rest = path.slice(firstSegment.length + 1) // drop "/xx"
  return rest || "/"
}
