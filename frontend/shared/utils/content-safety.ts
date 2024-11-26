/**
 * Contains utilities related to content safety.
 */

import {
  USER_REPORTED,
  PROVIDER_SUPPLIED,
  TEXT_FILTERED,
  Sensitivity,
} from "#shared/constants/content-safety"
import { hash, rand as prng } from "#shared/utils/prng"
import { log } from "~/utils/console"

/**
 * Get an array of randomly selected sensitive content flags for an item with
 * the given UUID v4 identifier. The `frac` param controls the probability of an
 * item having sensitivity flags.
 *
 * @param id - the ID of the item for which to calculate the flags
 * @param frac - the fraction of items to probabilistically flag
 * @returns an array of strings representing the sensitivity flags
 */
export const getFakeSensitivities = (id: string, frac = 0.5): Sensitivity[] => {
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

  log("Fake sensitive", id, sensitivity)
  return sensitivity
}
