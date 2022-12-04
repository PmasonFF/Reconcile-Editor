"""This script was written in Python 3.7 "out of the box" and should run without any added packages."""
import csv
import json

# File location section :
location = 'digging-up-the-oceans-past-classifications_demo.csv'
out_location = 'flatten_digging-up-the-oceans-past_classifications_demo.csv'
sorted_location = 'flatten_digging-up-the-oceans-past_class_sorted_demo.csv'


# Function definitions needed for any blocks.
def include(class_record): # to select classifications based on workflow_id and version
    if int(class_record['workflow_id']) in [20922]:
        pass
    else:
        return False
    if float(class_record['workflow_version']) >= 141.0:
        pass
    else:
        return False
    # otherwise :
    return True


# Set up the output file structure with desired fields:
# prepare the output file and write the header
with open(out_location, 'w', newline='', encoding='utf-8') as file:
    fieldnames = ['classification_id',
                  'subject_id',
                  'user_name',
                  'workflow_id',
                  'workflow_version',
                  'Filename'
                  ]
    fieldnames.extend(['location' + str(i) for i in range(1, 7)])
    fieldnames.extend(['date' + str(i) for i in range(1, 7)])
    fieldnames.extend([r'lat/long' + str(i) for i in range(1, 7)])
    fieldnames.extend(['depth' + str(i) for i in range(1, 7)])
    fieldnames.extend(['sampleEffort' + str(i) for i in range(1, 7)])
    fieldnames.extend(['count' + str(i) for i in range(1, 7)])
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()

    # this area for initializing counters:
    i = 0
    j = 0

    #  open the zooniverse data file using dictreader, and load the more complex json strings as python objects
    with open(location, encoding='utf-8') as f:
        r = csv.DictReader(f)
        for row in r:
            i += 1
            if include(row) is True:
                j += 1
                annotations = json.loads(row['annotations'])
                subject_data = json.loads(row['subject_data'])

                # pull metadata from the subject data field
                subjectdata = subject_data[(row['subject_ids'])]
                try:
                    filename = subjectdata['Filename']
                except KeyError:
                    filename = ''

                # reset the field variables for each new row
                loc = ['' for i in range(0, 6)]  # location
                date = ['' for i in range(0, 6)]  # date
                lat_long = ['' for i in range(0, 6)]  # lat/long
                depth = ['' for i in range(0, 6)]  # depth
                sample = ['' for i in range(0, 6)]  # sampleEffort
                count = ['' for i in range(0, 6)]  # location

                # loop over the tasks
                for task in annotations:

                    # Free Transcription locations
                    try:
                        if task['task'] == 'T7':  # combo task for loacations
                            for sub_task in task['value']:
                                if sub_task['task'] == 'T13':  # this workflow had on task number out of order
                                    loc[0] = sub_task['value']
                                for i1 in range(1, 6):
                                    if sub_task['task'] == 'T' + str(i1 + 7):
                                        loc[i1] = sub_task['value']
                    except KeyError:
                        pass

                    # Free Transcription dates
                    try:
                        if task['task'] == 'T14':
                            for sub_task in task['value']:
                                for i2 in range(0, 6):
                                    if sub_task['task'] == 'T' + str(i2 + 15):
                                        date[i2] = sub_task['value']
                    except KeyError:
                        pass

                    # Free Transcription lat/long
                    try:
                        if task['task'] == 'T21':
                            for sub_task in task['value']:
                                for i3 in range(0, 6):
                                    if sub_task['task'] == 'T' + str(i3 + 22):
                                        lat_long[i3] = sub_task['value']
                    except KeyError:
                        pass

                    # Free Transcription depth
                    try:
                        if task['task'] == 'T28':
                            for sub_task in task['value']:
                                for i4 in range(0, 6):
                                    if sub_task['task'] == 'T' + str(i4 + 29):
                                        depth[i4] = sub_task['value']
                    except KeyError:
                        pass

                    # Free Transcription sampleEffort
                    try:
                        if task['task'] == 'T35':
                            for sub_task in task['value']:
                                for i5 in range(0, 6):
                                    if sub_task['task'] == 'T' + str(i5 + 36):
                                        sample[i5] = sub_task['value'].replace('\n', ' ')
                    except KeyError:
                        pass

                    # Free Transcription count
                    try:
                        if task['task'] == 'T42':
                            for sub_task in task['value']:
                                for i6 in range(0, 6):
                                    if sub_task['task'] == 'T' + str(i6 + 43):
                                        count[i6] = sub_task['value']
                    except KeyError:
                        pass
                # This set up the writer to match the field names above and the variable names of their values:
                new_row = {'classification_id': row['classification_id'],
                           'subject_id': row['subject_ids'],
                           'user_name': row['user_name'],
                           'workflow_id': row['workflow_id'],
                           'workflow_version': row['workflow_version'],
                           'Filename': filename
                           }
                for j1 in range(1, 7):
                    new_row['location' + str(j1)] = loc[j1 - 1]
                for j2 in range(1, 7):
                    new_row['date' + str(j2)] = date[j2 - 1]
                for j3 in range(1, 7):
                    new_row[r'lat/long' + str(j3)] = lat_long[j3 - 1]
                for j4 in range(1, 7):
                    new_row['depth' + str(j4)] = depth[j4 - 1]
                for j5 in range(1, 7):
                    new_row['sampleEffort' + str(j5)] = sample[j5 - 1]
                for j6 in range(1, 7):
                    new_row['count' + str(j6)] = count[j6 - 1]
                writer.writerow(new_row)

        # This area prints some basic process info and status
        print('\n', i, 'lines read and inspected', j, 'records processed and copied')
