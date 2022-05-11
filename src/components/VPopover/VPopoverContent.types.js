import { placements as popoverPlacements } from '@popperjs/core'

export const propTypes = {
  visible: {
    type: Boolean,
    required: true,
  },
  hide: {
    type: /** @type {import('@nuxtjs/composition-api').PropType<() => void>} */ (
      Function
    ),
    required: true,
  },
  hideOnEsc: {
    type: Boolean,
    default: true,
  },
  hideOnClickOutside: {
    type: Boolean,
    default: true,
  },
  autoFocusOnShow: {
    type: Boolean,
    default: true,
  },
  autoFocusOnHide: {
    type: Boolean,
    default: true,
  },
  triggerElement: {
    type: /** @type {import('@nuxtjs/composition-api').PropType<HTMLElement>} */ (
      process.server ? Object : HTMLElement
    ),
  },
  placement: {
    type: /** @type {import('@nuxtjs/composition-api').PropType<import('@popperjs/core').Placement>} */ (
      String
    ),
    default: 'bottom-end',
    validate: (v) => popoverPlacements.includes(v),
  },
  strategy: {
    type: /** @type {import('@nuxtjs/composition-api').PropType<import('@popperjs/core').PositioningStrategy>} */ (
      String
    ),
    default: 'absolute',
    // todo: Use the actual PositioningStrategy type instead of manually writing these values,
    // when this file is updated to TypeScript.
    validate: (v) => ['absolute', 'fixed'].includes(v),
  },
  zIndex: {
    type: Number,
  },
}

/** @typedef {import('@nuxtjs/composition-api').ExtractPropTypes<typeof propTypes>} Props */
