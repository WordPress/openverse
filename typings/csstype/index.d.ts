// The import is necessary to augment the CSS type definitions,
// however eslint sees this import as unused.
// https://github.com/frenic/csstype#what-should-i-do-when-i-get-type-errors
// eslint-disable-next-line @typescript-eslint/no-unused-vars
import type * as CSS from 'csstype'
/**
 * To use CSS custom properties in a component that uses TypeScript, add them here.
 * See example in `VWaveform.vue`
 */
declare module 'csstype' {
  interface Properties {
    '--usable-height'?: string
    '--unusable-height'?: string
    '--progress-time-left'?: string
    '--seek-time-left'?: string
    '--popover-height'?: string
    '--link-col-height'?: number
  }
}
