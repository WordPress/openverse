import { screen } from "@testing-library/vue"
import { default as userEvent } from "@testing-library/user-event"

import { render } from "~~/test/unit/test-utils/render"

import VSourcesTableVue from "~/components/VSourcesTable.vue"

// const initialProviderStoreState = {
//   providers: {
//     image: [
//       {
//         source_name: "Provider_B",
//         display_name: "Provider B",
//         source_url: "http://yyy.com",
//         media_count: 1111,
//       },
//       {
//         source_name: "Provider_C",
//         display_name: "Provider C",
//         source_url: "www.xxx.com",
//         media_count: 2222,
//       },
//       {
//         source_name: "Provider_A",
//         display_name: "Provider A",
//         source_url: "https://zzz.com",
//         media_count: 3333,
//       },
//     ],
//   },
// }

const getTableData = (table) => {
  const data = [...table.rows].map((t) =>
    [...t.children].map((u) => u.textContent.trim())
  )
  // Remove the header row
  data.shift()
  return data
}

describe("VSourcesTable", () => {
  let options

  beforeEach(() => {
    options = {
      props: { media: "image" },
      stubs: ["TableSortIcon", "VLink"],
    }
    // configureStoreCb = (localVue, options) => {
    //   providerStore = useProviderStore(options?.pinia)
    //   providerStore.$patch(initialProviderStoreState)
    // }
  })

  it('should be sorted by display_name ("Source") by default', async () => {
    await render(VSourcesTableVue, options)
    const table = getTableData(screen.getByLabelText(/source/i))
    const expectedTable = [
      ["Provider A", "zzz.com", "3,333"],
      ["Provider B", "yyy.com", "1,111"],
      ["Provider C", "xxx.com", "2,222"],
    ]
    expect(table).toEqual(expectedTable)
  })

  it('should be sorted by clean url when click on "Domain" header', async () => {
    await render(VSourcesTableVue, options)
    const domainCell = screen.getByRole("columnheader", {
      name: /domain/i,
    })
    await userEvent.click(domainCell)
    const table = getTableData(screen.getByLabelText("sources table"))
    const expectedTable = [
      ["Provider C", "xxx.com", "2,222"],
      ["Provider B", "yyy.com", "1,111"],
      ["Provider A", "zzz.com", "3,333"],
    ]
    expect(table).toEqual(expectedTable)
  })

  it('should be sorted by media_count when click on "Total items" header', async () => {
    await render(VSourcesTableVue, options)
    const domainCell = screen.getByRole("columnheader", {
      name: /total items/i,
    })
    await userEvent.click(domainCell)
    const table = getTableData(screen.getByLabelText("sources table"))
    const expectedTable = [
      ["Provider B", "yyy.com", "1,111"],
      ["Provider C", "xxx.com", "2,222"],
      ["Provider A", "zzz.com", "3,333"],
    ]
    expect(table).toEqual(expectedTable)
  })
})
