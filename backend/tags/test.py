# import our cooking_task from tasks
import tags
import extract


def launch_celery():
    json_content = extract.extract_json("../../loul.json")
    api_calls = extract.extract_funcname_list(json_content)
    result = tags.set_tags.delay(api_calls)
    print(result)


launch_celery()