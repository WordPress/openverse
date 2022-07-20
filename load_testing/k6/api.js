import {vu} from "k6/execution";
import {group} from "k6";
import {searchByWord} from "./randomWords.js"

export const options = {
  vus: 5,
  iterations: 5,
};

const WORDS = ["honey", "duck", "hummingbird", "dog", "hedgehog"];


export default function () {
  console.log(`VU: ${vu.idInTest}  -  ITER: ${__ITER}`);
  const VU_WORD = WORDS[vu.idInTest - 1];

  group(`Image search`, () => {
    let page = 1;
    let page_count = 1;
    while (page <= page_count) {
      page_count = searchByWord(VU_WORD, page, "images", 20);
      page++;
    }
  });
}
