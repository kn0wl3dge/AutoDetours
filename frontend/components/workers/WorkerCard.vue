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
          <worker-state class="ml-3" :job="worker.job" />
        </b-col>
      </b-row>
      <b-row>
        <b-col sm="4">
          IP Address:
        </b-col>
        <b-col>
          {{ worker.ip }}
        </b-col>
      </b-row>
      <b-row>
        <b-col sm="4">
          Malware:
        </b-col>
        <b-col v-if="worker.job !== null">
          {{ worker.job.malware }}
        </b-col>
        <b-col v-else>
          Waiting for job...
        </b-col>
      </b-row>
      <b-row v-if="worker.job !== null">
        <b-col sm="4">
          Analysis Started:
        </b-col>
        <b-col>
          {{ $moment(worker.job.start_time).format('LLL') }}
        </b-col>
      </b-row>
      <b-row v-if="worker.job !== null">
        <b-col sm="4">
          Job Type:
        </b-col>
        <b-col>
          {{ worker.job.job_type }}
        </b-col>
      </b-row>
      <b-row v-if="worker.job !== null">
        <b-col sm="4">
          Job Time:
        </b-col>
        <b-col>
          {{ worker.job.job_time }}
        </b-col>
      </b-row>
    </b-card-text>
    <template #footer>
      <small class="text-muted">Registered {{ $moment(worker.registration_time).format('LLL') }}</small>
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
