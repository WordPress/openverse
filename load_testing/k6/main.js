import { group } from 'k6'
import { searchBy } from './search.js'
import { getProvider, getRandomWord } from './utils.js'

const createScenario = (mediaType, pageSize, funcName) => {
  return {
    executor: 'per-vu-iterations',
    env: {
      MEDIA_TYPE: mediaType,
      PAGE_SIZE: pageSize,
    },
    exec: funcName,
    vus: 5,
    iterations: 5,
  }
}

export const options = {
  scenarios: {
    random_word_image_page_20: createScenario(
      'images',
      '20',
      'searchByRandomWord'
    ),
    random_word_audio_page_20: createScenario(
      'audio',
      '20',
      'searchByRandomWord'
    ),
    random_word_image_page_500: createScenario(
      'images',
      '500',
      'searchByRandomWord'
    ),
    random_word_audio_page_500: createScenario(
      'audio',
      '500',
      'searchByRandomWord'
    ),
    provider_image_page_20: createScenario('image', '20', 'searchByProvider'),
    provider_image_page_500: createScenario('image', '500', 'searchByProvider'),
    provider_audio_page_20: createScenario('audio', '20', 'searchByProvider'),
    provider_audio_page_500: createScenario('audio', '500', 'searchByProvider'),
  },
}

const searchByField = (paramFunc, followLinks = false) => {
  const MEDIA_TYPE = __ENV.MEDIA_TYPE
  const PAGE_SIZE = __ENV.PAGE_SIZE
  console.log(`VU: ${__VU}  -  ITER: ${__ITER}`)
  const param = paramFunc(MEDIA_TYPE)
  const depth = followLinks ? 'Deep' : 'Shallow'

  group(
    `${depth} ${MEDIA_TYPE} search of ${PAGE_SIZE} items (using '${param}')`,
    () => {
      let page = 1
      let page_count = 1
      while (page <= page_count) {
        page_count = searchBy(param, page, MEDIA_TYPE, PAGE_SIZE, followLinks)
        page++
      }
    }
  )
}

export const searchByRandomWord = () =>
  searchByField(() => `q=${getRandomWord()}`, true)
export const searchByProvider = () =>
  searchByField((media_type) => `source=${getProvider(media_type)}`, false)
