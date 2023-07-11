/**
 * Contains utilities related to content safety.
 */

import { hash, rand as prng } from "~/utils/prng"
import { log } from "~/utils/console"
import {
  USER_REPORTED,
  PROVIDER_SUPPLIED,
  TEXT_FILTERED,
  Sensitivity,
} from "~/constants/content-safety"

/**
 * Marks the given item as mature based on a random number seeded with the
 * item's UUID v4 identifier. The `frac` param controls the probability of an
 * item being marked as mature.
 *
 * @param id - the ID of the item to mark as mature
 * @param frac - the fraction of items to mark as mature
 * @returns an array of strings representing the mature flags
 */
export const markFakeSensitive = (id: string, frac = 0.5): Sensitivity[] => {
  const random = prng(hash(id))()

  if (random > frac) {
    return []
  }

  const sensitivityMask = Math.floor((random * 7) / frac) + 1
  const sensitivity: Sensitivity[] = []
  if ((sensitivityMask & 4) !== 0) {
    sensitivity.push(USER_REPORTED)
  }
  if ((sensitivityMask & 2) !== 0) {
    sensitivity.push(PROVIDER_SUPPLIED)
  }
  if ((sensitivityMask & 1) !== 0) {
    sensitivity.push(TEXT_FILTERED)
  }

  log("Fake mature", id, sensitivity)
  return sensitivity
}
