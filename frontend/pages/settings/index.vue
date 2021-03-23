<template>
  <b-col>
    <b-container fluid>
      <h3>Settings</h3>
      <b-row class="mb-4" />
    </b-container>

      <label for="rule_name">Rule name:</label>
      <b-form-input
        id="rule_name"
        v-model="form.rule"
        class="mb-2"
        type="text"
        placeholder="Enter a rule name"
      />

      <label for="functions_list">Function list (separate each function with ;):</label>
      <b-form-input
        id="functions_list"
        v-model="form.functions"
        class="mb-2"
        type="text"
        placeholder="Enter functions names"
      />

      <label for="tag_name">Tag name:</label>
      <b-form-input
        id="tag_name"
        v-model="form.tag"
        class="mb-2"
        type="text"
        placeholder="Enter a tag name"
      />

    <b-btn
      size="lg"
      block class="mb-2 mt-4"
      :disabled="disabled_button"
      @click="uploadRule"
    >
      Upload rule
    </b-btn>

  </b-col>
</template>

<script>
//import Tags from '../../components/settings/Tags'
export default {
    async asyncData ({ app }) {
      const list = await app.$axios.$get('/rules/')
      console.log(list)
      return {
        rules_list : list
      }
    },
    name: 'RuleForm',
    data () {
    return {
      fields: [
          {
            key: 'name',
            label: 'Name',
            sortable: true
          }
        ],
      rule_list : [],
        form : {
          rule: null,
          functions: null,
          tag: null
        }
      }
    },
    computed: {
      disabled_button () {
        return  this.form.tag == null || this.form.rule == null || this.form.functions == null
      },
      rows () {
        return this.rules_list.length
    }
    },
    methods: {
      async uploadRule () {
        this.form.functions = this.form.functions.split(';')
        const presp = await this.$axios.$post('/rules/', this.form)
      }
    }
  }

</script>

<style scoped>
</style>
