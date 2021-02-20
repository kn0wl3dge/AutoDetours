<template>
  <b-icon
    :variant="mapping[state].color"
    font-scale="1.5"
    :animation="state === 'TASKED' ? 'spin' : ''"
    :icon="mapping[state].icon"
    class="mr-3 align-middle"
  />
</template>

<script>
export default {
  name: 'WorkerState',
  props: {
    state: { type: String, default: '' }
  },
  data () {
    return {
      mapping: {
        REGISTERED: {
          color: 'success',
          icon: 'check'
        },
        TASKED: {
          color: 'warning',
          icon: 'gear'
        },
        FINISHED: {
          color: 'danger',
          icon: 'exclamation-circle'
        }
      }
    }
  }
}
</script>

<style lang="scss" scoped>
</style>
