"# Grading-Script" 

All setting can be changed withing config.json which should be straightforward
For finding your path_to_makefile_and_exec run "cwd" in the folder and just copy.

boolean values can be used to enable the test and then you can set paths to where
those testcases are in file_paths

Testcase naming convensions should be test#.in test#.out

* FILE FORMATTING PARSING / SEMANTIC

Outputs to stderr and .in .out are not case sensitive but must match spec

If your expected output is 0 you dont need to fill out anything for the second line for Parsing / Semantic

Examples of file formatting can be found in ./TestParsing ./TestSemantic

* CODE GEN

The code gen is quite simple just follow naming requirements and then in the .in put the c code
and in the .out put the expected output from running the assembly. The formatting of the out
does not matter it will match any pattern regardles of where you put spaces. Examples
of these test cases can be found in ./TestCode to help you further make your own.
