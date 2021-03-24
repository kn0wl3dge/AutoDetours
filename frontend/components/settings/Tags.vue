<template>
  <b-col>
    <b-form-file
      id="finput"
      v-model="files"
      :state="null"
      size="md"
      placeholder="Choose a rule file or drop it here..."
      drop-placeholder="Drop files here..."
      class="mb-2"
      multiple
    />
  </b-col>
</template>
<script>
  export default {
    name: 'Tags',
    data() {
      return {
        files: null
      }
    }
  }
</script>

<style scoped></style>
