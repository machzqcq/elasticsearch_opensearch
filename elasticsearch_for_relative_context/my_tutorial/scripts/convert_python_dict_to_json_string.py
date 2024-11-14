# There might still be issues where apostrophe or single quote is inside the string
# for e.g after applying below, we get "RELATED_AI_DATA_NAMES_LIST":[\"Please Don"t Code\"]
# But we focus on related_tasks for now
import pandas as pd
import pprint
BASE_DIR = "/home/ubuntu/git-projects/personal/github.com/vm_superset/comprehensive.io/ai_work/there_is_an_ai_for_that"

COLUMNS_NEEDED = ["TASK_NAME","RELATED_AI_DATA_NAMES_LIST","RELATED_TASKS_NAMES_LIST",
                  "FIRST_SEEN_DATE","RELATED_AI_DATA_IDS_LIST"]
df_tasks = pd.read_parquet(f"{BASE_DIR}/tasks/there_is_an_ai_for_that_tasks.parquet")[COLUMNS_NEEDED]
df_tasks.info()

#OLD way
# print(df_tasks.head(1).to_json(orient="records"))
# print(df_tasks.sample(1).to_json(orient="records"))
df_code_related = df_tasks[df_tasks["TASK_NAME"].str.contains("Code",case=False)].head(2)

converted_string = str(df_code_related.head(2).to_json(orient="records")).replace("\'", '"').replace('\"[', '[').replace(']\"', ']') #.replace('\\"', '"')    
with open(f"../data/sample_tasks.json", "w") as f:
    f.write(converted_string)
