/**
 * Replace characters in the string that have special meanings in HTML with
 * their HTML character entities to prevent injection.
 *
 * @param text {string} - the string to sanitise
 * @returns {string} the clean string that can be interpolated into HTML markup
 */
export const escapeHtml = (text) => {
  const charHtmlMap = {
    "'": "&apos;",
    '"': "&quot;",
    "<": "&lt;",
    ">": "&gt;",
    "&": "&amp;",
  }
  return text.replace(/[&"'<>]/g, (c) => charHtmlMap[c])
}
