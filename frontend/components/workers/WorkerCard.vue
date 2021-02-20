<template>
  <b-card
    :header="worker.id"
    class="m-4"
  >
    <b-card-text>
      <b-row>
        <b-col sm="4">
          State:
        </b-col>
        <b-col>
          {{ worker.state }}
          <worker-state class="ml-3" :state="worker.state" />
        </b-col>
      </b-row>
      <b-row>
        <b-col sm="4">
          Malware:
        </b-col>
        <b-col v-if="worker.malware !== null">
          {{ worker.malware }}
        </b-col>
        <b-col v-else>
          Waiting for a malware not analyzed yet...
        </b-col>
      </b-row>
    </b-card-text>
    <template #footer>
      <small class="text-muted">Registered {{ $moment(worker.date).format('LLL') }}</small>
    </template>
  </b-card>
</template>

<script>
export default {
  name: 'WorkerCard',
  props: {
    worker: { type: Object, default: () => { return {} } }
  }
}
</script>

<style scoped>
.card {
  width: 350px;
}
</style>
