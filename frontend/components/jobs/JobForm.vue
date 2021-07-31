<template>
  <b-modal
    v-if="malwares.length !== 0"
    id="jobModal"
    title="Add Jobs"
    centered
    @ok="submitJobs"
    @cancel="cancelJobs"
  >
    <template #default="">
      <div>
        <b-form-group>
          <template #label>
            <b>Choose your jobs:</b><br>
            <b-form-checkbox
              v-model="allSelected"
              :indeterminate="indeterminate"
              aria-describedby="jobtypes"
              aria-controls="jobtypes"
              @change="toggleAll"
            >
              {{ allSelected ? 'Un-select All' : 'Select All' }}
            </b-form-checkbox>
          </template>

          <template v-slot="{ ariaDescribedby }">
            <b-form-checkbox-group
              id="jobtypes"
              v-model="selected"
              :options="jobTypes"
              :aria-describedby="ariaDescribedby"
              name="jobtypes"
              class="ml-4"
              aria-label="Individual job type"
              stacked
            ></b-form-checkbox-group>
          </template>
        </b-form-group>

        <b>Choose your analysis time:</b><br>
        <b-form-input
          id="timeinput"
          v-model="selectedTime"
          class="mb-2"
          type="number"
          placeholder="Enter a duration in second (30s by default ...)"
        />

        <span>
          {{ selected.length === 0 ? 'Please select at least one job.' : `${selected.length} job${selected.length === 1 ? '' : 's'} will be submited.` }}
        </span>

      </div>
    </template>

    <template #modal-footer="{ ok, cancel }">
      <b-button size="md" variant="secondary" @click="cancel()">
        Cancel
      </b-button>
      <b-button
        size="md"
        variant="primary"
        @click="ok()"
        :disabled="selected.length === 0"
      >
        Submit Jobs
      </b-button>
    </template>
  </b-modal>
</template>

<script>

export default {
  name: 'JobForm',
  props: {
    malwares: {
      type: Array,
      default: () => { return [] }
    }
  },
  data () {
    return {
      jobTypes: ['Detours', 'PESieve'],
      selected: [],
      selectedTime: null,
      allSelected: false,
      indeterminate: false
    }
  },
  methods: {
    cancelJobs () {
      this.selected = []
    },
    submitJobs () {
      for (const malware of this.malwares) {
        for (const job of this.selected) {
          this.$api.jobs.create(
            {
              job_type: job,
              job_time: this.selectedTime || 30,
              malware: malware.sha256
            }
          )
        }
      }
    },
    toggleAll (checked) {
      this.selected = checked ? this.jobTypes.slice() : []
    }
  },
  watch: {
    selected (newValue, oldValue) {
      // Handle changes in individual flavour checkboxes
      if (newValue.length === 0) {
        this.indeterminate = false
        this.allSelected = false
      } else if (newValue.length === this.jobTypes.length) {
        this.indeterminate = false
        this.allSelected = true
      } else {
        this.indeterminate = true
        this.allSelected = false
      }
    }
  }
}
</script>

<style scoped>
</style>
