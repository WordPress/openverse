import { ref } from '@nuxtjs/composition-api'

/** @type {import('@nuxtjs/composition-api').Ref<HTMLAudioElement | undefined>} */
const obj = ref(undefined)

export function useActiveAudio() {
  return Object.freeze({ obj })
}
