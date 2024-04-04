import { OpenverseClient } from "@openverse/api-client"
import nock from "nock"

export const baseUrl = "https://nock.local/"
export const apiClient = OpenverseClient({ baseUrl })
export const getApiNock = () => nock(baseUrl)
