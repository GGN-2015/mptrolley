# mptrolley
a simple python module to solve problem in a multiprocessing way.

## background
there are many jobs which are processed in batches. for example, in many computing tasks, you may need to run a same algorithm on many groups of different input data, and the "subproblems" are often **irrelevant** with each other. in this case, multiprocessing is a very simple and understandable way to accelerate. so we designed a very simple python module called mptrolley under the principle of KISS (Keep It Simple and Stupid).

## terminology
### problem and questions
in this passage, we define that a batched job is called a **problem**. in a single problem, there are may **questions**, and each question has a continuous numbering (begins from zero). we assume that you have already write a python function to solve a single question:
```python3
def question_function(question_index, common_context):
  ...
```
and we assume that you can solve your problem without any parallel in the following way:
```python3
common = ...
for i in range(question_count): # the questions should be numbered from 0 to (question_count-1)
  question_function(i, common)
```
in this case, mptrolley provides you a simple way to solve the problem faster with multiprocessing:
```python3
import mptrolley
common        = ...
process_count = ... # an interger to control the number of processes
mptrolley.solve_problem_with_multiprocessing(question_function, common, question_count, process_count)
```
the question list will be devided into `process_count` lists according to `question_index % process_count`. for some question `qx` and some process `px`, `px` will be used to solve `qx` if and only if `qx.question_index % process_count == px.process_index`.

## install
1. go [https://github.com/GGN-2015/mptrolley/releases](https://github.com/GGN-2015/mptrolley/releases) and download a .whl file.
2. use pip install `mptrolley-<version>-py3-none-any.whl` to install the package into your local environment.

## usage
```python3
import mptrolley

# define your own question function, it **MUST** have two parameters
#   question_index will be given a continuous integer index.
#   and common_context is the common information you may need during every question's solving procedure.
#   (there are many cases where we just don't need it.)
def question_function(question_index, common_context) -> None:
  ...

common        = ... # common information
process_count = ... # an interger to control the number of processes
mptrolley.solve_problem_with_multiprocessing(question_function, common, question_count, process_count)
```
