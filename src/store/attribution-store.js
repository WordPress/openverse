import { 
  CopyRtfAttribution,
  CopyTextAttribution, 
  CopyHtmlAttribution, 
  DownloadWatermark,
} from '@/analytics/events';
import {
  COPY_ATTRIBUTION,
  DOWNLOAD_WATERMARK,
} from './action-types';

const actions = GoogleAnalytics => ({
  // eslint-disable-next-line no-unused-vars
  [COPY_ATTRIBUTION]({ commit }, params) {
    let event;
    switch(params.contentType) {
      case "html":
        event = new CopyHtmlAttribution(params.content);
        break;
      case "rtf":
        event = new CopyRtfAttribution(params.content);
        break;
      default:
        event = new CopyTextAttribution(params.content);
        break;
    }
    GoogleAnalytics.sendEvent(event);
  },
  // eslint-disable-next-line no-unused-vars
  [DOWNLOAD_WATERMARK]({ commit }, params) {
    const event = DownloadWatermark(params);
    GoogleAnalytics.sendEvent(event);
  },
});

export default {
  actions,
};
