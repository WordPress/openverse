import store from '@/store/attribution-store';
import { CopyTextAttribution, CopyHtmlAttribution, DownloadWatermark } from '@/analytics/events';

describe('Attribution Store', () => {
  describe('actions', () => {
    let googleAnalyticsMock = null;

    beforeEach(() => {
      googleAnalyticsMock = {
        sendEvent: jest.fn(),
      };
    });

    it('COPY_ATTRIBUTION sends html event', () => {
      const data = {
        contentType: 'html',
        content: '<div>foo</div>',
      };
      store.actions(googleAnalyticsMock).COPY_ATTRIBUTION({}, data);

      expect(googleAnalyticsMock.sendEvent).toHaveBeenCalledWith(
        new CopyHtmlAttribution(data.content),
      );
    });

    it('COPY_ATTRIBUTION sends text event', () => {
      const data = {
        contentType: 'text',
        content: 'foo',
      };
      store.actions(googleAnalyticsMock).COPY_ATTRIBUTION({}, data);

      expect(googleAnalyticsMock.sendEvent).toHaveBeenCalledWith(
        new CopyTextAttribution(data.content),
      );
    });

    it('DOWNLOAD_WATERMARK sends event', () => {
      const data = {
        imageId: 'foo',
      };
      store.actions(googleAnalyticsMock).DOWNLOAD_WATERMARK({}, data);

      expect(googleAnalyticsMock.sendEvent).toHaveBeenCalledWith(
        new DownloadWatermark(data.imageId),
      );
    });
  });
});
