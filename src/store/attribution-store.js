import { 
  CopyRtfAttribution,
  CopyTextAttribution, 
  CopyHtmlAttribution, 
} from '@/analytics/events';
import {
  COPY_ATTRIBUTION,
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
});

export default {
  actions,
};
