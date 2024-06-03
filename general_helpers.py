
import csv

def dict_to_csv(file, data):
    columns = list(data.keys())
    rows = zip(*data.values())

    try:
        # # assert dict is formatted properly
        # num_entries = len(data[columns[0]])
        # for col in columns:
        #     assert(len(data[col]) == num_entries)
        
        # write to file
        with open(file, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(columns)  # Write the column headers
            writer.writerows(rows)    # Write the data rows
    except:
        # print([len(data[col]) for col in columns])
        print("Could not write to " + file)


