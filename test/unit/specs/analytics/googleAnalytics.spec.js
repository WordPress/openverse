import analytics from '@/analytics/GoogleAnalytics';
import { CopyTextAttribution } from '@/analytics/events';

describe('GA', () => {
  it('sends event', () => {
    window.ga = jest.fn();

    const event = new CopyTextAttribution('foo');
    analytics.sendEvent(event);

    expect(window.ga).toHaveBeenCalledWith('send', event);
  });
});
