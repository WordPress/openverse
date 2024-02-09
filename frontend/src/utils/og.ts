import type { MetaInfo } from "vue-meta"
import type {
  MetaPropertyName,
  MetaPropertyProperty,
} from "vue-meta/types/vue-meta"

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
  const head = {} as MetaInfo
  const meta = [
    {
      hid: "robots",
      name: "robots",
      content: "noindex",
    },
  ] as (MetaPropertyName | MetaPropertyProperty)[]
  if (title) {
    meta.push({
      hid: "og:title",
      property: "og:title",
      content: title,
    })
  }
  if (thumbnail && !isSensitive) {
    meta.push({
      hid: "og:image",
      property: "og:image",
      content: thumbnail,
    })
  }
  head.meta = meta
  return head
}
