<template>
  <b-navbar fixed="top" class="navbar-dark bg-secondary shadow-lg">
    <nuxt-link class="navbar-brand" to="/">
      <img src="~/assets/img/logo-small.png" height="30" class="mr-2 pb-1">
      AutoDetours
    </nuxt-link>
  </b-navbar>
</template>

<script>
export default {
  name: 'Navbar',
  components: {}
}
</script>

<style lang="scss">
  @import '../../assets/scss/_variables';
  .navbar-brand {
    color: $warning !important;
    font-size: 1.6rem;
    padding-bottom: 0;
    padding-top: 0;
  }
  .navbar-dark .navbar-brand:hover, .navbar-dark .navbar-brand:focus {
    color: $warning !important;
  }
  .navbar {
    padding: 0.5rem 1rem;
  }
  .navbar-dark .navbar-nav .nav-item .nav-link {
    color: $warning !important;
  }
</style>
