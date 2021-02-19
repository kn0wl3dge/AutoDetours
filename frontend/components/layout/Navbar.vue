<template>
  <b-navbar fixed="top" class="navbar-dark bg-secondary shadow-lg">
    <nuxt-link class="navbar-brand" to="/">
      AutoDetours
    </nuxt-link>
    <b-navbar-nav class="ml-auto">
      <b-nav-item-dropdown text="User" right>
        <b-dropdown-item href="#">
          Account
        </b-dropdown-item>
        <b-dropdown-item href="#">
          Settings
        </b-dropdown-item>
      </b-nav-item-dropdown>
      <b-nav-item v-b-toggle.sidebar-right right>
        <b-icon icon="bell-fill" font-scale="1" />
      </b-nav-item>
    </b-navbar-nav>
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
