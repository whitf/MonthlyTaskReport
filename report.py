#!/usr/bin/python3

import calendar, itertools, re, sys
import IssueDetails, WorkDetails, UserDetails
import JiraReport
from multiprocessing import Pool
from multiprocessing.dummy import Pool as ThreadPool
from prettytable import PrettyTable

# "main" code
options, conn, users = None, None, None
report = JiraReport.JiraReport()
conn = report.getConn()

# Handle configuration, input parsing, simple help messages
options = report.reportSettings(sys.argv[1:])

userDetails = UserDetails.UserDetails(jira = conn)

if options['group'] == None:
	# Run report for a single user.
	users = []
	users.append(options['user'])
else:
	# Run report for a group of users.
	users = []
	for u in userDetails.getUsersInGroup(group = options['group']):
		users.append(u)

issueDetails = IssueDetails.IssueDetails(month = options['month'],
	year = options['year'], user = None, jira = conn,
	workStartDate = options['start-date-string'], workEndDate = options['end-date-string'])

issues = []
issues = issueDetails.getAllIssues(users = users)

# Prep (user: [issues]) structure for threading.
issueList = []
for i in issues:
	names = userDetails.getNames(user = i[0])
	for issueKey in i[1]:
		issueList.append((names, issueKey))


workDetails = WorkDetails.WorkDetails(year = options['year'], month = options['month'],
	user = None, issue = None,jira = conn,
	workStartDate = options['start-date'], workEndDate = options['end-date'])

work = []
work = workDetails.getAllWorklogs(users = users, issueList = issueList)

# Format worklogs a bit better.
userWorklogs = dict({})
for w in work:

	if w[0] not in userWorklogs.keys():
		userWorklogs[str(w[0])] = []

	for wl in w[1]:
		userWorklogs[w[0]].append(wl)

#workFormatted = []
#workFormatted = report.formatWorkReport(worklogs = work)

if report.shouldParse():
	reportData = report.parseWorkReportDetails(userWorklogs)

workTotal = dict({})
for uw in userWorklogs:
	workTotal[uw] = report.summarizeWork(userWorklogs[uw])


# MAKE sure I am not counting any work logs more than once?

reportDateString = ""
if options['end-date'] is not None:
	reportDateString = "Work Totals for " + str(options['start-date-string']) + " to " + str(options['end-date-string'])
else:
	reportDateString = "Work Totals for " + calendar.month_name[options['month']] + " " + str(options['year'])

displayTable = PrettyTable(['User', 'Hours'])
# Add re.sub call to replace the \\\\u0040 code with the original @ sign if it is there.
for userKey in workTotal:
	displayTable.add_row([str(re.sub('\\\\u0040', '@', userKey)), "%.2f" % round((workTotal[userKey]/60/60),2) + "h"])

print()
print()
print(reportDateString)
print()
print(displayTable)
print()
