import { decodeData } from '~/utils/decode-data'
import { IMAGE } from '~/constants/media'

/**
 * @template {import('../store/types').MediaDetail} T
 * @param {T} media
 * @param {import('../store/types').SupportedMediaType} mediaType
 * @return {T}
 */
export default function decodeMediaData(media, mediaType = IMAGE) {
  return {
    ...media,
    frontendMediaType: mediaType,
    creator: decodeData(media.creator),
    title: decodeData(media.title)
      ? decodeData(media.title)
      : mediaType === IMAGE
      ? 'Image'
      : 'Audio',
    tags: media.tags
      ? media.tags.map((tag) => ({ ...tag, name: decodeData(tag.name) }))
      : [],
  }
}
