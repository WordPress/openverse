import http from "k6/http";
import vu from "k6/execution";
import {group, sleep} from "k6";
import {
    API_URL, getRandomWord,
    getUrlBatch,
    makeResponseFailedCheck,
    REQUEST_HEADERS,
    SLEEP_DURATION
} from "./utils.js";


export const searchByWord = (word, page, media_type, page_size) => {
    let url = `${API_URL}${media_type}/?q=${word}&page=${page}&page_size=${page_size}`;
    const response = http.get(url, { headers: REQUEST_HEADERS });

    const responseFailed = makeResponseFailedCheck(word, page)

    if (responseFailed(response, "search")) {
        return 0;
    }

    const parsedResp = response.json();
    const detailUrls = parsedResp["results"].map((i) => i.detail_url);
    const relatedUrls = parsedResp["results"].map((i) => i.related_url);

    let extraFailed = false;

    group("Details requests", () => {
        console.info(
            `Requesting all ${media_type} details from "${word}" at page ${page}`
        );
        const responses = http.batch(getUrlBatch(detailUrls));
        extraFailed = responses.map((r) => responseFailed(r, "details")).some(f => f)
    });

    sleep(SLEEP_DURATION);

    group("Related requests", () => {
        console.info(
            `Requesting all ${media_type} related from "${word}" at page ${page}`
        );
        const responses = http.batch(getUrlBatch(relatedUrls, "related_url"));
        extraFailed = responses.map((r) => responseFailed(r, "related")).some(f => f)
    });

    sleep(SLEEP_DURATION);

    return response.json("page_count");
};


export default function () {
    const MEDIA_TYPE = __ENV.MEDIA_TYPE;
    const PAGE_SIZE = __ENV.PAGE_SIZE;
    console.log(`VU: ${vu.idInTest}  -  ITER: ${__ITER}`);
    const VU_WORD = getRandomWord()

    group(`${MEDIA_TYPE} search (using '${VU_WORD}')`, () => {
        let page = 1;
        let page_count = 1;
        while (page <= page_count) {
            page_count = searchByWord(VU_WORD, page, MEDIA_TYPE, PAGE_SIZE);
            page++;
        }
    });
}
