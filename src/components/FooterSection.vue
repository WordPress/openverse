<template>
<footer class="footer callout large secondary">
   <div class="grid-container full">
      <div class="large-3 cell">
          <ul class="footer_links menu">
            <li><a href="https://creativecommons.org/contact">Contact</a></li>
            <li><a href="https://creativecommons.org/privacy">Privacy</a></li>
            <li><a href="https://creativecommons.org/policies">Policies</a></li>
            <li><a href="https://creativecommons.org/terms">Terms</a></li>
            <li><a href="https://creativecommons.org/faq">FAQ</a></li>
          </ul>
      </div>
      <hr>
      <div class="grid-x grid-margin-x grid-margin-y">
        <div class="medium-3 large-3 cell">
          <img class="footer_logo" src="../assets/cc-logo_large_black.png">
            <p>
              We’re changing the way people share around the world
              with our Global Community and 1.4 billion pieces of
              content under our simple, easy-to-use open licenses.
            </p>
        </div>
        <div class="medium-3 large-3 medium-offset-1 large-offset-1 cell">
          <div class="column footer_contact">
            <h6><a href="/about/contact">We'd love to hear from you!</a></h6>
              <address>
                Creative Commons<br>
                PO Box 1866, Mountain View, CA 94042
              </address>
              <ul>
                <li><a href="mailto:info@creativecommons.org">info@creativecommons.org</a></li>
                <li><a href="tel:1-415-429-6753">1-415-429-6753</a></li>
              </ul>
          </div>
        </div>
        <div class="medium-3 large-3 medium-offset-1 large-offset-1 cell footer_license">
          <aside>
          <div xmlns:cc="https://creativecommons.org/ns#" about="https://creativecommons.org">
            <p><a class="subfoot" href="https://creativecommons.org/website-icons" target="blank">Icons</a>
               by The Noun Project.</p>
            <p class="website-credit">Website by <a class="subfoot" href="https://creativecommons.org"
            target="blank">CC</a>.</p>
          </div>
          </aside>
        </div>
      </div>
      <div class="large-12 cell">
        <div class="footer_disclaimer callout warning">
          This is the first release of the new CC Search, aggregating data from publicly available repositories of open content. CC has no control over the results that are returned. Do not assume that the results displayed in this search portal are under a CC license. You should always verify that the work is actually under a CC license by following the link. Since there is no registration to use a CC license, CC has no way to determine what has and hasn't been placed under the terms of a CC license. If you are in doubt you should contact the copyright holder directly, or try to contact the site where you found the content.
        </div>
      </div>
   </div>
</footer>
</template>

<script>
export default {
  name: 'footer-section',
};
</script>


<!-- Add "scoped" attribute to limit CSS to this component only -->
<style lang="scss" scoped>
.footer {
  padding: 30px;
  margin-bottom: 0;
  background-color: #f7f8f9;

  hr {
    max-width: 100%;
  }

  /* Small only */
  @media screen and (max-width: 39.9375em) {
    & {
      padding: 15px !important;
    }
  }
}

.footer_links {
  font-weight: 500;
  font-size: 1.1em;

  a:first-child {
    padding-left: 0;
  }
}

.footer_logo,
.footer_license-icons img {
  height: 2em;
  margin-bottom: 1em;
}

.footer_contact {
  ul {
    margin: .25em 0 0 0;
    list-style-type: none;
  }

  h6 a {
    color: #000;
    font-size: 1.1em;
    font-weight: 500;

    &:hover {
      bottom-border: 1px solid black;
    }
  }
}

.footer_disclaimer {
  font-weight: 500;
  margin: 0 -15px;

  /* Small only */
  @media screen and (max-width: 39.9375em) {
    & {
      margin: 0 -15px;
    }
  }
}
</style>
