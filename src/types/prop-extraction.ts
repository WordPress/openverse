import type {
  ExtractPropTypes,
  ExtractDefaultPropTypes,
} from '@nuxtjs/composition-api'

/**
 * Correctly extracts optional prop types.
 *
 * I think this is fixed in the Vue 3 types but hasn't been
 * ported back to `@vue/composition-api` so for now we have
 * to suffer this ugly type.
 */
export type ProperlyExtractPropTypes<P> = Omit<
  ExtractPropTypes<P>,
  keyof ExtractDefaultPropTypes<P>
> &
  Partial<ExtractDefaultPropTypes<P>>
