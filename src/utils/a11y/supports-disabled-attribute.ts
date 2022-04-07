/**
 * @see https://github.com/reakit/reakit/blob/f05d36daa6fbcc52c70cf2c71baea69025aa2402/packages/reakit/src/Tabbable/Tabbable.ts#L50
 */
export function supportsDisabledAttribute(element: Element) {
  return ['BUTTON', 'INPUT', 'SELECT', 'TEXTAREA'].includes(element.tagName)
}
