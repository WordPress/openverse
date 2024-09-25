/**
 * Place k6 jslib imports into this module, between the eslint-disable lines.
 *
 * Declare minimum-viable type definitions for them in typings/jslib.d.ts
 * and follow existing examples there as a guide.
 *
 * Centralising the import of these modules prevents needing to scatter the
 * same eslint pragma throughout the k6 tests, and allows us to easily
 * document and encourage best practices, like declaring types for these modules.
 */

/* eslint-disable import/extensions, import/no-unresolved */
export {
  textSummary,
  type SummaryData,
} from "https://jslib.k6.io/k6-summary/0.1.0/index.js"
export { randomItem } from "https://jslib.k6.io/k6-utils/1.2.0/index.js"

/* eslint-enable import/extensions, import/no-unresolved */
