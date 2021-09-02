import decodeData from '~/utils/decode-data'
import { IMAGE } from '~/constants/media'

export default function decodeMediaData(media, mediaType = IMAGE) {
  return {
    ...media,
    creator: decodeData(media.creator),
    title: decodeData(media.title)
      ? decodeData(media.title)
      : `${mediaType[0].toUpperCase()}${mediaType.slice(1)}`,
    tags: media.tags
      ? media.tags.map((tag) => ({ ...tag, name: decodeData(tag.name) }))
      : [],
  }
}
