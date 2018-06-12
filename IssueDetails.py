#!/usr/bin/python3

import UserDetails
from jira.client import JIRA
from jira.client import ResultList
from calendar import monthrange
from multiprocessing import Pool
from multiprocessing.dummy import Pool as ThreadPool


class IssueDetails:
	user = None
	jira = None
	month = None
	year = None
	daysInMonth = None
	key = None
	names = None
	workStartDate, workEndDate = None, None

	def __init__(self, user, month, year, jira, workStartDate = None, workEndDate = None):
		self.user = user
		self.month = month
		self.year = year
		self.jira = jira

		self.daysInMonth = monthrange(self.year, self.month)[1]

		if user != None:
			userDetails = UserDetails.UserDetails(self.jira)
			nameKey = userDetails.getNames(user = self.user)
			self.names = nameKey[0]
			self.key = nameKey[1]

		if workStartDate is None:
			self.workStartDate = self.getDate(year = self.year, month = self.month, day = 1)
		else:
			self.workStartDate = "" + str(workStartDate)

		if workEndDate is None:
			self.workEndDate = self.getDate(year = self.year, month = self.month, day = self.daysInMonth)
		else:
			self.workEndDate = "" + str(workEndDate)



	def getDate(self, year, month, day):
		# Returns a simple date string for JQL.
		return "" + str(year) + "-" + str(month) + "-" + str(day)


	def getIssues(self):
		#@deprecated, shouldn't be used.
		# Returns a list of issues on which the user has logged time in the given month.

		issues = []
		issues = self.jira.search_issues('worklogAuthor = ' + self.key + 
			' and worklogDate >= "%(workStartDate)s" and worklogDate <= "%(workEndDate)s"' % globals(), fields="worklog,project", expand="worklog")

		return issues


	def getIssuesForUser(self, user):

		userDetails = UserDetails.UserDetails(self.jira)
		nameKey = userDetails.getNames(user = user)
		names = nameKey[0]
		key = nameKey[1]

		issues = []
		issueCount = 0
		issueTotal = 1

		while len(issues) < issueTotal:
			issueList = self.jira.search_issues('worklogAuthor = ' + key + 
				' and worklogDate >= "' + str(self.workStartDate) + '" and worklogDate <= "' + str(self.workEndDate) + '"',
				fields="worklog,project", expand="worklog", startAt=str(len(issues)), maxResults=50)

			if len(issues) == 0:
				issues = issueList
			else:
				issues.extend(issueList)

			issueTotal = issueList.total


		issues = ResultList(issues, 0, len(issues), len(issues), True)

		return user, issues


	def getAllIssues(self, users):

		pool = ThreadPool(len(users))

		issues = []
		issues = pool.map(self.getIssuesForUser, users)

		pool.close()
		pool.join()

		return issues

