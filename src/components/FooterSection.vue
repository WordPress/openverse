<template>
<footer class="footer callout large secondary">
   <div class="grid-container full">
      <div class="grid-x grid-margin-x grid-margin-y">
        <div class="medium-3 cell">
          <img class="footer_logo" src="../assets/cc-logo_white.png">
          <div class="cc-footer-links">
            <div class="menu-footer-links-container">
                <ul id="menu-footer-links" class="menu">
                    <li class="menu-item menu-item-type-post_type menu-item-object-page"><a href="https://creativecommons.org/about/contact/">Contact</a></li>
                    <li class="menu-item menu-item-type-post_type menu-item-object-page"><a href="https://creativecommons.org/privacy/">Privacy</a></li>
                    <li class="menu-item menu-item-type-post_type menu-item-object-page"><a href="https://creativecommons.org/policies/">Policies</a></li>
                    <li class="menu-item menu-item-type-post_type menu-item-object-page"><a href="https://creativecommons.org/terms/">Terms</a></li>
                </ul>
            </div>
        </div>
      </div>
        <div class="medium-3 large-3 medium-offset-1 large-offset-1 cell">
          <div class="column footer_contact">
            <h6><a href="https://creativecommons.org/about/contact/">We'd love to hear from you!</a></h6>
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
          <div xmlns:cc="https://creativecommons.org/ns#"
               about="https://creativecommons.org">
            <p><a class="subfoot"
                   href="https://creativecommons.org/website-icons"
                   target="blank">Icons</a>
               by The Noun Project.</p>
            <p class="website-credit">Website by <a class="subfoot"
               href="https://creativecommons.org"
            target="blank">CC</a>.</p>
          </div>
          </aside>
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
  background-color: #2b2b2b;
  width: 100%;

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
  height: 4em;
  margin-bottom: 1em;
}

.footer_contact {
  ul {
    margin: .25em 0 0 0;
    list-style-type: none;
  }

  h6 a {
    color: #fff;
    font-size: 1.1em;
    font-weight: 500;

    &:hover {
      border-bottom: 1px solid black;
    }
  }
}

address {
  color: #999;
}

.menu-item a {
  color: #999;
}

p {
  color: #999;
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
