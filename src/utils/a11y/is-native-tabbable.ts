/**
 * @see https://github.com/reakit/reakit/blob/f05d36daa6fbcc52c70cf2c71baea69025aa2402/packages/reakit/src/Tabbable/Tabbable.ts#L44
 */
export function isNativeTabbable(element: Element) {
  return ['BUTTON', 'INPUT', 'SELECT', 'TEXTAREA', 'A'].includes(
    element.tagName
  )
}
