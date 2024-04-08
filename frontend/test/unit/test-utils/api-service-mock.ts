import MockAdapter from "axios-mock-adapter"

import * as apiService from "~/data/api-service"

jest.mock("~/data/api-service", () => ({ createApiService: jest.fn() }))
const originalApiService = jest.requireActual("~/data/api-service")

const createApiService = apiService.createApiService as jest.Mock<
  ReturnType<typeof apiService.createApiService>,
  Parameters<typeof apiService.createApiService>
>

/**
 * Creates an API Service that gets reused throughout the lifetime of
 * the current context in which it is called.
 *
 * @example
 * ```typescript
 * it('should get some response', async () => {
 *   mockCreateApiService((mockAdapter) => {
 *     mockAdapter
 *       .onGet(/hello/).replyOnce(200, ', world!')
 *       .onGet(/hello/).replyOnce(200, ', Openverse!')
 *   })
 *
 *   expect(
 *     await createApiService().get('hello')
 *   ).toEqual(', world!')
 *
 *   expect(
 *     await createApiService().get('hello')
 *   ).toEqual(', Openverse!')
 * })
 * ```
 *
 * Note in the example that despite `createApiService` being called
 * twice, the mock adapter is not re-applied and the second registered
 * response still works as expected.
 *
 * With the particular way this mock creation function works,
 * even if `createApiService` is called several times during
 * the lifecycle of a particular test context, the same `apiService`
 * instance will be reused for each call. This is done to preserve
 * lists of responses applied to the mock adapter in the `applyMocks`
 * callback. Otherwise, if `createApiService` is called more than
 * once per test, then each time it is called will cause a new
 * call to `applyMocks` and reset the stack of responses on the
 * mock adapter (as it will be using a new axios client anyway).
 *
 * This may cause unforeseen difficulties with using this mock
 * in other tests. For now this is the only sane way to isolate
 * the `createApiService` behavior. Ideally the axios client would
 * be put into Nuxt context so that it can be universally mocked
 * throughout the lifecycle of plugin, component, and store operations.
 *
 * @see https://github.com/ctimmerm/axios-mock-adapter
 *
 * @param applyMocks - Callback function used to apply mock
 * responses using the `axios-mock-adapter` library
 */
export const mockCreateApiService = (
  applyMocks: (mockAdapter: MockAdapter) => void
): void => {
  let apiService: apiService.ApiService | undefined
  createApiService.mockImplementation((options) => {
    // Only ever generate the mock once
    if (apiService) {
      return apiService
    }

    apiService = originalApiService.createApiService(
      options
    ) as apiService.ApiService

    applyMocks(new MockAdapter(apiService.client))

    return apiService
  })
}
