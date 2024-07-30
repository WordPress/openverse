type Meta = {
  name?: string
  content?: string
  property?: string
  key?: string
}[]

export const createDetailPageMeta = ({
  title,
  thumbnail,
  isSensitive,
}: {
  /** Media title or localized sensitive or generic media title */
  title?: string
  thumbnail?: string
  isSensitive: boolean
}) => {
  const head: { meta: Meta } = { meta: [] }
  const meta: Meta = []
  if (title) {
    meta.push({
      key: "og:title",
      property: "og:title",
      content: title,
    })
  }
  if (thumbnail && !isSensitive) {
    meta.push({
      key: "og:image",
      property: "og:image",
      content: thumbnail,
    })
  }
  head.meta = meta
  return head
}
