import { ref, useFetch } from '@nuxtjs/composition-api'
import { mediaServices } from '~/store/media'

export default function useRelated({
  mediaType,
  mediaId,
  service = mediaServices[mediaType],
}) {
  const media = ref([])
  // fetch and fetchState are available as this.$fetch and this.$fetchState
  // in components, so there's no need to export them,
  // see https://composition-api.nuxtjs.org/lifecycle/usefetch/
  // eslint-disable-next-line no-unused-vars
  const { fetch } = useFetch(async () => {
    const data = await service.getRelatedMedia({
      id: mediaId.value,
    })
    media.value = data.results
  })
  fetch()
  return { media }
}
