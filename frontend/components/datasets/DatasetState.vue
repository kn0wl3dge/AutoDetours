<template>
  <span>
    {{ mapping[state].text }}
    <b-icon
      :variant="mapping[state].color"
      font-scale="1.7"
      :animation="state === 'GENERATING' ? 'spin' : ''"
      :icon="mapping[state].icon"
      class="ml-2 align-middle"
    />
  </span>
</template>

<script>

export default {
  name: 'DatasetState',
  props: {
    state: { type: String, default: '' }
  },
  data () {
    return {
      mapping: {
        GENERATING: {
          color: 'warning',
          icon: 'gear',
          text: 'Generating'
        },
        GENERATED: {
          color: 'success',
          icon: 'check',
          text: 'Generated'
        }
      }
    }
  }
}
</script>

<style lang="scss" scoped>
</style>
