import pandas as pd

patients = pd.read_csv('../../data/predimed_records.csv')
groups = pd.read_csv('../../data/predimed_mapping.csv')

patients_with_group = patients.copy()
patients_with_group['group_2'] = 'n/a'

sorted_patients = patients_with_group.sort_values(['patient-id', 'location-id'])
sorted_groups = groups.sort_values(['patient-id', 'location-id'])

groups_idx = 0
patients_idx = 0

while True:
    row_groups = sorted_groups.iloc[groups_idx]
    location = row_groups['location-id']
    patient = row_groups['patient-id']

    row_patients = sorted_patients.iloc[patients_idx]

    location_patients = row_patients['location-id']
    patient_patients = row_patients['patient-id']
    if location_patients == location and patient_patients == patient:
        row_patients['group_2'] = row_groups['group']
        patients_idx += 1
    elif location_patients < location or patient_patients < patient:
        patients_idx += 1
    else:
        groups_idx += 1
        if groups_idx >= len(sorted_groups):
            break
    if patients_idx >= len(sorted_patients):
        break

print(sorted_patients['group_2'].value_counts(dropna=False))
