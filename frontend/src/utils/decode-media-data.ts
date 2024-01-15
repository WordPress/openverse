import { decodeData as decodeString } from "~/utils/decode-data"
import { SENSITIVITY_RESPONSE_PARAM } from "~/constants/content-safety"
import { AUDIO, IMAGE, MODEL_3D, VIDEO } from "~/constants/media"
import type { ApiMedia, Media, Tag } from "~/types/media"
import type { MediaType } from "~/constants/media"
import { useFeatureFlagStore } from "~/stores/feature-flag"
import { useProviderStore } from "~/stores/provider"
import { capitalCase } from "~/utils/case"
import { getFakeSensitivities } from "~/utils/content-safety"

const mediaTypeExtensions: Record<MediaType, string[]> = {
  [IMAGE]: ["jpg", "jpeg", "png", "gif", "svg"],
  [AUDIO]: ["mp3", "wav", "ogg", "flac", "aac", "aiff", "mp32"],
  [VIDEO]: ["mp4", "webm", "mkv", "avi", "mov", "wmv", "flv", "mpg", "mpeg"],
  [MODEL_3D]: ["fbx", "obj", "stl", "dae", "3ds", "blend", "max", "obj", "ply"],
}

const matchers = [/jpe?g$/i, /tiff?$/i, /mp32?$/i]

/**
 * Compares the filetypes, taking into account different versions of the same
 * filetype. For example, `.jpg` and `.jpeg` are considered the same filetype.
 * @param extension - the extension of the file.
 * @param filetype - the type of the file.
 */
const isFiletypeMatching = (extension: string, filetype?: string) => {
  if (filetype === extension) {
    return true
  }
  if (!filetype) {
    return false
  }
  return matchers.some((matcher) =>
    Boolean(filetype.match(matcher) && extension.match(matcher))
  )
}
export const extractPartAfterLastDot = (str?: string) => {
  if (!str || str.lastIndexOf(".") === -1) {
    return ""
  }
  return str.split(".").pop()?.toLowerCase() ?? ""
}

/**
 * Strip the extension from title if it matches the filetype of the media.
 * Since not all media records return filetype, we also try to guess the filetype
 * from the url extension.
 */
const stripExtension = (
  title: string,
  mediaType: MediaType,
  media: ApiMedia
) => {
  const filetype = media.filetype ?? extractPartAfterLastDot(media.url)
  const lastDotIndex = title.lastIndexOf(".")
  const [titleWithoutExtension, possibleExtension] = [
    title.slice(0, lastDotIndex),
    title.slice(lastDotIndex + 1),
  ]
  if (
    mediaTypeExtensions[mediaType].includes(filetype) &&
    isFiletypeMatching(possibleExtension, filetype)
  ) {
    return titleWithoutExtension
  }
  return title
}

const extractFiletype = (url: string, mediaType: MediaType) => {
  if (url.lastIndexOf(".") === -1) {
    return null
  }
  const extension = url.split(".").pop()?.toLowerCase()
  return extension && mediaTypeExtensions[mediaType].includes(extension)
    ? extension
    : null
}
/**
 * Corrects the encoding of the media title, or uses the media type as the title.
 * If the title has a file extension that matches media filetype, it will be stripped.
 */
const mediaTitle = (
  media: ApiMedia,
  mediaType: MediaType
): { title: string; originalTitle: string } => {
  const originalTitle = decodeString(media.title) || capitalCase(mediaType)
  return {
    originalTitle,
    title: stripExtension(originalTitle, mediaType, media),
  }
}

/**
 * Removes the tags that are empty or undefined, and decodes the tag names.
 */
const parseTags = (tags: Tag[]) => {
  return tags
    .filter((tag) => Boolean(tag))
    .map((tag) => ({ ...tag, name: decodeString(tag.name) }))
}

/**
 * Prepare any given media for the frontend:
 * - decode the media title, creator name and individual tag names to ensure
 * that there are no incorrectly encoded strings.
 * - populate the `frontendMediaType` field on the model.
 * - populate the `sensitivity` and `isSensitive` field on the model.
 * - clean up the title by removing the file extension if it matches the media
 * filetype, and removing "FILE:" prefix for wikimedia items.
 *
 * @param media - the media object of which to decode attributes
 * @param mediaType - the type of the media
 * @returns the given media object with the text fields decoded
 */
export const decodeMediaData = <T extends Media>(
  media: ApiMedia | undefined | null,
  mediaType: T["frontendMediaType"]
): T => {
  if (!media) {
    throw new Error("Media is undefined or null")
  }
  // Fake ~50% of results as sensitive.
  const featureFlagStore = useFeatureFlagStore()
  const sensitivity =
    featureFlagStore.isOn("fake_sensitive") &&
    featureFlagStore.isOn("fetch_sensitive")
      ? getFakeSensitivities(media.id)
      : media[SENSITIVITY_RESPONSE_PARAM] ?? []
  sensitivity.sort()
  const isSensitive = sensitivity.length > 0

  const providerStore = useProviderStore()
  const sourceName = providerStore.getProviderName(media.source, mediaType)
  const providerName = providerStore.getProviderName(media.provider, mediaType)
  const filetype =
    media.filetype ?? extractFiletype(media.url, mediaType) ?? "Unknown"

  return {
    ...media,
    ...mediaTitle(media, mediaType),
    frontendMediaType: mediaType,
    creator: decodeString(media.creator),
    tags: media.tags ? parseTags(media.tags) : ([] as Tag[]),
    filetype,
    sourceName,
    providerName,
    sensitivity,
    isSensitive,
  } as T
}
