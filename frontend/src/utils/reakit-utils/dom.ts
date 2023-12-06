/**
 * Returns `element.ownerDocument || document`.
 */
export function getDocument(node?: Node | null): Document {
  return node ? node.ownerDocument || (node as Document) : document
}

/**
 * Returns `element.ownerDocument.activeElement`.
 */
export function getActiveElement(
  node?: Node | null,
  activeDescendant = false
): HTMLElement | null {
  const { activeElement } = getDocument(node)
  if (!activeElement?.nodeName) {
    // In IE11, activeElement might be an empty object if we're interacting
    // with elements inside of an iframe.
    return null
  }
  if (isFrame(activeElement) && activeElement.contentDocument) {
    return getActiveElement(
      activeElement.contentDocument.body,
      activeDescendant
    )
  }
  if (activeDescendant) {
    const id = activeElement.getAttribute("aria-activedescendant")
    if (id) {
      const element = getDocument(activeElement).getElementById(id)
      if (element) {
        return element
      }
    }
  }
  return activeElement as HTMLElement | null
}

/**
 * Similar to `Element.prototype.contains`, but a little bit faster when
 * `element` is the same as `child`.
 * @example
 * contains(document.getElementById("parent"), document.getElementById("child"));
 */
export function contains(parent: Node, child: Node): boolean {
  return parent === child || parent.contains(child)
}

/**
 * Checks whether `element` is a frame element.
 */
export function isFrame(element: Element): element is HTMLIFrameElement {
  return element.tagName === "IFRAME"
}

/**
 * Checks if the element is visible or not.
 */
export function isVisible(element: Element) {
  const htmlElement = element as HTMLElement
  return (
    htmlElement.offsetWidth > 0 ||
    htmlElement.offsetHeight > 0 ||
    element.getClientRects().length > 0
  )
}

export function isInDocument(target: Element) {
  const document = getDocument(target)
  if (target.tagName === "HTML") {
    return true
  }
  return contains(document.body, target)
}
