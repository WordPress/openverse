import {default as randomWordsTest} from  "./randomWords.js"


const createScenario = (mediaType, pageSize, funcName) => {
  return {
    executor: 'per-vu-iterations',
    env: {
      MEDIA_TYPE: mediaType,
      PAGE_SIZE: pageSize,
    },
    exec: funcName,
    vus: 5,
    iterations: 5
  }
}

export const options = {
  scenarios: {
    random_word_image_page_20: createScenario("images", "20", "randomWords"),
    random_word_audio_page_20: createScenario("audio", "20", "randomWords"),
    random_word_image_page_500: createScenario("images", "500", "randomWords"),
    random_word_audio_page_500: createScenario("audio", "500", "randomWords"),
  }
};


export const randomWords = randomWordsTest;


export default function() {
}
