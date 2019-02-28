import { CopyTextAttribution, CopyHtmlAttribution } from '@/analytics/events';
import {
  COPY_ATTRIBUTION,
} from './action-types';

const actions = GoogleAnalytics => ({
  // eslint-disable-next-line no-unused-vars
  [COPY_ATTRIBUTION]({ commit }, params) {
    const event = params.contentType === 'html' ?
      new CopyHtmlAttribution(params.content) :
      new CopyTextAttribution(params.content);

    GoogleAnalytics.sendEvent(event);
  },
});

export default {
  actions,
};
