type Meta = { name?: string; content?: string; property?: string }[]

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
  const meta: Meta = [
    {
      name: "robots",
      content: "noindex",
    },
  ]
  if (title) {
    meta.push({
      property: "og:title",
      content: title,
    })
  }
  if (thumbnail && !isSensitive) {
    meta.push({
      property: "og:image",
      content: thumbnail,
    })
  }
  head.meta = meta
  return head
}
