import { contains, getActiveElement, isFrame, isVisible } from "./dom"

const selector =
  "input:not([type='hidden']):not([disabled]), select:not([disabled]), " +
  "textarea:not([disabled]), a[href], button:not([disabled]), [tabindex], " +
  "iframe, object, embed, area[href], audio[controls], video[controls], " +
  "[contenteditable]:not([contenteditable='false'])"

function hasNegativeTabIndex(element: Element) {
  const tabIndex = parseInt(element.getAttribute("tabindex") || "0", 10)
  return tabIndex < 0
}

/**
 * Checks whether `element` is focusable or not.
 * @example
 * isFocusable(document.querySelector("input")); // true
 * isFocusable(document.querySelector("input[tabindex='-1']")); // true
 * isFocusable(document.querySelector("input[hidden]")); // false
 * isFocusable(document.querySelector("input:disabled")); // false
 */
export function isFocusable(element: Element): element is HTMLElement {
  return element.matches(selector) && isVisible(element)
}

/**
 * Checks whether `element` is tabbable or not.
 * @example
 * isTabbable(document.querySelector("input")); // true
 * isTabbable(document.querySelector("input[tabindex='-1']")); // false
 * isTabbable(document.querySelector("input[hidden]")); // false
 * isTabbable(document.querySelector("input:disabled")); // false
 */
export function isTabbableElement(element: Element): element is HTMLElement {
  return isFocusable(element) && !hasNegativeTabIndex(element)
}

export function isTabbable(element: Element): boolean {
  return isFocusable(element) && !hasNegativeTabIndex(element)
}

/**
 * Returns all the focusable elements in `container`.
 */
export function getAllFocusableIn(
  container: HTMLElement,
  includeContainer?: boolean
) {
  const elements = Array.from(container.querySelectorAll<HTMLElement>(selector))
  if (includeContainer) {
    elements.unshift(container)
  }

  const focusableElements = elements.filter(isFocusable)

  focusableElements.forEach((element, i) => {
    if (isFrame(element) && element.contentDocument) {
      const frameBody = element.contentDocument.body
      focusableElements.splice(i, 1, ...getAllFocusableIn(frameBody))
    }
  })

  return focusableElements
}

/**
 * Returns all the tabbable elements in `container`, including the container
 * itself.
 */
export function getAllTabbableIn(
  container: HTMLElement,
  includeContainer?: boolean,
  fallbackToFocusable?: boolean
) {
  const elements = Array.from(container.querySelectorAll<HTMLElement>(selector))

  const tabbableElements = elements.filter(isTabbableElement)

  if (includeContainer && isTabbableElement(container)) {
    tabbableElements.unshift(container)
  }

  tabbableElements.forEach((element, i) => {
    if (isFrame(element) && element.contentDocument) {
      const frameBody = element.contentDocument.body
      const allFrameTabbable = getAllTabbableIn(
        frameBody,
        false,
        fallbackToFocusable
      )
      tabbableElements.splice(i, 1, ...allFrameTabbable)
    }
  })

  if (!tabbableElements.length && fallbackToFocusable) {
    return elements
  }
  return tabbableElements
}

/**
 * Returns the first tabbable element in `container`, including the container
 * itself if it's tabbable.
 */
export function getFirstTabbableIn(
  container: HTMLElement,
  includeContainer?: boolean,
  fallbackToFocusable?: boolean
) {
  const [first] = getAllTabbableIn(
    container,
    includeContainer,
    fallbackToFocusable
  )

  return first || null
}

/**
 * Checks if `element` has focus. Elements that are referenced by
 * `aria-activedescendant` are also considered.
 * @example
 * hasFocus(document.getElementById("id"));
 */
export function hasFocus(element: Element) {
  const activeElement = getActiveElement(element)
  if (!activeElement) {return false}
  if (activeElement === element) {return true}
  const activeDescendant = activeElement.getAttribute("aria-activedescendant")
  if (!activeDescendant) {return false}
  return activeDescendant === element.id
}

/**
 * Checks if `element` has focus within. Elements that are referenced by
 * `aria-activedescendant` are also considered.
 * @example
 * hasFocusWithin(document.getElementById("id"));
 */
export function hasFocusWithin(element: Node | Element) {
  const activeElement = getActiveElement(element)
  if (!activeElement) {return false}
  if (contains(element, activeElement)) {return true}
  const activeDescendant = activeElement.getAttribute("aria-activedescendant")
  if (!activeDescendant) {return false}
  if (!("id" in element)) {return false}
  if (activeDescendant === element.id) {return true}
  return !!element.querySelector(`#${CSS.escape(activeDescendant)}`)
}

/**
 * Ensures `element` will receive focus if it's not already.
 * @example
 * ensureFocus(document.activeElement); // does nothing
 *
 * const element = document.querySelector("input");
 *
 * ensureFocus(element); // focuses element
 * ensureFocus(element, \{ preventScroll: true \}); // focuses element preventing scroll jump
 *
 * function isActive(el) \{
 *   return el.dataset.active === "true";
 * \}
 *
 * ensureFocus(document.querySelector("[data-active='true']"), \{ isActive \}); // does nothing
 *
 * @returns \{number\} `requestAnimationFrame` call ID so it can be passed to `cancelAnimationFrame` if needed.
 */
export function ensureFocus(
  el: Element,
  { preventScroll, isActive = hasFocus }: EnsureFocusOptions = {}
) {
  const element = el as HTMLElement
  // TODO: Try to use queueMicrotask before requestAnimationFrame and dispatch
  // focus events if the element is not focusable?
  if (isActive(element)) {return -1}
  element.focus({ preventScroll })
  if (isActive(element)) {return -1}
  return requestAnimationFrame(() => {
    if (isActive(element)) {return}
    element.focus({ preventScroll })
  })
}

type EnsureFocusOptions = FocusOptions & {
  isActive?: typeof hasFocus
}
