import {check} from "k6";
import {randomItem} from "https://jslib.k6.io/k6-utils/1.2.0/index.js";

export const API_URL = __ENV.API_URL || "https://api-dev.openverse.engineering/v1/";
export const SLEEP_DURATION = 0.1;
// Use the random words list available locally, but filter any words that end with apostrophe-s
const WORDS = open("/usr/share/dict/words").split("\n").filter(w => !w.endsWith("'s"));


export const getRandomWord = () => randomItem(WORDS);


export const REQUEST_HEADERS = {
    Authorization: `Bearer ${__ENV.API_TOKEN}`,
    "User-Agent": "k6",
};

export const getUrlBatch = (urls, type = "detail_url") => {
    return urls.map((u) => {
        const params = {headers: REQUEST_HEADERS, tags: {name: type}};
        return ["GET", u, null, params];
    });
};

export const makeResponseFailedCheck = (word, page) => {
    return (response, action) => {
        if (check(response, {"status was 200": (r) => r.status === 200})) {
            console.log(`Checked status 200 ✓ for word "${word}" at page ${page} for ${action}.`);
            return false;
        } else {
            console.error(`Request failed ⨯ for word "${word}" at page ${page} for ${action}: ${response.body}`);
            return true;
        }
    }
}
