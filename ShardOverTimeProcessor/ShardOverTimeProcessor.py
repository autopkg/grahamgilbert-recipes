#!/usr/bin/env python
#

"""See docstring for ShardOverTimeProcessor class"""

import os
import datetime
from autopkglib import Processor, ProcessorError

__all__ = ["ShardOverTimeProcessor"]

DEFAULT_CONDITION = "shard"
DEFAULT_DELAY_HOURS = 0
DEFAULT_SHARD_DAYS = 7


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
        }
    }
    output_variables = {
        "installable_condition": {
            "description": "The installable condition"
        }
    }

    def main(self):
        try:
            condition = self.env.get("condition", DEFAULT_CONDITION)
            delay_hours = int(self.env.get("delay_hours", DEFAULT_DELAY_HOURS))
            shard_days = int(self.env.get("shard_days", DEFAULT_SHARD_DAYS))
            output_string = ""

            now = datetime.datetime.now()
            target_date = now + datetime.timedelta(days=shard_days)
            start_date = now + datetime.timedelta(hours=delay_hours)

            # How many do we increment by for each group?
            deploy_time = target_date - start_date
            time_increment = deploy_time / 10
            date_format = "%Y-%m-%dT%H:%M:%SZ"

            time_10 = start_date
            time_20 = start_date + (time_increment * 2)
            time_30 = start_date + (time_increment * 3)
            time_40 = start_date + (time_increment * 4)
            time_50 = start_date + (time_increment * 5)
            time_60 = start_date + (time_increment * 6)
            time_70 = start_date + (time_increment * 7)
            time_80 = start_date + (time_increment * 8)
            time_90 = start_date + (time_increment * 9)
            time_100 = start_date + (time_increment * 10)

            output_string = """({} &lt;= 10 AND date &gt; CAST("{}", "NSDate")) OR {} &lt;= 20 AND date &gt; CAST("{}", "NSDate")) OR {} &lt;= 30 AND date &gt; CAST("{}", "NSDate")) OR {} &lt;= 40 AND date &gt; CAST("{}", "NSDate")) OR {} &lt;= 50 AND date &gt; CAST("{}", "NSDate")) OR {} &lt;= 60 AND date &gt; CAST("{}", "NSDate")) OR {} &lt;= 70 AND date &gt; CAST("{}", "NSDate")) OR {} &lt;= 80 AND date &gt; CAST("{}", "NSDate")) OR {} &lt;= 90 AND date &gt; CAST("{}", "NSDate")) OR {} &lt;= 100 AND date &gt; CAST("{}", "NSDate"))
            """.format(condition, time_10.strftime(date_format), condition, time_20.strftime(date_format), condition, time_30.strftime(date_format), condition, time_40.strftime(date_format), condition, time_50.strftime(date_format), condition, time_60.strftime(date_format), condition, time_70.strftime(date_format), condition, time_80.strftime(date_format), condition, time_90.strftime(date_format), condition, time_100.strftime(date_format))

            self.env["installable_condition"] = output_string
        except BaseException as err:
            # handle unexpected errors here
            raise ProcessorError(err)

if __name__ == "__main__":
    PROCESSOR = ShardOverTimeProcessor()
    PROCESSOR.execute_shell()