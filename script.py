import glob
import re
import csv

path = r'./**/UnitTestZK/*output.txt'
files = glob.glob(path, recursive=True)

result = []
tests_name = set()

for f in files:
    with open(f, "r") as obj:
        test_name = ''
        unit_test_name = ''
        test_method_calls = {}

        for line_num, x in enumerate(obj, 1):
            # Extract the line number from the stack trace element
            line_number_match = re.search('stack\strace\selement:\s*(.*)\.(.*)\s+\(Line\s+(\d+)\)', x)
            line_number = '-' if not line_number_match else line_number_match.group(3)

            # Extract the Unit Test from the line
            unit_test_match = re.search('\[wasabi\]\s+org\.(.*)\.runTest\s+', x)
            if unit_test_match:
                unit_test_name = unit_test_match.group(1)

            # Extract the method name from the stack trace element
            method_name = line_number_match.group(2) if line_number_match else 'unknown'

            # Extract the ID from the line
            id_match = re.search('\[wasabi\]\sRetry\sLoop\s([0-9]+)', x)
            if id_match:
                id = f"ZK{id_match.group(1)}"

            if s := re.search("\[wasabi\]\s.*\sis\sstarted", x):
                test_name = s.group().replace('[wasabi] ', '').replace(' is started', '')
                tests_name.add(test_name)

            elif re.search("\[wasabi\]\sRetry\sLoop", x):
                full_method_name = f"{f.split('/')[-1].replace('-output.txt', '')}.{method_name}"

                # Extracting constraint details
                constraint_match = re.search('(MaxRetry|MaxDuration)\s:\s([0-9]+)', x)
                if constraint_match:
                    constraint = f"{constraint_match.group(1)}: {constraint_match.group(2)}"
                else:
                    constraint = "[not called the constraint]"

                result.append([id, full_method_name, unit_test_name, line_number, constraint])

# Writing to result.csv
with open('resultFinal2.csv', 'w') as f:
    write = csv.writer(f)
    write.writerow(['ID', 'Method called', 'Unit Test', 'Line Number (from stack trace element)', 'Constraint'])
    for entry in result:
        id, method, unit_test, line_number, constraint = entry
        write.writerow([id, method, unit_test, line_number, constraint])

# Writing to testsname.csv
with open('testsnameFinal2.csv', 'w') as f:
    write = csv.writer(f)
    write.writerow(['test_name'])
    for test in sorted(tests_name):
        write.writerow([test])

print("\n".join([f"{x[0]}:[{x[1]}] Constraint: {x[2]}" for x in result]))