"""
Calculate max weeks of programmer availability for yearly planning.

Assumes the following:

1. The number of maintainers stays the same
2. We cannot anticipate availability changes like parental leave, part-time moves, etc.
3. 5 weeks of holiday + sick leave with stipulation that this is just an estimate!!!!!
4. Not all conferences are accounted for
"""

programmers_with_reduced_availability = {
    # _ is part-time (safer to assume that isn't going to change)
    "_": 52 * 0.6,
    # __ is on parental leave for the first quarter of the year
    "__": 52 - (52 / 4),
    # assume whoever is lead at any point probably has 1/3rd availability for dev work
    "lead": 52 / 3,
}

total_openverse_maintainers = 8

programmers_with_regular_availability = {
    "-" * (i + 1): 52
    for i in range(
        total_openverse_maintainers - len(programmers_with_reduced_availability)
    )
}

programmer_availability_ignoring_regular_leave = (
    programmers_with_reduced_availability | programmers_with_regular_availability
)

# These are just vague estimates, obviously some folks take more or less, etc.
holiday_weeks = 4
sick_weeks = 1

total_leave_weeks = holiday_weeks + sick_weeks

# Conferences with attendance estimate in reduced availability by weeks
conference_weeks = {
    "wceu": 3,
    "wcus": 2,
    "wccs": 2,
    "wcasia": 2,
    "ccglobalsummit": 1,
    "data": 1,
    "pydata": 0.5,
    "pycascades": 1,
    "widsps": 0.25,
    "other": 2,
    "teammeetup1": total_openverse_maintainers,
    "teammeetup2": total_openverse_maintainers,
    # Not all team members attend division meetups
    "divisonmeetup": total_openverse_maintainers / 2,
}

total_programmer_availability = sum(
    [
        weeks - total_leave_weeks
        for weeks in programmer_availability_ignoring_regular_leave.values()
    ]
    + [weeks * -1 for weeks in conference_weeks.values()]
)

print("Total weeks of programmer availability:", total_programmer_availability)
# => (e.g.) 221.6
