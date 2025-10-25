from typing import Optional
from python import os
import sys
import datetime
import time
from python import subprocess
from python import termcolor
colored = termcolor.colored

contest_id: Optional[str] = None
problem: Optional[str] = None

WORKSPACE_DIR = "/workspaces/atcoder/"

# --- utils ---


def sep():
    print("---------------------------")


def exit_gracefully():
    print(colored("Exiting...", "yellow"))
    sys.exit(0)


def get_time_from_str(time_str: str) -> datetime.time:
    h, m = list(map(int, time_str.split(":")))
    return datetime.time(h, m)


def set_new_contest():
    global contest_id
    c = input("Enter contest ID: ")
    contest_id = c
    print(colored(f"Initialized new contest with ID: {contest_id}", "green"))
    sep()


def set_problem(new_problem: str):
    assert contest_id is not None
    global problem

    problem = new_problem

    SOURCE_PATH = f"{WORKSPACE_DIR}{contest_id}/{problem}/main.py"
    subprocess.run(["code", SOURCE_PATH])


# --- phases ---


def home():
    sep()
    print(f"""
Select oparation:
1. Start new contest
2. Resume ongoing contest: {contest_id if contest_id is not None else ""}
3. Resume existing contest
0. Exit
""")
    op = input("Your choice: ")
    match op:
        case "0":
            # exit
            exit_gracefully()
        case "1":
            set_new_contest()
            starting_time = input(
                "Set starting time (press Enter to set to default: 21:00): ")
            init_new_contest(starting_time=starting_time or "21:00")
        case "2":
            sep()
            during_contest()
        case "3":
            resume_contest()


def init_new_contest(starting_time="21:00"):
    if contest_id is None or contest_id == "":
        print(colored("contest ID is required.", "red"))
        return
    print(colored(f"Contest starting time set to: {starting_time}", "green"))
    print("Waiting for contest to start...")
    parsed_starting_time = get_time_from_str(starting_time)
    while True:
        now = datetime.datetime.now()
        if now.time() >= parsed_starting_time:
            print(colored("Contest has started!", "green"))
            sep()
            break
        time.sleep(1)

    subprocess.run(["acc", "new", contest_id])
    sep()
    during_contest()


def during_contest():
    global problem

    if contest_id is None or contest_id == "":
        print(colored("contest ID is required.", "red"))
        return

    WORKING_DIR = f"{WORKSPACE_DIR}{contest_id}/"

    def show_existing_problems(dir_list: list[str]):
        print("Existing problems:")
        print()
        for p in dir_list:
            print(f" - {p}")
        print()

    # set problem
    if problem is None:
        dir_list = sorted([str(f) for f in os.listdir(
            WORKING_DIR) if os.path.isdir(f"{WORKING_DIR}{f}")])

        show_existing_problems(dir_list)

        while True:
            selected = input("Your choice: ")
            if selected in dir_list:
                set_problem(new_problem=selected)
                break

    def run_test():
        subprocess.run(
            ["codon", "build", f"{WORKING_DIR}{problem}/main.py"]
        )
        subprocess.run(
            ["oj", "t", "-c", "'./main'"],
            cwd=f"{WORKING_DIR}{problem}/"
        )

    def debug():
        subprocess.run(
            ["codon", "build", f"{WORKING_DIR}{problem}/main.py"]
        )
        subprocess.run(
            ["./main"],
            cwd=f"{WORKING_DIR}{problem}/"
        )

    while True:
        cmd = input(f"\n[problem {problem}] > ")

        if cmd == "exit":
            break

        elif cmd == "n":
            dir_list_before = [
                f for f in os.listdir(WORKING_DIR) if os.path.isdir(f"{WORKING_DIR}{f}")
            ]
            subprocess.run(["acc", "add"], cwd=WORKING_DIR)
            dir_list_after = [
                f for f in os.listdir(WORKING_DIR) if os.path.isdir(f"{WORKING_DIR}{f}")
            ]

            for dr in dir_list_after:
                if dr not in dir_list_before:
                    set_problem(dr)

        elif cmd == "c":
            dir_list = sorted([
                str(f) for f in os.listdir(WORKING_DIR) if os.path.isdir(f"{WORKING_DIR}{f}")
            ])
            show_existing_problems(dir_list)

            while True:
                target = input("Move to problem: ")
                if target in dir_list:
                    set_problem(target)
                    break
                elif target == "cancel":
                    break

        elif cmd == "t":
            run_test()

        elif cmd == "d":
            debug()

        elif cmd == "h":
            print("exit: exit, n: next problem, t: test")


def resume_contest():
    global contest_id
    input_contest_id = input("Enter contest ID: ")
    if not os.path.isdir(f"{WORKSPACE_DIR}/{input_contest_id}"):
        print(
            colored(f"contest '{input_contest_id}' is not initialized.", "red"))
        return
    contest_id = input_contest_id
    sep()
    during_contest()


if __name__ == "__main__":
    while True:
        home()
