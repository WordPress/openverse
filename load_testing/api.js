import http from "k6/http";
import { vu } from "k6/execution";
import { check, group, sleep } from "k6";

export const options = {
  vus: 5,
  iterations: 5,
};

const API_URL = __ENV.API_URL || "https://api-dev.openverse.engineering/v1/";
const PAGE_SIZE = __ENV.PAGE_SIZE || 20;
const MEDIA_TYPE = __ENV.MEDIA_TYPE || "images";
const REQUEST_HEADERS = {
  Authorization: `Bearer ${__ENV.API_TOKEN}`,
  "User-Agent": "k6",
};
const SLEEP_DURATION = 0.1;
const WORDS = ["honey", "duck", "hummingbird", "dog", "hedgehog"];

const getUrlBatch = (urls, type = "detail_url") => {
  return urls.map((u) => {
    const params = { headers: REQUEST_HEADERS, tags: { name: type } };
    return ["GET", u, null, params];
  });
};

const searchByWord = (word, page) => {
  let url = `${API_URL}${MEDIA_TYPE}/?q=${word}&page=${page}&page_size=${PAGE_SIZE}`;
  const response = http.get(url, { headers: REQUEST_HEADERS });

  if (check(response, { "status was 200": (r) => r.status === 200 })) {
    console.log(`Checked status 200 ✓ for word "${word}" at page ${page}.`);
  } else {
    console.error(`Request failed ⨯ for word "${word}" at page ${page}.`);
    return 0;
  }

  const parsedResp = response.json();
  const detailUrls = parsedResp["results"].map((i) => i.detail_url);
  const relatedUrls = parsedResp["results"].map((i) => i.related_url);

  group("Details requests", () => {
    console.info(
      `Requesting all ${MEDIA_TYPE} details from "${word}" at page ${page}`
    );
    const responses = http.batch(getUrlBatch(detailUrls));
  });

  sleep(SLEEP_DURATION);

  group("Related requests", () => {
    console.info(
      `Requesting all ${MEDIA_TYPE} related from "${word}" at page ${page}`
    );
    const responses = http.batch(getUrlBatch(relatedUrls, "related_url"));
  });

  sleep(SLEEP_DURATION);

  return response.json("page_count");
};

export default function () {
  console.log(`VU: ${vu.idInTest}  -  ITER: ${__ITER}`);
  const VU_WORD = WORDS[vu.idInTest - 1];

  group(`${MEDIA_TYPE} search`, () => {
    let page = 1;
    let page_count = 1;
    while (page <= page_count) {
      page_count = searchByWord(VU_WORD, page);
      page++;
    }
  });
}
