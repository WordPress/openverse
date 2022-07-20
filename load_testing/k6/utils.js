import {check} from "k6";


export const API_URL = __ENV.API_URL || "https://api-dev.openverse.engineering/v1/";
export const SLEEP_DURATION = 0.1;


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
            console.error(`Request failed ⨯ for word "${word}" at page ${page} for ${action}.`);
            return true;
        }
    }
}