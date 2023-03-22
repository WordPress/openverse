import { ref } from "vue"

/**
 * This global ref is SSR safe because it will only
 * change internal value based on client side interaction.
 */
const obj = ref<HTMLAudioElement | undefined>(undefined)

export function useActiveAudio() {
  return Object.freeze({ obj })
}
