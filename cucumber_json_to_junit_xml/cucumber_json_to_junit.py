#!/usr/bin/env python3
'''
Utility to convert from Cucumber JSON output to JUnit XML output
'''

import sys
import json

def main():
    '''
    Main function
    '''
    if len(sys.argv) < 2:
        print("A JSON file needs to be provided as a parameter. Usage:")
        print("\tpython3 cucumber-json-to-junit.py source-report.json")
        sys.exit()

    if len(sys.argv) > 2:
        print("A JSON file needs to be provided as a parameter. Usage:")
        print("\tpython3 cucumber-json-to-junit.py source-report.json")
        sys.exit()

    if len(sys.argv) == 2 and not sys.argv[1].endswith(".json"):
        print("Wrong file format provided as a parameter. Usage:")
        print("\tpython3 cucumber-json-to-junit.py source-report.json")
        sys.exit()

    with open(sys.argv[1], "r") as json_file:
        print("Opening file " + sys.argv[1] + " in read-only")
        json_data = json.load(json_file)

    header = "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"no\"?>\n"

    for feature in json_data:

        feature_name = sanitize(feature["name"])
        xml_feature_name = (feature["name"].replace(" ","" )) + ".xml"

        scenarios = feature["elements"]
        test_suite_time = 0.0
        feature_time = 0.0
        scenario_count = 0
        failure_count = 0

        test_cases = ""

        for scenario in scenarios:

            if scenario["type"] != "background":

                scenario_name = sanitize(scenario["name"])
                steps_blob = "<![CDATA["
                err_blob = ""
                scenario_status = "passed"

                scenario_time = 0.0
                scenario_count += 1
            
                for tag in scenario["tags"]:
                    steps_blob += tag["name"] + " "
                steps_blob += "\n"

                for step in scenario["steps"]:

                    description = sanitize(step["name"])
                    results = step["result"]
                    status = sanitize(results["status"])
                    keyword = sanitize(step["keyword"])

                    if status != "skipped":
                        scenario_time += float(results["duration"]) / 1000000000

                    num_dots = 120 - len(keyword) - len(description) - len(status)
                    if num_dots <= 0:
                        num_dots = 1

                    steps_blob += keyword + description
                    for i in range(num_dots):
                        steps_blob += "."
                    steps_blob += status + "\n"

                    if status == "failed":
                        err_blob = results["error_message"].replace("\"","&quot;")
                        scenario_status = "failed"
                        failure_count += 1

                steps_blob += "]]>"

                test_case = "<testcase "
                test_case += "classname=\"" + feature_name + "\" "
                test_case += "name=\"" + scenario_name + "\" "
                test_case += "time=\"" + str(scenario_time) + "\">"
                if scenario_status == "passed":
                    test_case += "<system-out>" + steps_blob + "</system-out>\n"
                else:
                    test_case += "<failure message=\"" + err_blob + "\">"
                    test_case += steps_blob + "</failure>\n"
                test_case += "</testcase>\n"

                test_cases += test_case
                feature_time += scenario_time

        test_suite_time += feature_time

        test_suite = "<testsuite "
        test_suite += "failures=\"" + str(failure_count) + "\" "
        test_suite += "name=\"" + str(feature_name) + "\" "
        test_suite += "skipped=\"0\" "
        test_suite += "tests=\"" + str(scenario_count) + "\" "
        test_suite += "time=\"" + str(test_suite_time) + "\">\n"
        
        for test_case in test_cases:
            test_suite += test_case

        test_suite += "</testsuite>"


        with open(xml_feature_name, "w") as junit_file:
            print("Writing to file " + xml_feature_name + " ...")
            junit_file.write(header)
            junit_file.write(test_suite)

    print("Done.")

def sanitize(input):
    #input = input.replace("&","&amp;").replace("\"","&quot;")
    #input = input.replace("<","&lt;").replace(">","&gt;")
    return input

if __name__ == "__main__":
    # execute only if run as a script
    main()
