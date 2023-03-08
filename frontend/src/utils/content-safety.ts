/**
 * Contains utilities related to content safety.
 */

import type { Media } from "~/types/media"
import { hash, rand as prng } from "~/utils/prng"
import { log } from "~/utils/console"

/**
 * Marks the given item as mature based on a random number seeded with the
 * item's UUID v4 identifier. The `frac` param controls the probability of an
 * item being marked as mature.
 *
 * @param item - the item to mark as mature
 * @param frac - the fraction of items to mark as mature
 */
export const markFakeSensitive = (item: Media, frac = 0.5) => {
  const random = prng(hash(item.id))()
  if (random < frac) {
    item.mature = true
    log("Fake mature", item.frontendMediaType, item.id)
  }
}
