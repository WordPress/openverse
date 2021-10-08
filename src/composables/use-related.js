import AudioService from '~/data/audio-service'
import ImageService from '~/data/image-service'
import { ref, useFetch } from '@nuxtjs/composition-api'
import { AUDIO, IMAGE } from '~/constants/media'

const services = { [AUDIO]: AudioService, [IMAGE]: ImageService }

export default function useRelated({
  mediaType,
  mediaId,
  service = services[mediaType],
}) {
  const media = ref([])
  // fetch and fetchState are available as this.$fetch and this.$fetchState
  // in components, so there's no need to export them,
  // see https://composition-api.nuxtjs.org/lifecycle/usefetch/
  // eslint-disable-next-line no-unused-vars
  const { fetch } = useFetch(async () => {
    const response = await service.getRelatedMedia({
      id: mediaId.value,
    })
    media.value = response.data.results
  })
  fetch()
  return { media }
}
