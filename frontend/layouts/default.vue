<template>
  <div id="wrapper" class="d-flex">
    <sidebar />
    <div
      id="page-content-wrapper"
      :class="{
        'page-content-wrapper-extended': display,
        'page-content-wrapper-collapsed': !display
      }"
    >
      <navbar />
      <nuxt />
    </div>
  </div>
</template>

<script>
import Navbar from '../components/layout/Navbar'
import Sidebar from '../components/layout/sidebar/Sidebar'
export default {
  components: { Sidebar, Navbar },
  data () {
    return { display: true }
  },
  mounted () {
    this.$root.$on('displayNavbar', (display) => {
      this.display = display
    })
  }
}
</script>

<style>
  #page-content-wrapper {
    min-width: 0;
    margin-top: 4.5rem;
    margin-right: 1rem;
    width: 100%;
    -webkit-transition: margin .25s ease-out;
    -moz-transition: margin .25s ease-out;
    -o-transition: margin .25s ease-out;
    transition: margin .25s ease-out;
  }

  @media (min-width: 768px) {
    .page-content-wrapper-extended {
      margin-left: 16rem;
    }
    .page-content-wrapper-collapsed {
      margin-left: 5rem;
    }
  }
</style>
