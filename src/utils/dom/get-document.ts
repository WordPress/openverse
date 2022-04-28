/**
 * Returns `element.ownerDocument || document`.
 * From reakit-utils/getDocument
 */
export function getDocument(element: Element | Document | null): Document {
  return element ? element.ownerDocument || element : document
}
