// eslint-disable-next-line spaced-comment
/// <reference types="cypress" />

describe('Home', () => {
  beforeEach(() => {
    // Because we're only testing the homepage
    // in this test file, we can run this command
    // before each individual test instead of
    // repeating it in every test.
    cy.viewport(1400, 1000)
    cy.visit('')
    cy.wait(5000)
  })

  it('Should display the search input', () => {
    cy.get('.is-hidden-touch #searchTerm').should('be.visible')
  })

  it('Should submit a search when the submit button is clicked', () => {
    cy.get('.is-hidden-touch #searchTerm').type('dogs')
    cy.get('form').submit()
  })
})
