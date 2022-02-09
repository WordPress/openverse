import { v4 as uuidv4 } from 'uuid'

/**
 * @typedef UserState
 * @property {string | undefined} usageSessionId
 */

/**
 * @returns {UserState}
 */
export const state = () => ({
  /**
   * Default to `undefined` on the client and let client side
   * SSR state hydration pull the SSR generated ID into the client.
   * This way we avoid generating any spurious IDs on the client.
   */
  usageSessionId: process.server ? uuidv4() : undefined,
})
