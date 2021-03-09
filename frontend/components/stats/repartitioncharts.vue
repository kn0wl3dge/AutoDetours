<template>
  <doughnut-chart v-if="loaded" :chartdata="chartdata" :options="options" />
</template>
<script>
import DoughnutChart from './chart'
export default {
  name: 'repartitionchart',
  components: { doughnutchart },
  props: {
    top5: { type: Array, default () { return [] } }
  },
  data () {
    return {
      chartdata: null,
      options: null,
      loaded: false
    }
  },
  mounted () {
    this.chartdata = {
      datasets: [{
        data: [7, 3, 1],
        backgroundColor: ['#E74C3C', '#fd7e14', '#18BC9C', '#3498DB', '#6610f2']
      }],
      labels: ["Analyzed", "Test", "Passed"]
    }
    this.options = {
      responsive: true,
      maintainAspectRatio: false,
      title: {
        display: false
      }
    }
    this.loaded = true
  },
  methods: {
    getLabels (main) {
      const labels = []
      for (let i = 0; i < main.length; i++) {
        labels.push(main[i].name)
      }
      return labels
    },
    getData (main) {
      const d = []
      for (let i = 0; i < main.length; i++) {
        d.push(Number(main[i].nbr))
      }
      return d
    }
  }
}
</script>
<style scoped>
</style>