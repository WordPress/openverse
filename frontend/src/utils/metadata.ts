import type { AudioDetail, ImageDetail, Metadata } from "~/types/media"
import { IMAGE } from "~/constants/media"

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
  if (!audio.alt_files)
    return audio.filetype ?? i18n.t("mediaDetails.information.unknown")
  const altFormats = audio.alt_files.map((altFile) => altFile.filetype)
  if (audio.filetype) {
    altFormats.unshift(audio.filetype)
  }
  const uniqueFormats = new Set(altFormats)
  return [...uniqueFormats].join(", ")
}

export const getMediaMetadata = (
  media: AudioDetail | ImageDetail,
  i18n: NuxtI18nInstance,
  imageInfo?: { width?: number; height?: number; type?: string }
) => {
  const metadata: Metadata[] = []
  if (media.frontendMediaType === IMAGE) {
    const mediaTypeString = getImageType(imageInfo?.type, i18n)
    metadata.push({
      label: "mediaDetails.information.type",
      value: mediaTypeString.toString().toUpperCase(),
    })
    if (media.providerName !== media.sourceName) {
      metadata.push({
        label: "mediaDetails.providerLabel",
        value: media.providerName || media.provider,
      })
    }
    metadata.push({
      label: "mediaDetails.sourceLabel",
      value: media.sourceName ?? media.providerName ?? media.provider,
      url: media.foreign_landing_url,
    })
    metadata.push({
      label: "imageDetails.information.dimensions",
      value: `${i18n.t("imageDetails.information.sizeInPixels", {
        width: imageInfo?.width,
        height: imageInfo?.height,
      })}`,
    })
  } else {
    const mediaTypeString = getAudioType(media, i18n)
    if (media.audio_set) {
      metadata.push({
        label: "audioDetails.table.album",
        value: media.audio_set.title,
        url: media.audio_set.foreign_landing_url,
      })
    }
    if (media.category) {
      const categoryKey = `filters.audioCategories.${media.category}`
      metadata.push({
        label: "mediaDetails.information.type",
        value: `${i18n.t(categoryKey)}`,
      })
    }
    if (media.sample_rate) {
      metadata.push({
        label: "audioDetails.table.sampleRate",
        value: `${media.sample_rate}`,
      })
    }
    if (media.filetype) {
      metadata.push({
        label: "audioDetails.table.filetype",
        value: mediaTypeString.toString().toUpperCase(),
      })
    }
    metadata.push({
      label: "mediaDetails.providerLabel",
      value: media.providerName || media.provider,
      url: media.foreign_landing_url,
    })
    if (media.source && media.providerName !== media.sourceName) {
      metadata.push({
        label: "mediaDetails.sourceLabel",
        value: media.sourceName ?? media.providerName ?? media.provider,
      })
    }
    if (media.genres && media.genres.length > 0) {
      metadata.push({
        label: "audioDetails.table.genre",
        value: media.genres.join(", "),
      })
    }
  }
  return metadata
}
