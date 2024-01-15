import { useI18n } from "#imports"

import { computed, ref, watch } from "vue"

import { createDetailPageMeta } from "~/utils/og"

import type { AudioDetail, ImageDetail } from "~/types/media"

import type { Ref } from "vue"

export const useSingleResultPageMeta = (
  media: Ref<AudioDetail | ImageDetail | null>
) => {
  const { t } = useI18n({ useScope: "global" })

  const titles = () => {
    if (!media.value) {
      return { genericTitle: "", sensitiveTitle: "" }
    }
    return {
      genericTitle: `${t(
        `mediaDetails.reuse.${media.value.frontendMediaType}`
      )}`,
      sensitiveTitle: `${t(
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
