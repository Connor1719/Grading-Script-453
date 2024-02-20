"# Grading-Script" 

All setting can be changed withing config.json which should be straightforward
For finding your path_to_makefile_and_exec run "cwd" in the folder and just copy.

boolean values can be used to enable the test and then you can set paths to where
those testcases are in file_paths

Testcase naming convensions should be test#.in test#.out

* FILE FORMATTING

Outputs to stderr and in .out are not case sensitive but must match spec

.in files are just the text you want to stderr.

.out files are formatted as first line expected error second line expected out

If your expected output is 0 you dont need to fill out anything for the second line

Examples of how to format the files can be found in TestParsing and TestSemantic
