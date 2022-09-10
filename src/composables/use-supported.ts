import { Ref, ref } from '@nuxtjs/composition-api'

import { tryOnMounted } from '~/utils/try-on-mounted'

export function useSupported(callback: () => unknown, sync = false) {
  const isSupported = ref() as Ref<boolean>

  const update = () => (isSupported.value = Boolean(callback()))

  update()

  tryOnMounted(update, sync)
  return isSupported
}
