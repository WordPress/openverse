import {
  CopyAttribution,
  EmbedAttribution,
  DownloadWatermark,
} from '@/analytics/events';
import {
  COPY_ATTRIBUTION,
  EMBED_ATTRIBUTION,
  DOWNLOAD_WATERMARK,
} from './action-types';

const actions = GoogleAnalytics => ({
  // eslint-disable-next-line no-unused-vars
  [COPY_ATTRIBUTION]({ commit }, params) {
    const event = CopyAttribution(params.content);
    GoogleAnalytics.sendEvent(event);
  },
  [EMBED_ATTRIBUTION]() {
    const event = EmbedAttribution();
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
