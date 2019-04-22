#!/usr/bin/env python
#

"""See docstring for ShardOverTimeProcessor class"""

import os
import datetime
from autopkglib import Processor, ProcessorError
import sys

__all__ = ["ShardOverTimeProcessor"]

DEFAULT_CONDITION = "shard"
DEFAULT_DELAY_HOURS = 0
DEFAULT_SHARD_DAYS = 5
DEFAULT_WORKING_HOURS = True


class ShardOverTimeProcessor(Processor):
    """This processor will add an installable condition to Munki pkginfo files to roll updates out over a period of time based on a integer value of a configurable condition."""
    description = __doc__
    input_variables = {
        "condition": {
            "required": False,
            "description": "The condition to use to divide devices. Defaults to \"{}\"".format(DEFAULT_CONDITION)
        },
        "delay_hours": {
            "required": False,
            "description": "Number of hours to delay the initial rollout by. Defaults to \"{}\"".format(DEFAULT_DELAY_HOURS)
        },
        "shard_days": {
            "required": False,
            "description": "The number of days the rollout will be rolled over. Defaults to \"{}\"".format(DEFAULT_SHARD_DAYS)
        },
        "working_hours": {
            "required": False,
            "description": "Restrict rollout times to 9am-6pm (local time). Defaults to \"{}\"".format(DEFAULT_WORKING_HOURS)
        }
    }
    output_variables = {
        "installable_condition": {
            "description": "The installable condition"
        }
    }

    def next_working_day(self, the_date):
        try:
            if the_date.weekday() == 5:
                # It's a saturday
                return the_date.replace(hour=9, minute=00) + datetime.timedelta(days=2)
            elif the_date.weekday() == 6:
                # It's a sunday
                return the_date.replace(hour=9, minute=00) + datetime.timedelta(days=1)
            elif the_date.hour not in range(9,18):
                print("{} is not between 9 and 18".format(the_date))
                print("Sending {} back to next_working_day".format(the_date.replace(hour=9, minute=00) + datetime.timedelta(days=1)))
                # The time is not in working hours, call ourself with tomorrow as the date
                return self.next_working_day(the_date.replace(hour=9, minute=00) + datetime.timedelta(days=1))
            else:
                return the_date
        except BaseException as err:
            # handle unexpected errors here
            exc_type, exc_obj, exc_tb = sys.exc_info()
            error_string = "error: {}, line: {}".format(err, exc_tb.tb_lineno)
            raise ProcessorError(error_string)

    def main(self):
        try:
            condition = self.env.get("condition", DEFAULT_CONDITION)
            delay_hours = int(self.env.get("delay_hours", DEFAULT_DELAY_HOURS))
            shard_days = int(self.env.get("shard_days", DEFAULT_SHARD_DAYS))
            working_hours = bool(self.env.get("working_hours", DEFAULT_WORKING_HOURS))
            output_string = ""

            now = datetime.datetime.now()
            target_date = now + datetime.timedelta(days=shard_days)
            start_date = now + datetime.timedelta(hours=delay_hours)

            date_format = "%Y-%m-%dT%H:%M:%SZ"



            # We also only deploy monday to friday
            if working_hours:
                # If working hours, we only have 9 hours a day.

                # We are only going to start deploying (or more if delay_hours > 24) at 9am
                if delay_hours > 24:
                    start_date = now + datetime.timedelta(hours=delay_hours)
                    if start_date.hour > 18 and start_date.hour < 9:
                        start_date = start_date.replace(hour=9, minute=00) + datetime.timedelta(days=1)
                    else:
                        start_date = start_date.replace(hour=9, minute=00)

                # make sure it's a working day
                start_date = self.next_working_day(start_date)
                # how many working hours between now and end of shard_days
                increment = datetime.timedelta(minutes= (9 * shard_days * 60) / 10)
                current_deploy_date = start_date
                output_string += "("
                for group in range(0, 10):
                    group = (group + 1) * 10
                    deploy_time = self.next_working_day(current_deploy_date + increment)
                    print("group: {} deploy_time: {}".format(group, deploy_time))
                    output_string += "({} <= {} AND date > CAST(\"{}\", \"NSDate\")) OR ".format(condition, group, deploy_time.strftime(date_format))
                    current_deploy_date = deploy_time
                output_string = output_string[:-3]
                output_string += ")"
            else:
                # How many do we increment by for each group?
                deploy_time = target_date - start_date
                time_increment = deploy_time / 10


                time_10 = start_date
                # if working_hours is true, make sure the start time is between 9 and 6
                time_20 = start_date + (time_increment * 2)
                time_30 = start_date + (time_increment * 3)
                time_40 = start_date + (time_increment * 4)
                time_50 = start_date + (time_increment * 5)
                time_60 = start_date + (time_increment * 6)
                time_70 = start_date + (time_increment * 7)
                time_80 = start_date + (time_increment * 8)
                time_90 = start_date + (time_increment * 9)
                time_100 = start_date + (time_increment * 10)

                output_string = """({} <= 10 AND date > CAST("{}", "NSDate")) OR {} <= 20 AND date > CAST("{}", "NSDate")) OR {} <= 30 AND date > CAST("{}", "NSDate")) OR {} <= 40 AND date > CAST("{}", "NSDate")) OR {} <= 50 AND date > CAST("{}", "NSDate")) OR {} <= 60 AND date > CAST("{}", "NSDate")) OR {} <= 70 AND date > CAST("{}", "NSDate")) OR {} <= 80 AND date > CAST("{}", "NSDate")) OR {} <= 90 AND date > CAST("{}", "NSDate")) OR {} <= 100 AND date > CAST("{}", "NSDate"))
                """.format(condition, time_10.strftime(date_format), condition, time_20.strftime(date_format), condition, time_30.strftime(date_format), condition, time_40.strftime(date_format), condition, time_50.strftime(date_format), condition, time_60.strftime(date_format), condition, time_70.strftime(date_format), condition, time_80.strftime(date_format), condition, time_90.strftime(date_format), condition, time_100.strftime(date_format))
            # print(output_string)
            self.env["installable_condition"] = output_string
        except BaseException as err:
            # handle unexpected errors here
            exc_type, exc_obj, exc_tb = sys.exc_info()
            error_string = "error: {}, line: {}".format(err, exc_tb.tb_lineno)
            raise ProcessorError(error_string)

if __name__ == "__main__":
    PROCESSOR = ShardOverTimeProcessor()
    PROCESSOR.execute_shell()