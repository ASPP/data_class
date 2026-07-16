"""Create an untidy "second batch" of predimed patients.

We draw a small sample (without replacement) from the clean predimed table and
deliberately make it untidy in two ways:

-  two variables in one column: `sex_age` 
   --> needs string split to tidy it
-  one variable in wide format: `smoke_never`, `smoke_former` and `smoke_current`, with a
   1 in the column that matches the patient and 0 in the others. 
   --> needs melt to tidy it 
"""

from pathlib import Path

import pandas as pd


SOURCE = "processed_data_predimed.csv"
TARGET = "predimed_2.csv"

N = 400
SEED = 352


def main():
    df = pd.read_csv(SOURCE)
    sample = df.sample(n=N, replace=False, random_state=SEED).reset_index(drop=True)

    # give this batch new patient-ids 
    new_id_start = int(df["patient-id"].max()) + 1
    out = pd.DataFrame()
    out["patient-id"] = range(new_id_start, new_id_start + N)
    out["group"] = sample["group"]

    # untidy 1: two variables (sex and age) glued into one column
    out["sex_age"] = sample["sex"] + "_" + sample["age"].astype(str)

    # untidy 2: one variable (smoking status) spread across three
    # indicator columns (a 1 marks the patient's status, 0 otherwise)
    out["smoke_never"] = (sample["smoke"] == "Never").astype(int)
    out["smoke_former"] = (sample["smoke"] == "Former").astype(int)
    out["smoke_current"] = (sample["smoke"] == "Current").astype(int)

    # event already coded as 1 / 0
    out["event"] = sample["event"].map({"Yes": 1, "No": 0})

    out.to_csv(TARGET, index=False)
    print("wrote", TARGET, "shape", out.shape)
    print(out.head())


if __name__ == "__main__":
    main()
