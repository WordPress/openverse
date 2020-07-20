<template>
  <footer class="main-footer">
    <div class="container">
      <div class="columns">
        <section
          role="complementary"
          aria-label="cc contact info"
          class="column"
        >
          <a
            aria-label="home"
            href="https://creativecommons.org"
            class="main-logo margin-bottom-bigger has-text-white"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              preserveAspectRatio="xMidYMid meet"
              viewBox="0 0 304 73"
            >
              <use href="/static/logos/cc/logomark.svg#logomark"></use>
            </svg>
          </a>
          <address class="margin-bottom-normal">
            <span class="is-block">Creative Commons</span>
            <span>PO Box 1866, Mountain View CA 94042</span>
          </address>
          <a
            href="mailto:info@creativecommons.org"
            aria-label="cc info email"
            class="mail is-block"
          >
            info@creativecommons.org
          </a>
          <a
            href="tel://+1-415-429-6753"
            aria-label="cc info telephone"
            class="phone"
            >+1-415-429-6753</a
          >

          <div class="margin-vertical-large">
            <a
              aria-label="instagram"
              href="https://www.instagram.com/creativecommons"
              class="social has-text-white"
              target="_blank"
              rel="noopener"
            >
              <i class="icon instagram margin-right-small is-size-4" />
            </a>
            <a
              aria-label="twitter"
              href="https://www.twitter.com/creativecommons"
              class="social has-text-white"
              target="_blank"
              rel="noopener"
            >
              <i class="icon twitter margin-right-small is-size-4" />
            </a>
            <a
              aria-label="facebook"
              href="https://www.facebook.com/creativecommons"
              class="social has-text-white"
              target="_blank"
              rel="noopener"
            >
              <i class="icon facebook margin-right-small is-size-4" />
            </a>
            <a
              aria-label="linkedin"
              href="https://www.linkedin.com/company/creative-commons/"
              class="social has-text-white"
              target="_blank"
              rel="noopener"
            >
              <i class="icon linkedin margin-right-small is-size-4" />
            </a>
          </div>
        </section>
        <div class="column is-half">
          <nav aria-label="footerlinks" class="footer-navigation">
            <ul class="menu">
              <li>
                <a
                  class="menu-item"
                  href="https://creativecommons.org/about/contact/"
                  >Contact</a
                >
              </li>
              <li>
                <a class="menu-item" href="https://creativecommons.org/privacy/"
                  >Privacy</a
                >
              </li>
              <li>
                <a
                  class="menu-item"
                  href="https://creativecommons.org/policies/"
                  >Policies</a
                >
              </li>
              <li>
                <a class="menu-item" href="https://creativecommons.org/terms/"
                  >Terms</a
                >
              </li>
            </ul>
          </nav>
          <div class="attribution margin-top-bigger">
            <p class="caption">
              Except where otherwise
              <a
                href="https://creativecommons.org/policies#license"
                target="_blank"
                rel="noopener"
                >noted</a
              >, content on this site is licensed under a
              <a
                href="https://creativecommons.org/licenses/by/4.0/"
                target="_blank"
                rel="noopener"
              >
                Creative Commons Attribution 4.0 International license </a
              >.
              <a
                href="https://fontawesome.com/"
                target="_blank"
                rel="noopener"
                class="has-text-white"
              >
                Icons by Font Awesome.
              </a>
            </p>

            <div class="margin-top-smaller">
              <i
                class="icon cc-logo margin-right-small is-size-4 is-color-white"
              />
              <i
                class="icon cc-by margin-right-small is-size-4 is-color-white"
              />
            </div>
          </div>
        </div>
        <div class="column">
          <section
            role="complementary"
            aria-label="donate section"
            class="donate-section"
          >
            <h5>Our work relies on you!</h5>
            <p>Help us keep the internet free and open.</p>
            <a
              aria-label="donate button"
              class="button small donate"
              href="http://creativecommons.org/donate"
            >
              <i
                class="icon cc-letterheart margin-right-small is-size-5 padding-top-smaller"
              />
              Donate now
            </a>
          </section>
        </div>
      </div>
    </div>
  </footer>
</template>

<script>
export default {
  name: 'footer-section',
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style lang="scss" scoped>
.donate,
.social {
  &:hover {
    text-decoration: none;
  }
}

.icon {
  vertical-align: middle;
}
</style>
