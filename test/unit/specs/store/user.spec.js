import { v4 as uuidv4 } from 'uuid'

import * as user from '~/store/user'

jest.mock('uuid', () => ({ v4: jest.fn() }))

describe('user store', () => {
  beforeEach(() => {
    process.server = false
    process.client = false
  })

  afterAll(() => {
    // avoid polluting other tests that might be affected by these flags
    delete process.server
    delete process.client
  })

  it('should generate a new usageSessionId when on server', () => {
    uuidv4.mockReturnValue('abcd-1234')
    process.server = true
    expect(user.state().usageSessionId).toEqual('abcd-1234')
  })

  it('should not generate a new usageSessionId when on client', () => {
    process.client = true
    expect(user.state().usageSessionId).toBeUndefined()
  })
})
