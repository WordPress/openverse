<template>
<footer class="footer callout large secondary">
   <article class="grid-container full">
      <div class="large-3 cell">
          <ul class="footer_links menu">
            <li><a href="/contact">Contact</a></li>
            <li><a href="/privacy">Privacy</a></li>
            <li><a href="/policies">Policies</a></li>
            <li><a href="/terms">Terms</a></li>
            <li><a href="/faq">FAQ</a></li>
          </ul>
      </div>
      <hr>
      <div class="grid-x grid-margin-x">
        <div class="large-3 cell">
          <img class="footer_logo" src="../assets/cc-logo_large_black.png">
            <p>
              We’re changing the way people share around the world
              with our Global Community and 1.4 billion pieces of
              content under our simple, easy-to-use open licenses.
            </p>
        </div>
        <div class="large-3 large-offset-1 cell">
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
        <div class="large-3 large-offset-1 cell footer_license">
          <div class="footer_license-icons">
            <a rel="license" href="https://creativecommons.org/licenses/by/4.0/"
               title="Creative Commons Attribution 4.0 International license">
              <img src="../assets/cc-icon_large.png">
              <img src="../assets/cc-by-icon_large.png">
            </a>
          </div>
          <aside>
          <div xmlns:cc="https://creativecommons.org/ns#" about="https://creativecommons.org">
            <p>Except where otherwise <a class="subfoot" href="/policies#license">noted</a>,
              content on this site is licensed under a <a
              class="subfoot" href="https://creativecommons.org/licenses/by/4.0/"
              rel="license">Creative Commons Attribution 4.0 International license</a>.
              <a class="subfoot" href="/website-icons" target="blank">Icons</a>
               by The Noun Project.</p>
            <p class="website-credit">Website by <a class="subfoot" href="http://affinitybridge.com/"
            target="blank"> Affinity Bridge</a>.</p>
          </div>
          </aside>
        </div>
      </div>
   </article>
</footer>
</template>

<script>
export default {
  name: 'footer-section',
  data() {
    return {
      msg: '',
    };
  },
};
</script>


<!-- Add "scoped" attribute to limit CSS to this component only -->
<style lang="scss" scoped>

.footer {
  padding: 30px;
  margin-bottom: 0;

  hr {
    max-width: 100%;
  }
}

.footer_links {
  font-weight: 700;
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
</style>
