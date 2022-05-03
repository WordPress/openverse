/**
 * A module exporting KeyboardEvent['key'] codes as constants.
 *
 * This is incomplete and based purely on the current usage of
 * the application, so if you come across a new one that is
 * needed just add it.
 *
 * This mostly exists to avoid having to look at the MDN page
 * everytime you need to look up a keycode, especially for easy
 * to forget ones like Spacebar, while also removing "magic strings".
 */

export const keycodes = Object.freeze({
  Spacebar: ' ',
  Home: 'Home',
  End: 'End',
  ArrowUp: 'ArrowUp',
  ArrowDown: 'ArrowDown',
  ArrowLeft: 'ArrowLeft',
  ArrowRight: 'ArrowRight',
  Escape: 'Escape',
  PageUp: 'PageUp',
  PageDown: 'PageDown',
  Tab: 'Tab',
  Enter: 'Enter',
} as const)
