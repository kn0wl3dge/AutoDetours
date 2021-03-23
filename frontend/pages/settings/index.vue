<template>
  <b-col>
    <b-container fluid>
      <h3>Settings</h3>
      <b-row class="mb-4" />
    </b-container>

      <b-button size="lg" class="mb-2 mt-4" @click="toggle_form">
        Add a new rule
      </b-button>

      <label for="rule_name" v-if="show_form">Rule name:</label>
      <b-form-input
        v-if="show_form"
        id="rule_name"
        v-model="form.rule"
        class="mb-2"
        type="text"
        placeholder="Enter a rule name"
        :disabled="exist"
      />

      <label for="functions_list" v-if="show_form">Function list (separate each function with ;):</label>
      <textarea
        v-if="show_form"
        id="functions_list"
        v-model="form.functions"
        class="form-control"
        type="text"
        placeholder="Enter functions names"
        rows="3"
      ></textarea>

      <label for="tag_name" v-if="show_form">Tag name:</label>
      <b-form-input
        v-if="show_form"
        id="tag_name"
        v-model="form.tag"
        class="mb-2"
        type="text"
        placeholder="Enter a tag name"
      />

    <b-btn
      v-if="update_rule"
      size="lg"
      block class="mb-2 mt-4"
      :disabled="disabled_button"
      @click="uploadRule"
    >
      Update rule
    </b-btn>

    <b-btn
      v-else
      size="lg"
      block class="mb-2 mt-4"
      :disabled="disabled_button"
      @click="uploadRule"
    >
      Upload rule
    </b-btn>

    <table class="table table-striped">
      <thead>
        <tr>
          <th>Name</th>
          <th>Tag</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="rule in rules_list" :key="rule.name">
          <td>{{ rule.name }}</td>
          <td>{{ rule.tag }}</td>
          <td>
            <b-btn
              size="sm"
              block class="mr-2 ml-2"
              @click="modify(rule)"
            >
              Modify Rule
            </b-btn>
          </td>
          <td>
            <b-btn
              size="sm"
              block class="mr-2 ml-2"
              variant="danger"
              @click="delete_rule(rule.name)"
            >
              Delete Rule
            </b-btn>
          </td>
        </tr>
      </tbody>
    </table>
  </b-col>
</template>

<script>
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
      update_rule: false,
      show_form : false,
      rules_list : [],
      exist: false,
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
      }
    },
    methods: {
      async uploadRule () {
        console.log(this.rules_list)
        this.form.functions = this.form.functions.split(';')
        const presp = await this.$axios.$post('/rules/', this.form)
      },
      async modify(rule) {
        console.log(rule.name)
        this.form.rule = rule.name
        this.form.functions = rule.patterns.join(';')
        this.form.tag = rule.tag
        this.exist = true
        this.show_form = true
        this.update_rule = true
      },
      async toggle_form() {
        this.form.rule = null
        this.form.functions = null
        this.form.tag = null
        this.show_form = true
        this.exist = false
        this.update_rule = false
      },
      async delete_rule(name) {
        const presp = await this.$axios.$delete('/rules/?rule='+name)
      }
    }
  }

</script>

<style scoped>
</style>
