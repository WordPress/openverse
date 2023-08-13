import type { AudioDetail, ImageDetail, Metadata } from "~/types/media"
import { AUDIO, IMAGE } from "~/constants/media"

import type { NuxtI18nInstance } from "@nuxtjs/i18n"

const getImageType = (
  imageType: string | undefined,
  i18n: NuxtI18nInstance
) => {
  if (imageType) {
    if (imageType.split("/").length > 1) {
      return imageType.split("/")[1].toUpperCase()
    }
    return imageType.toUpperCase()
  }
  return i18n.t("imageDetails.information.unknown")
}

const getAudioType = (audio: AudioDetail, i18n: NuxtI18nInstance) => {
  if (!audio.alt_files)
    return audio.filetype ?? i18n.t("imageDetails.information.unknown")
  const altFormats = audio.alt_files.map((altFile) => altFile.filetype)
  if (audio.filetype) {
    altFormats.unshift(audio.filetype)
  }
  const uniqueFormats = new Set(altFormats)
  return [...uniqueFormats].join(", ").toUpperCase()
}

export const getMediaMetadata = (
  media: AudioDetail | ImageDetail,
  i18n: NuxtI18nInstance,
  imageInfo?: { width?: number; height?: number; type?: string }
) => {
  const metadata: Metadata[] = []
  if (media.source && media.providerName !== media.sourceName) {
    metadata.push({
      label: i18n.t("imageDetails.information.provider"),
      value: media.providerName || media.provider,
    })
  }
  metadata.push({
    label: i18n.t("imageDetails.information.source"),
    value: media,
    component: "VSourceExternalLink",
  })

  if (media.category) {
    metadata.push({
      label: i18n.t("audioDetails.table.category"),
      value: i18n.t(
        `filters.${media.frontendMediaType}Categories.${media.category}`
      ),
    })
  }

  const mediaTypeString =
    media.frontendMediaType === IMAGE
      ? getImageType(imageInfo?.type, i18n)
      : getAudioType(media, i18n)
  metadata.push({
    label: i18n.t("imageDetails.information.type"),
    value: mediaTypeString,
  })

  if (media.frontendMediaType === IMAGE) {
    metadata.push({
      label: i18n.t("imageDetails.information.dimensions"),
      value: `${imageInfo?.width || 0} × ${imageInfo?.height || 0} ${i18n.t(
        "imageDetails.information.pixels"
      )}`,
    })
  }
  if (media.frontendMediaType === AUDIO) {
    if (media.audio_set) {
      metadata.push({
        label: i18n.t("audioDetails.table.album"),
        value: media.audio_set.title,
        url: media.audio_set.foreign_landing_url,
      })
    }
    if (media.genres && media.genres.length > 0) {
      metadata.push({
        label: i18n.t("audioDetails.table.genre"),
        value: media.genres.join(", "),
      })
    }

    if (media.sample_rate) {
      metadata.push({
        label: i18n.t("audioDetails.table.sampleRate"),
        value: media.sample_rate.toString(),
      })
    }
  }

  return metadata
}
