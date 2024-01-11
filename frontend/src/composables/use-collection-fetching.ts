import { handledClientSide, showError, useAsyncData } from "#imports"

import { ref, watch } from "vue"

import { useMediaStore } from "~/stores/media"

import { isClient } from "~/constants/window"

export const useCollectionFetching = async ({
  collectionId,
}: {
  collectionId: string
}) => {
  const mediaStore = useMediaStore()
  const page = ref(1)
  const handleLoadMore = () => {
    page.value += 1
  }

  const { pending, error } = await useAsyncData(
    collectionId,
    async () => {
      return await mediaStore.fetchMedia({ shouldPersistMedia: page.value > 1 })
    },
    { lazy: isClient, watch: [page] }
  )

  watch(error, () => {
    const err = mediaStore.fetchState.fetchingError
    if (err && !handledClientSide(err)) {
      showError({
        ...(err ?? {}),
        fatal: true,
      })
    }
  })
  return {
    pending,
    handleLoadMore,
  }
}
