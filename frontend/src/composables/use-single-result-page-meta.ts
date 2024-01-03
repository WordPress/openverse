import { computed, ref , watch } from "vue"


import type { AudioDetail, ImageDetail } from "~/types/media"

import { useI18n } from "~/composables/use-i18n"
import { createDetailPageMeta } from "~/utils/og"

import type { Ref } from "vue"

export const useSingleResultPageMeta = (
  media: Ref<AudioDetail | ImageDetail | null>
) => {
  const i18n = useI18n()

  const titles = () => {
    if (!media.value) {
      return { genericTitle: "", sensitiveTitle: "" }
    }
    return {
      genericTitle: `${i18n.t(
        `mediaDetails.reuse.${media.value.frontendMediaType}`
      )}`,
      sensitiveTitle: `${i18n.t(
        `sensitiveContent.title.${media.value.frontendMediaType}`
      )}`,
    }
  }

  const isSensitive = computed(() => media.value?.isSensitive ?? false)

  // Do not show sensitive content title in the social preview cards.
  const getMediaTitle = () => {
    if (!media.value) {
      return ""
    }
    return isSensitive.value
      ? titles().sensitiveTitle
      : media.value.title ?? titles().genericTitle
  }
  const getPageTitle = () => `${getMediaTitle()} | Openverse`

  const pageTitle = ref(getPageTitle())
  const detailPageMeta = createDetailPageMeta({
    title: getMediaTitle(),
    thumbnail: media.value?.thumbnail,
    isSensitive: isSensitive.value,
  })
  watch(media, () => {
    pageTitle.value = getPageTitle()
  })

  return {
    pageTitle,
    detailPageMeta,
  }
}
