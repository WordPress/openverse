import store from '@/store/bug-report-store';

describe('Attribution Store', () => {
  describe('actions', () => {
    let serviceMock = null;

    beforeEach(() => {
      serviceMock = {
        reportBug: jest.fn(),
      };
    });

    it('calls reportBug service', () => {
      const data = {
        name: 'Foo',
        email: 'foo@bar.com',
        bug_description: 'FooBar',
        browser_info: 'Foo browser',
      };
      store.actions(serviceMock).REPORT_BUG({}, data);

      expect(serviceMock.reportBug).toHaveBeenCalledWith(data);
    });
  });
});
