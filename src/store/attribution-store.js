import { CopyTextAttribution, CopyHtmlAttribution, DownloadWatermark } from '@/analytics/events';
import {
  COPY_ATTRIBUTION,
  DOWNLOAD_WATERMARK,
} from './action-types';

const actions = GoogleAnalytics => ({
  // eslint-disable-next-line no-unused-vars
  [COPY_ATTRIBUTION]({ commit }, params) {
    const event = params.contentType === 'html' ?
      new CopyHtmlAttribution(params.content) :
      new CopyTextAttribution(params.content);

    GoogleAnalytics.sendEvent(event);
  },
  // eslint-disable-next-line no-unused-vars
  [DOWNLOAD_WATERMARK]({ commit }, params) {
    const event = DownloadWatermark(params.imageId);
    GoogleAnalytics.sendEvent(event);
  },
});

export default {
  actions,
};
