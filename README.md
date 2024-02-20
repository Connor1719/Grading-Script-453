"# Grading-Script" 

All setting can be changed withing config.json which should be straightforward
For finding your path_to_makefile_and_exec run "cwd" in the folder and just copy.

boolean values can be used to enable the test and then you can set paths to where
those testcases are in file_paths

Testcase naming convensions should be test#.in test#.out

* FILE FORMATTING

Outputs to stderr and in .out are not case sensitive but must match spec

.in files are just the text you want to stderr.

If your expected outout is to fail the file should be formatted as:

- FILE#.out
1
error line #


If your expected output is 0 you dont need to fill out anything for the second line

Further examples of file formatting can be seen in TestParsing

