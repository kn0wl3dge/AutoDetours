<template>
  <span>
    {{ state }}
    <b-icon
      :variant="mapping[state].color"
      font-scale="1.5"
      :animation="state === 'Running' ? 'spin' : ''"
      :icon="mapping[state].icon"
      class="mr-3 ml-2 align-middle"
    />
  </span>
</template>

<script>
export default {
  name: 'WorkerState',
  props: {
    job: { type: String, default: null }
  },
  data () {
    return {
      mapping: {
        Registered: {
          color: 'success',
          icon: 'check'
        },
        Running: {
          color: 'warning',
          icon: 'gear'
        }
      }
    }
  },
  computed: {
    state () {
      return this.job === null ? 'Registered' : 'Running'
    }
  }
}
</script>

<style lang="scss" scoped>
</style>
