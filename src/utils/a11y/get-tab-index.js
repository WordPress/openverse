/**
 * @see https://github.com/reakit/reakit/blob/f05d36daa6fbcc52c70cf2c71baea69025aa2402/packages/reakit/src/Tabbable/Tabbable.ts#L54
 * @param {boolean} trulyDisabled
 * @param {boolean} nativeTabbable
 * @param {boolean} supportsDisabled
 * @param {number} [htmlTabIndex]
 * @returns {number}
 */
export function getTabIndex(
  trulyDisabled,
  nativeTabbable,
  supportsDisabled,
  htmlTabIndex
) {
  if (trulyDisabled) {
    if (nativeTabbable && !supportsDisabled) {
      // Anchor, audio and video tags don't support the `disabled` attribute.
      // We must pass tabIndex={-1} so they don't receive focus on tab.
      return -1
    }
    // Elements that support the `disabled` attribute don't need tabIndex.
    return undefined
  }
  if (nativeTabbable) {
    // If the element is enabled and it's natively tabbable, we don't need to
    // specify a tabIndex attribute unless it's explicitly set by the user.
    return htmlTabIndex
  }
  // If the element is enabled and is not natively tabbable, we have to
  // fallback tabIndex={0}.
  return htmlTabIndex || 0
}
