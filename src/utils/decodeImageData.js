import decodeData from '~/utils/decodeData'

export default function decodeImageData(image) {
  return {
    ...image,
    creator: decodeData(image.creator),
    title: decodeData(image.title) ? decodeData(image.title) : 'Image',
    tags: image.tags
      ? image.tags.map((tag) => ({ ...tag, name: decodeData(tag.name) }))
      : [],
  }
}
