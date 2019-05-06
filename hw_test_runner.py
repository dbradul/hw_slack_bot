import sys
import threading

import hw_test_set
import hw_current_task
import hw_slack_bot

import math
import random
import re
import string

STOP_PROCESS = False
task_run_error = ""
task_failed_error = ""

#---------------------------------------------------------------
exec(hw_current_task.code)


#---------------------------------------------------------------
class TestFailedException(Exception):

    def __init__(self, input=None, expected=None, actual=None, text=None):
        self._input = input
        self._expected = expected
        self._actual = actual
        self._text = text

    def __str__(self):
        if self._text:
            return self._text
        else:
            return ":red_circle: TEST FAILED:\n" \
                 "```\n" \
                 "INPUT    :\t%s\n" \
                 "EXPECTED :\t%s\n" \
                 "ACTUAL   :\t%s\n" \
                 "```" % (self._input, self._expected, self._actual)


#---------------------------------------------------------------
def run_test(func, input, expected):
    try:
        actual = func(*input)
        if callable(expected):
            for i in range(1000):
                actual = func(*input)
                if actual is None: # sometimes we need to check modified in place params
                    if not expected(*input):
                        raise TestFailedException(input, "Doesn't meet task requirements", actual)
                elif not expected(actual):
                    raise TestFailedException(input, "Doesn't meet task requirements", actual)

        elif isinstance(expected, tuple):
            for elem_exp, elem_act in zip(expected, actual):

                if isinstance(elem_exp, float):
                    if not math.isclose(elem_act, elem_exp, abs_tol=0.001):
                        raise TestFailedException(input, expected, actual)

                elif not elem_act == elem_exp:
                        raise TestFailedException(input, expected, actual)

        elif isinstance(expected, float):
            if not math.isclose(actual, expected, abs_tol=0.001):
                raise TestFailedException(input, expected, actual)

        elif not actual == expected:
            raise TestFailedException(input, expected, actual)

    except TestFailedException as ex:
        global task_failed_error
        task_failed_error = str(ex)
    except Exception as ex:
        global task_run_error
        task_run_error = str(ex)


#---------------------------------------------------------------
def run_code(task_id, user):

    result = "<UNKNOWN>"
    error = None

    try:
        if task_id in hw_test_set.tests:
            tests = hw_test_set.tests[task_id]
            for test in tests:

                global task_run_error
                task_run_error = ""
                t = threading.Thread(target=run_test, daemon=True, args=(TASKS[user][task_id], test[0], test[1]))
                t.start()
                t.join(hw_slack_bot.TIMEOUT_CODE_RUN_SEC)

                if t.is_alive():
                    global STOP_PROCESS
                    STOP_PROCESS = True
                    raise TimeoutError(":red_circle: TIMEOUT ERROR:\nCode run time limit is exceeded: %d sec!" % hw_slack_bot.TIMEOUT_CODE_RUN_SEC)

                if task_failed_error:
                    raise TestFailedException(text=task_failed_error)

                if task_run_error:
                    raise RuntimeError(task_run_error)

                result = "TEST PASSED!\nWell done! :+1:"
        else:
            result = "Sorry, tests are not available for this task :(\nPlease, check later."

    except TestFailedException as ex:
        print(ex)
        result = str(ex)

    except TimeoutError as ex:
        print(ex)
        result = str(ex)

    except Exception as ex:
        print(ex)
        error = str(ex)

    except:
        print("Unexpected error:", sys.exc_info()[0])
        error = sys.exc_info()[0]

    return result, error
