<script>
import { PolarArea } from 'vue-chartjs'
export default {
  extends: PolarArea,
  props: {
    chartdata: {
      type: Object,
      default: null
    },
    options: {
      type: Object,
      default: null
    }
  },
  mounted () {
    this.renderChart(this.chartdata, this.options)
  }
}
</script>
<style scoped></style>
