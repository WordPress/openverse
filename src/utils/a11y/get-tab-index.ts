/**
 * @see https://github.com/reakit/reakit/blob/f05d36daa6fbcc52c70cf2c71baea69025aa2402/packages/reakit/src/Tabbable/Tabbable.ts#L54
 * @param trulyDisabled - disabled and inaccessible when disabled
 * @param nativeTabbable - some elements are not natively tabbable
 * @param supportsDisabled - whether the element natively supports `disabled` attribute
 * @param htmlTabIndex - tabindex value in the HTML
 */
export function getTabIndex(
  trulyDisabled: boolean,
  nativeTabbable: boolean,
  supportsDisabled: boolean,
  htmlTabIndex?: number
): number | undefined {
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
    // If the element is enabled, and it's natively tabbable, we don't need to
    // specify a tabIndex attribute unless it's explicitly set by the user.
    return htmlTabIndex
  }
  // If the element is enabled and is not natively tabbable, we have to
  // fallback tabIndex={0}.
  return htmlTabIndex || 0
}
