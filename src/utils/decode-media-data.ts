import { title } from 'case'

import { decodeData as decodeString } from '~/utils/decode-data'
import type { Media, Tag } from '~/models/media'

/**
 * This interface is a subset of `Media` that types dictionaries sent by the API
 * being decoded in the `decodeMediaData` function.
 */
interface ApiMedia extends Omit<Media, 'frontendMediaType' | 'title'> {
  title?: string
}

/**
 * For any given media, decode the media title, creator name and individual tag
 * names. Also populates the `frontendMediaType` field on the model.
 *
 * @param media - the media object of which to decode attributes
 * @param mediaType - the type of the media
 * @returns the given media object with the text fields decoded
 */
export const decodeMediaData = <T extends Media>(
  media: ApiMedia,
  mediaType: T['frontendMediaType']
): T =>
  ({
    ...media,
    frontendMediaType: mediaType,
    title: decodeString(media.title) || title(mediaType),
    creator: decodeString(media.creator),
    // TODO: remove `?? []`
    tags: (media.tags ?? ([] as Tag[])).map((tag) => ({
      ...tag,
      name: decodeString(tag.name),
    })),
  } as T)
