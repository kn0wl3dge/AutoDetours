<template>
  <b-col>
    <b-container fluid>
      <h3>Settings</h3>
      <b-row class="mb-4" />
    </b-container>

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
import Tags from '../../components/settings/Tags'
export default {
  components: { Tags }
}

</script>

<style scoped>
</style>
