import { capitalCase } from "~/utils/case"
import type { AudioDetail, ImageDetail, Metadata } from "~/types/media"
import { AUDIO, IMAGE } from "~/constants/media"

import { useProviderStore } from "~/stores/provider"

import type { NuxtI18nInstance } from "@nuxtjs/i18n"

const getImageType = (
  imageType: string | undefined,
  i18n: NuxtI18nInstance
) => {
  if (imageType) {
    if (imageType.split("/").length > 1) {
      return imageType.split("/")[1]
    }
    return imageType
  }
  return i18n.t("mediaDetails.information.unknown")
}

const getAudioType = (audio: AudioDetail, i18n: NuxtI18nInstance) => {
  if (!audio.alt_files) {
    return audio.filetype ?? i18n.t("mediaDetails.information.unknown")
  }
  const altFormats = audio.alt_files
    .map((altFile) => altFile.filetype)
    .filter((filetype) => filetype !== audio.filetype)
  const uniqueFormats = Array.from(new Set(altFormats))
  if (audio.filetype) {
    uniqueFormats.unshift(audio.filetype)
  }
  return [...uniqueFormats].join(", ")
}

export const getMediaMetadata = (
  media: AudioDetail | ImageDetail,
  i18n: NuxtI18nInstance,
  imageInfo?: { width?: number; height?: number; type?: string }
) => {
  const metadata: Metadata[] = []
  if (media.source && media.providerName !== media.sourceName) {
    metadata.push({
      name: "provider",
      label: "mediaDetails.providerLabel",
      value: media.providerName || media.provider,
    })
  }
  const sourceUrl = useProviderStore().getSourceUrl(
    media.source ?? media.provider,
    media.frontendMediaType
  )
  const sourceName = media.sourceName ?? media.providerName ?? media.provider
  metadata.push({
    name: "source",
    label: "mediaDetails.sourceLabel",
    source: media.source ?? media.provider,
    url: sourceUrl,
    value: sourceName,
  })

  if (media.category) {
    metadata.push({
      label: "mediaDetails.information.category",
      value: i18n
        .t(`filters.${media.frontendMediaType}Categories.${media.category}`)
        .toString(),
    })
  }

  const mediaTypeString =
    media.frontendMediaType === IMAGE
      ? getImageType(imageInfo?.type, i18n)
      : getAudioType(media, i18n)
  metadata.push({
    label: "mediaDetails.information.type",
    value: mediaTypeString.toString().toUpperCase(),
  })

  if (media.frontendMediaType === IMAGE) {
    metadata.push({
      label: "imageDetails.information.dimensions",
      value: `${i18n.t("imageDetails.information.sizeInPixels", {
        width: imageInfo?.width,
        height: imageInfo?.height,
      })}`,
    })
  }
  if (media.frontendMediaType === AUDIO) {
    if (media.audio_set) {
      metadata.unshift({
        label: "audioDetails.table.album",
        value: media.audio_set.title,
        url: media.audio_set.foreign_landing_url,
      })
    }
    if (media.genres && media.genres.length > 0) {
      metadata.push({
        label: "audioDetails.table.genre",
        value: media.genres.map((genre) => capitalCase(genre)).join(", "),
      })
    }

    if (media.sample_rate) {
      metadata.push({
        label: "audioDetails.table.sampleRate",
        value: media.sample_rate.toString(),
      })
    }
  }

  return metadata
}
