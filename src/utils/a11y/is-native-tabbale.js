/**
 * @see https://github.com/reakit/reakit/blob/f05d36daa6fbcc52c70cf2c71baea69025aa2402/packages/reakit/src/Tabbable/Tabbable.ts#L44
 * @param {Element} element
 * @returns {boolean}
 */
export function isNativeTabbable(element) {
  return ['BUTTON', 'INPUT', 'SELECT', 'TEXTAREA', 'A'].includes(
    element.tagName
  )
}
