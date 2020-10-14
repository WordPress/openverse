/// <reference types="cypress" />

describe('Home', () => {
  beforeEach(() => {
    // Because we're only testing the search flow
    // in this test file, we can run this command
    // before each individual test instead of
    // repeating it in every test.
    cy.viewport(1400, 1000)
    cy.visit('')
    // cy.wait(1000)
  })

  it('Should execute the entire search flow properly', async () => {
    // Submit the form
    cy.get('.is-hidden-touch #searchTerm').type('dogs').blur()
    cy.get('form').submit()

    // click on a single image result
    cy.get('.search-grid_image:first').click()

    // Confirm there's a url on the source!
    cy.get('[data-testid="source-button"]').should('have.attr', 'href')
  })
})
