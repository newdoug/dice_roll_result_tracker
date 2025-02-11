#!/usr/bin/env python3
"""Dice results tracker"""

import cmd
from collections import defaultdict
import json
import sys


def _get_range_err(num: int, low: int, high: int) -> str:
    return f"Number {num} no in range [{low}, {high}]"


class App(cmd.Cmd):
    """CLI app for dice roll result tracking"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.range_low = 1
        self.range_high = 6
        self._reset_tracker()
        self.prompt = "DICE> "

    def perror(self, *args, **kwargs) -> None:
        """Print to stderr. Name borrowed from cmd2"""
        # pylint: disable=no-self-use
        kwargs["file"] = kwargs.get("file", sys.stderr)
        print(*args, **kwargs)

    # pylint: disable=invalid-name
    def do_EOF(self, _):
        """Exit application with code 0"""
        # pylint: disable=no-self-use
        print("")
        sys.exit(0)

    def do_exit(self, _):
        """Exit application with code 0"""
        # pylint: disable=no-self-use
        sys.exit(0)

    def do_quit(self, _):
        """Exit application with code 0"""
        # pylint: disable=no-self-use
        sys.exit(0)

    def emptyline(self):
        """Overriden: Don't repeat last command"""
        # pylint: disable=no-self-use

    def _reset_tracker(self) -> None:
        self.tracker = defaultdict(int)
        self._set_range(self.range_low, self.range_high)

    def _set_range(self, low: int, high: int) -> None:
        self.range_low = low
        self.range_high = high
        for i in range(self.range_low, self.range_high + 1):
            # Even though it's a defaultdict, we want `len(tracker)` to be
            # accurate
            if i not in self.tracker:
                self.tracker[i] = 0
        print(f"Range set to [{self.range_low}, {self.range_high}]")

    def _in_range(self, num: int, raise_exc: bool = False) -> bool:
        if num not in range(self.range_low, self.range_high + 1):
            if raise_exc:
                raise ValueError(
                    _get_range_err(num, self.range_low, self.range_high))
            return False
        return True

    def _track(self, num: int, add_amount: int = 1) -> None:
        if not self._in_range(num):
            self.perror(_get_range_err(num, self.range_low, self.range_high))
            return
        self.tracker[num] += add_amount

    def _inc(self, num: int, amount: int = 1) -> None:
        self._track(num, amount)

    def _dec(self, num: int, amount: int = 1) -> None:
        self._track(num, -amount)

    def do_i(self, args):
        """Increment number(s) seen by 1"""
        try:
            args = [int(arg.strip()) for arg in args.split()]
        except ValueError as exc:
            self.perror(f"Failed to process input args: {exc}'")
            return False

        if not args:
            print("Nothing to do")
        for arg in args:
            self._inc(arg)
        return False

    def do_d(self, args):
        """Decrement number(s) seen by 1"""
        try:
            args = [int(arg.strip()) for arg in args.split()]
        except ValueError as exc:
            self.perror(f"Failed to process input args: {exc}'")
            return False

        if not args:
            print("Nothing to do")
        for arg in args:
            self._dec(arg)
        return False

    def do_reset(self, _):
        """Reset tracked numbers"""
        self._reset_tracker()

    def do_rs(self, args):
        """Set the valid range (inclusive)"""
        args = [arg.strip() for arg in args.split()]
        if len(args) != 2:
            self.perror("Please enter 2 integers (range low and high)")
            return False

        try:
            args = [int(arg) for arg in args]
        except ValueError:
            self.perror("Please enter 2 integers (range low and high)")
            return False

        self._set_range(args[0], args[1])
        return False

    def do_p(self, _):
        """Print current stats"""
        total = sum(self.tracker.values())
        if not total:
            print("Total occurrences == 0")
            return False

        total_perc = 0.0
        print("Num | Occurrences | Percent")
        for key in sorted(self.tracker.keys()):
            val = self.tracker[key]
            perc = (val / total) * 100
            total_perc += perc
            print(f"{key:3d} | {val:11d} | {round(perc, 2)}")
        print(f"Total num occurrences: {total}")
        print(f"Total percent: {round(total_perc, 2)}")
        avg_roll = sum(k * v for k, v in self.tracker.items()) / total
        expected_avg_roll = sum(self.tracker.keys()) / len(self.tracker)
        print(f"Average roll: {round(avg_roll, 2)}")
        print(f"Expected average roll: {expected_avg_roll}")
        avg_num_occurrences = total / len(self.tracker)
        print(f"Average num occurrences: {avg_num_occurrences}")
        expected_perc = (1 / (self.range_high + 1 - self.range_low)) * 100
        print(f"Fair percent: {round(expected_perc, 2)}")
        return False

    def do_save(self, filename):
        """Save results to file"""
        filename = (filename or "").strip()
        if not filename:
            filename = "save.json"

        with open(filename, "w", encoding="UTF8") as handle:
            handle.write(json.dumps(self.tracker, indent=2))
        print(f"Saved current results to file '{filename}'")

    def do_load(self, filename):
        """Load results from file"""
        filename = (filename or "").strip()
        if not filename:
            filename = "save.json"

        with open(filename, "r", encoding="UTF8") as handle:
            self._reset_tracker()
            self.tracker.update({
                # `json.dumps` will convert int keys to strings
                int(k): v for k, v in json.loads(handle.read()).items()
            })
        print(f"Loaded previous results from file '{filename}'")


if __name__ == "__main__":
    def main():
        """main runs the CLI command loop"""
        App().cmdloop()

    main()
