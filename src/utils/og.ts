import type { MetaInfo } from 'vue-meta'
import type { MetaPropertyName } from 'vue-meta/types/vue-meta'

export const createDetailPageMeta = (title?: string, thumbnail?: string) => {
  const head = {} as MetaInfo
  const meta = [
    {
      hid: 'robots',
      name: 'robots',
      content: 'noindex',
    },
  ] as MetaPropertyName[]
  if (title) {
    head.title = `${title} | Openverse`
    meta.push({
      hid: 'og:title',
      name: 'og:title',
      content: title,
    })
  }
  if (thumbnail) {
    meta.push({
      hid: 'og:image',
      name: 'og:image',
      content: thumbnail,
    })
  }
  head.meta = meta
  return head
}
