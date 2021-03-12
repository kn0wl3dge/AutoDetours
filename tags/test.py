# import our cooking_task from tasks
import tags
import extract
import rule


# Dishes ordered for Table-1
jsona = extract.extract_json("../../loul.json")
list_a = extract.extract_funcname_list(jsona)
rules = rule.get_db_rules('db_rules')
result = tags.set_tags.delay(jsona, rules)
# Call the cooking_task.delay task with input parameters defined for that Task.
# prints the task id
print(result)