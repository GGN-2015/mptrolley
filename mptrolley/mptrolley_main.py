import multiprocessing
import time
import sys

# timer and verbose output
BEGIN_TIME = time.time()
def verbose_output(verbose:bool, msg: str): # output verbose info to stderr
    if verbose:
        timenow = time.time()
        sys.stderr.write("[%13.3f] %s\n" % (timenow-BEGIN_TIME, msg.strip()))

# to create a single process
# return the process object just after it is created
def create_process_for_problem(verbose:bool, question_function, common_context:dict, question_count:int, process_count:int, process_id:int) -> multiprocessing.Process:
    def worker_process():
        for question_id in range(1, question_count):      # question 0 should be skipped
            if question_id % process_count == process_id: # select some question to solve
                verbose_output(verbose, "START: process_id: %4d, question_id: %8d/%8d" % (process_id, question_id, question_count))
                question_function(question_id, common_context)
                verbose_output(verbose, "DONE : process_id: %4d, question_id: %8d/%8d" % (process_id, question_id, question_count))
    process_now = multiprocessing.Process(target=worker_process, args=())
    return process_now

"""
question_function(question_id: int, common_context: dict):
    it should be a function with two parameters.
    the first parameter is an index value begins from 0.
    and the second parameter is the common infomation that should be known to solve all those questions.

question_count:
    the number of the questions.
    which means the index of questions should be 0 to (question_count - 1).

problem:
    problem is a list of questions.
    and you can basically solve the problem by calling the `question_function` one by one as:
    ```python3
    common_context = {}
    for question_id in range(question_count):
        question_function(question_id, common_context)
    ```

attention:
    the user needs to ensure that the function question_function can be called in parallel.
"""
def solve_problem_with_multiprocessing(question_function, common_context: dict, question_count: int, process_count: int, verbose=True):
    assert question_count >= 1
    assert process_count > 0

    # test phase: solve the first question (without parallel)
    # to prevent some basic errors which may occured in the sub process.
    verbose_output(verbose, "START: process_id: main, question_id: %8d/%8d" % (0, question_count))
    question_function(0, common_context)
    verbose_output(verbose, "DONE : process_id: main, question_id: %8d/%8d" % (0, question_count))

    # solve phase: create all process
    process_pool = []
    for process_id in range(process_count):
        process_now = create_process_for_problem(verbose, question_function, common_context, question_count, process_count, process_id)
        process_now.start()
        process_pool.append(process_now)

    # waiting phase: wait all process to finish
    for process_obj in process_pool:
        process_obj.join()



# the following code are a sample usage of mptrolley
def run_sample_problem(question_cnt, process_cnt):
    import os
    import hashlib
    dirnow    = os.path.dirname(os.path.abspath(__file__))
    test_case = os.path.join(dirnow, "test_case")

    def calculate_sha256(input_string: str) -> str:
        sha256_hash = hashlib.sha256()
        sha256_hash.update(input_string.encode('utf-8'))
        return sha256_hash.hexdigest()

    def sample_question_function(qid: int, ctx: dict): # create may file in a folder
        os.makedirs(test_case, exist_ok=True)
        data_file  = os.path.join(test_case, "%5d.txt" % qid)
        raw_string = "%d" % qid
        for _ in range(1000000): # calculate sha256sum for many times (to waste time)
            raw_string = calculate_sha256(raw_string)
        open(data_file, "w").write(raw_string)
    solve_problem_with_multiprocessing(sample_question_function, {}, question_cnt, process_cnt)

if __name__ == "__main__": # this is just a testcase
    run_sample_problem(100, 32)