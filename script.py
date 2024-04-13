import json
import os
import re
import glob
import subprocess

config = json.load(open("config.json"))

passed = 0
total = 0

def inc_pass():
    global passed
    passed+=1

def inc_total():
    global total
    total+=1


def run_tests():
    for test in config['tests']:
        if config['tests'][test]:
            tests_path = config['file_paths'][f"{test}_path"]
            if os.path.exists(tests_path):
                input_files = glob.glob(os.path.join(tests_path, "test*.in"))
                input_files.sort(key=lambda f: int(re.findall(r'\d+', os.path.basename(f))[0]))
                for file in input_files:
                    out_file = f"{os.path.splitext(file)[0]}.out"
                    if os.path.exists(out_file):
                        exec_prog_comp(file, out_file, test)
                    else:
                        print(f"Could not found corresponding output file for {file}\n")
            else:
                print(f"Could not find folder {tests_path}")
                return


def exec_prog_comp(in_file, out_file, test):
    cla =  [f"{config['paths']['path_to_makefile_and_exec']}/compile", "/compile"]
    b = True if test == 'test_ast' else False
    c = True if test == "test_code" else False
    if (config['params'][f'{test}_param']):
        cla.append(config['params'][f'{test}_param'])
    if c:
        cla.append(config['params']['test_semantic_param'])
    with open(in_file, 'rb') as inpt:
        otpt = open(out_file, 'r').read().splitlines()
        if not otpt: return
        try:
            result = subprocess.run(cla, stdin=inpt, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except subprocess.CalledProcessError as e:
            if e.returncode == 1:
                if c:
                    code_gen_err(in_file, otpt, "1", test, e.stdout.decode())
                    return
                if b:
                    compare_cases(in_file, otpt, "1", test, e.stdout.decode(), b)
                    return
                compare_cases(in_file, otpt, "1", test, e.stderr.decode())
            else:
                bad_error(otpt, e, test, in_file)
                # print(f"Unknown error on 1 {test} -> {e}\n")
        else:
            if result.returncode == 0:
                if c:
                    code_gen(in_file, otpt, "0", test, result.stdout.decode())
                    return
                if b:
                    # TODO: might be useless case
                    compare_cases(in_file, otpt, "0", test, result.stdout.decode(), b)
                    return
                compare_cases(in_file, otpt, "0", test)
            else:
                bad_error(otpt, e, test, in_file)
                # print(f"Unknown return code on 2 {test}")


def bad_error(out_file, err, test, in_file):
    if out_file[0] == "0":
        print(f"{config['print_map'][test]} FAILED {in_file}")
        print("    Expected: Exit status 0")
        print(f"    Actual: (Likely Seg Fault) -> {err}\n")
    else:
        print(f"{config['print_map'][test]} FAILED {in_file}")
        print(f"    Expected: Exit status 1 -> {first_three(out_file[1])}")
        print(f"    Actual: (Likely Seg Fault) -> {err}\n")
    inc_total()


def code_gen(in_file, out_file, out_code, test, stdout):
    in_file = in_file[in_file.rfind("/")+1:]
    file = open("testout.s", "w")
    file = open("testout.s", "w")
    file.write(stdout)
    file.close()
    cla = ["spim", "-file", "testout.s"]
    result = subprocess.run(cla, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    os.remove("testout.s")
    output_spim = re.sub(r"(?s)SPIM Version.*exceptions.s\n", "", result.stdout.decode(), flags=re.DOTALL)
    output_spim_pretty = output_spim.rstrip("\n")
    lines_split = output_spim_pretty.splitlines()
    output_modified = [lines_split[0]] + [" " * 14 + line for line in lines_split[1:]]
    output_spim_pretty = "\n".join(output_modified)
    output_spim_cleaned = re.sub(r"\s+", "", output_spim)
    output_modified = [out_file[0]] + [" " * 14 + line for line in out_file[1:]]
    output_match_pretty = "\n".join(output_modified)
    output_match_cleaned = re.sub(r"\s+", "", output_match_pretty)
    if (output_match_cleaned == output_spim_cleaned):
        print(f"{config['print_map'][test]} PASSED {in_file}\n")
        inc_pass()
    else:
        print(f"{config['print_map'][test]} FAILED {in_file}")
        print(f"    Expected: {output_match_pretty}\n")
        print(f"      Actual: {output_spim_pretty}\n")
    inc_total()


def code_gen_err(in_file, out_file, out_code, test, stdout):
    in_file = in_file[in_file.rfind("/")+1:]
    output_modified = [out_file[0]] + [" " * 14 + line for line in out_file[1:]]
    output_match_pretty = "\n".join(output_modified)
    print(f"{config['print_map'][test]} FAILED {in_file}")
    print(f"    Expected: {output_match_pretty}\n")
    if (len(stdout) == 0): 
        print(f"      Actual: Unknown error nothing to STDOUT please test further yourself. Likely semantic though.\n")
    else: 
        print(f"      Actual: {stdout}\n")
    inc_total()


def check_output(output_file):
    return output_file[0] == "1" and len(output_file) > 1 and not first_three(output_file[1])


def compare_cases(in_file, out_file, output_code, test, out = None, b: bool = False):
    in_file = in_file[in_file.rfind("/")+1:]
    if out_file[0] == "0" and output_code == "0":
        if not b:
            print(f"{config['print_map'][test]} PASSED {in_file}\n")
            inc_pass()
        elif b:
            if out == out_file[1]:
                print(f"{config['print_map'][test]} PASSED {in_file}\n")
                inc_pass()
            else:
                print(f"{config['print_map'][test]} FAILED {in_file}")
                print(f"    Expected: Exit status 0 -> {out_file[1]}")
                print(f"      Actual: {out}\n")
    elif out_file[0] == "0" and output_code == "1":
        print(f"{config['print_map'][test]} FAILED {in_file}")
        print("    Expected: Exit status 0")
        print(f"      Actual: Exit status 1 -> {out}\n")
    elif out_file[0] == "1" and output_code == "0":
        print(f"{config['print_map'][test]} FAILED {in_file}")
        print(f"    Expected: Exit status 1 -> {first_three(out_file[1])}")
        print("      Actual: Exit status 0\n")
    elif out_file[0] == "1" and output_code == "1":
        # PARSING/SEMANTIC
        if not b:
            try:
                if first_three(out) == first_three(out_file[1]):
                    print(f"{config['print_map'][test]} PASSED {in_file}\n")
                    inc_pass()
                else:
                    print(f"{config['print_map'][test]} FAILED {in_file}")
                    print(f"    Expected: Exit status 1 -> {first_three(out_file[1])}")
                    print(f"      Actual: Exit status 1-> {out}\n")
            except:
                print(f"{config['print_map'][test]} FAILED {in_file}\n")
                print("ERROR OCCURED DURING COMPARISON\n")
        # AST fail
        elif b:
            try:
                if out == out_file[1]:
                    print(f"{config['print_map'][test]} PASSED {in_file}\n")
                    inc_pass()
                else:
                    print(f"{config['print_map'][test]} FAILED {in_file}")
                    print(f"    Expected: Exit status 1 -> {first_three(out_file[1])}")
                    print(f"      Actual: Exit status 1-> {out}\n")
            except:
                print(f"{config['print_map'][test]} FAILED {in_file}\n")
                print("ERROR OCCURED DURING COMPARISON\n")

    else:
        print(f"ERROR WITH CODES PARSING {test} {output_code} {out_file[0]}")
    inc_total()


def first_three(str):
    spl = str.lower().split()
    if len(spl) < 3: return False
    return ' '.join(spl[:3])


def compile():
    try:
        print("Beginning compiliation...\n")
        result = subprocess.run(["make", "compile", "-C", config['paths']['path_to_makefile_and_exec']], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(result.stdout.decode())
    except subprocess.CalledProcessError as e:
        print("Compilation failed.")
        print(e.stderr.decode())
        return False
    except FileNotFoundError as e:
        print("Compilation failed.\nMakefile not found.")
        return False
    except Exception as e:
        print(f"Unknown error {e}")
        return False
    else:
        print("Compilation successful.\nBeginning testing...")
        return True

def clean():
    try:
        print("Cleaning files...")
        result = subprocess.run(["make", "clean", "-C", config['paths']['path_to_makefile_and_exec']], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # print(result.stdout.decode())
    except subprocess.CalledProcessError as e:
        print("Make clean failed.\n")
        return 
    except Exception as e:
        print(f"Unknown error during clean {e}\n")
        return  
    else:
        print("Cleaning successful.\n")
        return

def main():
    if not compile(): return
    run_tests()
    if config["other"]["clean_files"]: clean()
    global passed
    global total
    print(f"Passed {passed} out of {total} total test cases.")
    



if __name__ == "__main__":
    main()