import process_wrap_queue
from rich.progress import Progress, TextColumn, BarColumn, TimeElapsedColumn, TimeRemainingColumn
import time
import json

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
def solve_problem_with_multiprocessing(question_function, common_context: dict, question_count: int, process_count: int, timeout=None, dumpfile=None):
    assert question_count >= 1
    assert process_count > 0

    # create pw wrap queue
    pw_queue_list = []
    for _ in range(process_count):
        pw_queue = process_wrap_queue.ProcessWrapQueue()
        pw_queue_list.append(pw_queue)

    # create all inner_process_wrap in subprocess
    for i in range(question_count):
        pw            = process_wrap_queue.InnerProcessWrap(question_function, args=(i, common_context), timeout=timeout)
        process_index = i % process_count
        pw_queue_list[process_index].add_process_wrap(pw) # add inner process wrap

    def get_total_job_count(pw_queue) -> int:
        brief     = pw_queue.get_queue_status_brief()
        total_cnt = brief["term_queue_len"] + brief["run_queue_len"] + brief["pend_queue_len"]
        return total_cnt

    def get_finished_job_count(pw_queue) -> int:
        return pw_queue.get_queue_status_brief()["term_queue_len"]
    
    # show process progress bar
    task_list = []
    with Progress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.completed}/{task.total}"),
        TimeElapsedColumn(),
        TimeRemainingColumn()
    ) as progress:
        for idx, pw_queue in enumerate(pw_queue_list):
            task = progress.add_task("process %3d: " % idx, total=get_total_job_count(pw_queue))
            task_list.append(task)

        # set all status to AUTO
        for pw_queue in pw_queue_list:
            pw_queue.set_queue_status("AUTO") # auto quit when finished

        # save progress to file
        def create_dump_file(dumpfile: str):
            dict_value = {}
            for idx, pw_queue in enumerate(pw_queue_list):
                dict_value[idx] = pw_queue.get_queue_status()
            fp = open(dumpfile, "w")
            json.dump(dict_value, fp, indent=4)

        # wait
        while not progress.finished:
            time.sleep(0.2)
            for i in range(len(task_list)):
                progress.update(task_list[i], completed=get_finished_job_count(pw_queue_list[i]))
            if dumpfile is not None:
                create_dump_file(dumpfile)



# the following code are a sample usage of mptrolley
def run_sample_problem(question_cnt, process_cnt):
    import os
    import hashlib
    dirnow    = os.path.dirname(os.path.abspath(__file__))
    test_case = os.path.join(dirnow, "test_case")

    def calculate_sha256(input_string: str) -> str:
        time.sleep(2)
        sha256_hash = hashlib.sha256()
        sha256_hash.update(input_string.encode('utf-8'))
        return sha256_hash.hexdigest()

    def sample_question_function(qid: int, ctx: dict): # create may file in a folder
        os.makedirs(test_case, exist_ok=True)
        data_file  = os.path.join(test_case, "%05d.txt" % qid)
        raw_string = "%d" % qid
        for _ in range(1000000): # calculate sha256sum for many times (to waste time)
            raw_string = calculate_sha256(raw_string)
        open(data_file, "w").write(raw_string)

    dirnow         = os.path.dirname(os.path.abspath(__file__))
    test_dump_file = os.path.join(dirnow, "test_case", "log.json")
    solve_problem_with_multiprocessing(sample_question_function, {}, question_cnt, process_cnt, timeout=1.5, dumpfile=test_dump_file)

if __name__ == "__main__": # this is just a testcase
    run_sample_problem(100, 5)