<template>
  <div class="navbar">
    <img id="logo" src="../assets/ccsearch.png">
    <div class="navPanel">
      <div class="topnav-left">
        <form id="searchForm">
          <input id="searchInput" type="text">
          <button type="submit" id="searchButton">
            <img id="searchButtonImage" src="../assets/ccbutton.png">
          </button>
	</form>
      </div>
      <div class="bottomnav-left">
        <p id="selected">Images</p>
      </div>
      <p class="signIn">Sign in</p>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Navbar',
  props: {
    msg: String
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
.navbar {
  position: absolute;
  background-color: #03a7ff;
  width: 100%;
  height: 130px;
  white-space: nowrap;
}
#logo {
  float: left;
  height: 110px;
  width: auto;
  padding-left: 10px;
  padding-top: 10px;
}
.navPanel {
  position: absolute;
  left: 250px;
  width: 80%;
  height: 130px;
  white-space: nowrap;
}
.topnav-left {
  height: 60%;
  width: 70%;
  white-space: nowrap;
}
.bottomnav-left {
  width: 100%;
}

.signIn {
  position: relative;
  float: right;
  bottom: 90px;
  font-size: 17px;
  color: #ffffff;
  font-weight: bold;
}
#searchForm {
  height: 100%;
  display: inline;
}
#searchButton {
  position: relative;
  top: 18px;
  background-color: Transparent;
  background-repeat: no-repeat;
  border: none;
  cursor:pointer;
  overflow: hidden;
  outline: none;
  height: 100%;
  width: auto;
  margin-left: -50px;
}
#searchButtonImage {
  height: 40%;
  width: auto;
}
#searchInput {
  position: relative;
  top: 10px;
  height: 40px;
  box-sizing: border-box;
  border: 1px solid grey;
  border-radius: 3px;
  box-shadow: 1px 1px 10px;
  font-size: 23px;
  width: 500px;
}
#selected {
  display: inline;
  position: relative;
  top: 19px;
  color: #000000;
  font-size: 17px;
  font-weight: bold;
}
a {
  color: #ffffff;
}
</style>
