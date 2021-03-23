<template>
  <b-col>
    <b-container fluid>
      <h3>Rules</h3>
      <b-row class="mb-4" />
    </b-container>

      <b-button size="lg" class="mb-2 mt-4" @click="toggle_form">
        Add a new rule
      </b-button>

      <div v-if="show_form">
        <label for="rule_name" v-if="show_form">Rule name:</label>
        <b-form-input
          id="rule_name"
          v-model="form.rule"
          class="mb-2"
          type="text"
          placeholder="Enter a rule name"
          :disabled="exist"
        />

        <label for="functions_list" v-if="show_form">Function list:</label>
        <b-form-tags
          id="functions_list"
          v-model="form.functions"
          class="form-control"
          separator=" ,;"
          placeholder="Enter new functions separated by space, comma or semicolon"
          remove-on-delete
          no-add-on-enter
        ></b-form-tags>

        <label for="tag_name" v-if="show_form">Tag name:</label>
        <b-form-input
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
      </div>
    <b-form-input v-model="filter" class="mb-4" type="search" placeholder="Enter your filter..." />
    <template>
      <b-table
        class="table table-striped"
        :per-page="perPage"
        :current-page="currentPage"
        :filter="filter"
        :fields="fields"
        hover
        striped
        :items="rules_list"
        id="rule-table"
      >
        <template #cell(name)="data">
          {{ data.item.name }}
        </template>

        <template #cell(tag)="data">
          {{ data.item.tag }}
        </template>

        <template #cell(modify)="data">
          <b-btn
              size="sm"
              block class="mr-2 ml-2"
              @click="modify(data.item)"
          >
            Modify Rule
          </b-btn>
        </template>

        <template #cell(delete)="data">
          <b-btn
            size="sm"
            block class="mr-2 ml-2"
            variant="danger"
            @click="delete_rule(data.item.name)"
          >
            Delete Rule
          </b-btn>
        </template>

      </b-table>
    </template>
    <b-pagination
      v-model="currentPage"
      :per-page="perPage"
      :total-rows="rows"
      aria-controls="rule-table"
      align="center"
    />
  </b-col>
</template>

<script>
export default {
    async asyncData ({ app }) {
      const list = await app.$axios.$get('/rules/')
      return {
        rules_list : list
      }
    },
    name: 'RuleForm',
    data () {
    return {
      update_rule: false,
      show_form : false,
      filter : null,
      perPage: 10,
      currentPage: 1,
      rules_list : [],
      fields: [
        {
          key: 'name',
          label: 'Name',
          sortable: true
        },
        {
          key: 'tag',
          label: 'Tag',
          sortable: true
        },
        {
          key: 'modify',
          label: 'Modify',
          sortable: false
        },
        {
          key: 'delete',
          label: 'Delete',
          sortable: false
        }
      ],
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
      },
      rows () {
        return this.rules_list.length
      }
    },
    methods: {
      async uploadRule () {
        console.log(this.rules_list)
        await this.$axios.$post('/rules/', this.form)
        this.rules_list.push(this.form)
      },
      async modify(rule) {
        console.log(rule.name)
        this.form.rule = rule.name
        this.form.functions = rule.functions
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
        await this.$axios.$delete('/rules/?rule='+name)
        this.rules_list.splice(this.rules_list.findIndex((el) => el.name === name), 1)
      }
    }
  }

</script>

<style scoped>
</style>
