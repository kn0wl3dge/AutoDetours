<template>
  <div
    id="sidebar-wrapper"
    :class="{ 'sidebar-collapsed': !display, 'sidebar-extended': display }"
    class="bg-secondary shadow-lg"
  >
    <div class="list-group">
      <sidebar-entry
        v-for="item in items"
        :key="item.key"
        :name="item.name"
        :href="item.href"
        :icon="item.icon"
      />
      <br>
      <br>
      <br>
      <br>
      <sidebar-entry href="/about" name="About" icon="question-circle" />
      <a
        href="javascript:void(0)"
        class="menu-item list-group-item list-group-item-action justify-content-between d-flex bg-secondary"
        @click="displayNavbar"
      ><h5>Collapse</h5>
        <b-icon
          v-if="display"
          key="extended"
          icon="chevron-double-left"
          font-scale="2"
          pill
        /><b-icon
          v-else
          key="collapsed"
          icon="chevron-double-right"
          font-scale="2"
          pill
        />
      </a>
    </div>
  </div>
</template>

<script>
import SidebarEntry from './SidebarEntry'
export default {
  name: 'Sidebar',
  components: { SidebarEntry },
  data () {
    return {
      display: true,
      items: [
        { key: 1, name: 'Dashboard', href: '/', icon: 'graph-up' },
        { key: 2, name: 'Malwares', href: '/malwares', icon: 'bug' },
        { key: 3, name: 'Datasets', href: '/datasets', icon: 'folder2-open' },
        { key: 4, name: 'Workers', href: '/workers', icon: 'box' },
        {
          key: 5,
          name: 'Add a Malware',
          href: '/malwares/add',
          icon: 'plus-square'
        },
        { key: 6, name: 'Rules', href: '/rules', icon: 'gear' }
      ]
    }
  },
  methods: {
    displayNavbar () {
      this.display = !this.display
      this.$root.$emit('displayNavbar', this.display)
    }
  }
}
</script>

<style lang="scss" scoped>
  @import 'assets/scss/_variables.scss';
  .btn:focus {
    outline: 0;
    box-shadow: 0 0 0 0 rgba(0,0,0,0);
  }

  .menu-item {
    align-items: center;
    color: $warning;
  }
  h5 {
    margin-bottom: 0;
  }

  .list-group-item {
    border-top: 1px solid $dark;
  }

  #sidebar-wrapper {
    width: 15rem;
    position: fixed;
    top: 54px;
    min-height: 100vh;
    -webkit-transition: margin .25s ease-out;
    -moz-transition: margin .25s ease-out;
    -o-transition: margin .25s ease-out;
    transition: margin .25s ease-out;
  }

  .sidebar-collapsed {
    margin-left: -10.5rem;
  }

  .sidebar-extended {
    margin-left: 0;
  }

  @media (min-width: 768px) {
    .sidebar-collapsed {
      margin-left: -10.5rem;
    }

    .sidebar-extended {
      margin-left: 0;
    }
  }
</style>
