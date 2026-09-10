/**
 * Shared URL-scheme guard for values rendered into anchor `href`/`to`
 * attributes. Both the raw-HTML attribution builder and the shared `VLink`
 * component route untrusted, provider-supplied URLs (e.g. `creator_url`,
 * `foreign_landing_url`) through this, so a single allow-list governs every
 * link sink.
 */

/**
 * Schemes permitted to appear in a rendered link. Anything else with an
 * explicit scheme (`javascript:`, `data:`, `vbscript:`, …) is neutralised.
 */
const ALLOWED_SCHEMES = ["http", "https", "mailto"]

/**
 * Drop URLs with a non-allow-listed scheme to `about:blank`, so a
 * `javascript:` or `data:` URL can't yield an executable link. Escaping the
 * attribute value does not stop these, as they contain nothing to escape.
 * Scheme-relative and relative URLs (no explicit scheme) are left untouched.
 *
 * @param href - the untrusted URL to sanitise
 * @returns the URL if its scheme is safe, otherwise `about:blank`
 */
export const sanitizeHref = (href: string): string => {
  // Strip the C0 controls and spaces a browser ignores when parsing, else `\x01javascript:` or `java\tscript:` evades the check but still runs.
  const stripped = Array.from(href)
    .filter((char) => (char.codePointAt(0) ?? 0) > 0x20)
    .join("")
  const scheme = stripped.match(/^([a-z][a-z0-9+.-]*):/i)
  if (scheme && !ALLOWED_SCHEMES.includes(scheme[1].toLowerCase())) {
    return "about:blank"
  }
  return href
}
