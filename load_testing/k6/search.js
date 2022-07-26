import http from "k6/http";
import {group, sleep} from "k6";
import {API_URL, getUrlBatch, makeResponseFailedCheck, REQUEST_HEADERS, SLEEP_DURATION} from "./utils.js";


export const searchBy = (param, page, media_type, page_size, followLinks) => {
    let url = `${API_URL}${media_type}/?${param}&page=${page}&page_size=${page_size}&filter_dead=false`;
    const response = http.get(url, { headers: REQUEST_HEADERS });

    const checkResponseFailed = makeResponseFailedCheck(param, page)

    if (checkResponseFailed(response, "search")) {
        console.error(`Failed URL: ${url}`)
        return 0;
    }

    const parsedResp = response.json();
    const pageCount = parsedResp["page_count"];
    const detailUrls = parsedResp["results"].map((i) => i.detail_url);
    const relatedUrls = parsedResp["results"].map((i) => i.related_url);

    // Don't view details/related if not requested
    if (!followLinks) {return pageCount}

    group("Details requests", () => {
        console.info(
            `Requesting all ${media_type} details from "${param}" at page ${page}`
        );
        const responses = http.batch(getUrlBatch(detailUrls));
        responses.map((r) => checkResponseFailed(r, "details"))
    });

    sleep(SLEEP_DURATION);

    group("Related requests", () => {
        console.info(
            `Requesting all ${media_type} related from "${param}" at page ${page}`
        );
        const responses = http.batch(getUrlBatch(relatedUrls, "related_url"));
        responses.map((r) => checkResponseFailed(r, "related"))
    });

    sleep(SLEEP_DURATION);

    return pageCount
};
