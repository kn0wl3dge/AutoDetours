<template>
  <b-col>
    <b-row>
      <b-col>
        <b-form-input v-model="filter" class="mb-4" type="search" placeholder="Enter your filter..." />
      </b-col>
      <b-col sm="2">
        <b-btn
          variant="primary"
          @click="generateDataset"
          block
        >
          Generate a Dataset
        </b-btn>
      </b-col>
    </b-row>
    <b-table
      id="datasets-table"
      :items="datasets"
      :fields="fields"
      :filter="filter"
      :per-page="perPage"
      :current-page="currentPage"
      hover
      striped
    >
      <template #cell(creation_time)="row">
        {{ $moment(row.item.upload_time).format('LLL') }}
      </template>

      <template #cell(state)="row">
        <dataset-state class="ml-2" :state="row.item.status" />
      </template>

      <template #cell(download)="row">
        <b-btn
          variant="primary"
          v-b-modal="'jobModal'"
          @click="downloadDataset(row.item.id)"
          size="sm"
        >
          Download
        </b-btn>
      </template>

      <template #cell(delete)="row">
        <b-btn
          variant="danger"
          v-b-modal="'jobModal'"
          @click="deleteDataset(row.item.id)"
          size="sm"
        >
          Delete
        </b-btn>
      </template>
    </b-table>
    <b-pagination
      v-model="currentPage"
      :total-rows="rows"
      :per-page="perPage"
      aria-controls="datasets-table"
      align="center"
    />
  </b-col>
</template>

<script>
import DatasetState from './DatasetState.vue'

export default {
  name: 'DatasetTable',
  components: { DatasetState },
  props: {
    datasets: {
      type: Array,
      default: () => { return [] }
    }
  },
  data () {
    return {
      filter: '',
      perPage: 10,
      currentPage: 1,
      fields: [
        {
          key: 'creation_time',
          label: 'Creation Time',
          sortable: true,
          class: 'text-center'
        },
        {
          key: 'state',
          label: 'State',
          sortable: true,
          class: 'text-center'
        },
        {
          key: 'download',
          label: 'Download',
          class: 'text-center'
        },
        {
          key: 'delete',
          label: 'Delete',
          class: 'text-center'
        }
      ]
    }
  },
  computed: {
    rows () {
      return this.datasets.length
    }
  },
  methods: {
    generateDataset () {
      this.$api.datasets.create()
    },
    downloadDataset (id) {
      window.open(`/api/datasets/${id}/download/`)
    },
    deleteDataset (id) {
      this.$api.datasets.delete(id)
    }
  }
}
</script>

<style scoped>
</style>
