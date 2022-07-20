import {default as randomWordsTest} from  "./randomWords.js"

export const options = {
  scenarios: {
    random_word_image_page_20: {
      executor: 'per-vu-iterations',
      env: {
        MEDIA_TYPE: "images",
        PAGE_SIZE: "20",
      },
      exec: "randomWords",
      vus: 5,
      iterations: 5
    }
  }
};


export const randomWords = randomWordsTest;


export default function() {
}