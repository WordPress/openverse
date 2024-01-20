import { screen } from "@testing-library/vue"
import { default as userEvent } from "@testing-library/user-event"

import { beforeEach, describe, expect, it } from "vitest"

import { render } from "~~/test/unit/test-utils/render"

import { useProviderStore } from "~/stores/provider"

import VSourcesTable from "~/components/VSourcesTable.vue"

const getTableData = (tableRows) => {
  const data = [...tableRows].map((t) =>
    [...t.children].map((u) => u.textContent.trim())
  )
  // Remove the header row
  data.shift()
  return data
}

describe("VSourcesTable", () => {
  let options

  beforeEach(() => {
    const providerStore = useProviderStore()
    providerStore.$patch({
      providers: {
        image: [
          {
            source_name: "Provider_B",
            display_name: "Provider B",
            source_url: "http://yyy.com",
            media_count: 1111,
          },
          {
            source_name: "Provider_C",
            display_name: "Provider C",
            source_url: "www.xxx.com",
            media_count: 2222,
          },
          {
            source_name: "Provider_A",
            display_name: "Provider A",
            source_url: "https://zzz.com",
            media_count: 3333,
          },
        ],
      },
    })
    options = {
      props: { media: "image" },
      global: {
        stubs: ["TableSortIcon"],
      },
    }
  })

  it('should be sorted by display_name ("Source") by default', async () => {
    await render(VSourcesTable, options)

    const table = getTableData(screen.getAllByRole("row"))
    const expectedTable = [
      ["Provider A", "zzz.com", "3,333"],
      ["Provider B", "yyy.com", "1,111"],
      ["Provider C", "xxx.com", "2,222"],
    ]
    expect(table).toEqual(expectedTable)
  })

  it('should be sorted by clean url when click on "Domain" header', async () => {
    await render(VSourcesTable, options)
    const domainCell = screen.getByRole("columnheader", {
      name: /domain/i,
    })
    await userEvent.click(domainCell)
    const table = getTableData(screen.getAllByRole("row"))
    const expectedTable = [
      ["Provider C", "xxx.com", "2,222"],
      ["Provider B", "yyy.com", "1,111"],
      ["Provider A", "zzz.com", "3,333"],
    ]
    expect(table).toEqual(expectedTable)
  })

  // https://github.com/wordpress/openverse/issues/411
  it('should be sorted by media_count when click on "Total items" header', async () => {
    await render(VSourcesTable, options)
    const domainCell = screen.getByRole("columnheader", {
      name: /total items/i,
    })
    await userEvent.click(domainCell)
    const table = getTableData(screen.getAllByRole("row"))
    const expectedTable = [
      ["Provider B", "yyy.com", "1,111"],
      ["Provider C", "xxx.com", "2,222"],
      ["Provider A", "zzz.com", "3,333"],
    ]
    expect(table).toEqual(expectedTable)
  })
})
