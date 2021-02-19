<template>
  <nuxt-link
    :to="href"
    class="menu-item list-group-item list-group-item-action justify-content-between d-flex bg-secondary"
  >
    <h5>{{ name }}</h5><b-icon :icon="icon" font-scale="2" pill />
  </nuxt-link>
</template>

<script>
export default {
  name: 'SidebarEntry',
  props: {
    name: { type: String, default: '' },
    href: { type: String, default: '' },
    icon: { type: String, default: '' }
  }
}
</script>

<style lang="scss" scoped>
  @import 'assets/scss/_variables.scss';
  h5 {
    margin-bottom: 0;
  }
</style>
