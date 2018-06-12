#!/usr/bin/python3

import datetime, os
import IssueDetails, UserDetails
from calendar import monthrange
from dateutil import parser
from jira.client import JIRA
from multiprocessing import Pool
from multiprocessing.dummy import Pool as ThreadPool


class WorkDetails:
	# WorkDetails

	jira, issue, issueDetails = None, None, None
	user, names, key = None, None, None
	workStartDate, workEndDate = None, None
	year, month, daysInMonth, offset = None, None, None, None


	def getDateWithOffset(self, year, month, day, offset):
		# Return a dateime object with the given offset.
		tzOffset = datetime.timezone(datetime.timedelta(hours=offset))
		return datetime.datetime(year, month, day, tzinfo = tzOffset)



	def __init__(self, jira, user, issue, month, year, workStartDate = None, workEndDate = None):
		self.jira = jira
		self.user = user
		self.issue = issue
		self.month = month
		self.year = year

		self.daysInMonth = monthrange(year, month)[1]
		self.offset = -5

		if issue != None:
			self.issueDetails = IssueDetails.IssueDetails(user = user, month = month,
				year = year, jira = jira)

		if user != None:
			userDetails = UserDetails.UserDetails(jira = self.jira)
			nameKey = userDetails.getNames(user = user)
			self.names = nameKey[0]
			self.key = nameKey[1]


		startYear, startMonth, startDay = 1, 1, 1
		if workStartDate is not None:
			startYear = workStartDate.year
			startMonth = workStartDate.month
			startDay = workStartDate.day
		else:
			startYear = self.year
			startMonth = self.month
			startDay = 1

		self.workStartDate = self.getDateWithOffset(year = startYear, month = startMonth, day = startDay, offset = self.offset)

		endYear, endMonth, endDay = 1, 1, 1
		if workEndDate is not None:
			endYear = workEndDate.year
			endMonth = workEndDate.month
			endDay = workEndDate.day
		else:
			endYear = self.year
			endMonth = self.month
			endDay = self.daysInMonth

		self.workEndDate = self.getDateWithOffset(year = endYear, month = endMonth, day = endDay, offset = self.offset)



	def getWorkSimple(self, issue, worklogs, names):
		# Return work logs for a "simple" issue.  That is, one with <20 worklogs.
		work = []
		
		for wl in worklogs:
			if str(wl.author) in names:
				workDate = parser.parse(str(wl.started))
				if self.workEndDate >= workDate and self.workStartDate <= workDate:
					wl.userDisplay = names[0]
					wl.userKey = names[1]
					wl.issueName = issue.key
					wl.issueId = issue.id
					wl.projectName = issue.fields.project.name
					wl.projectKey = issue.fields.project.key

					work.append(wl)

		return work


	def getWorkComplex(self, issue, names):
		# Return work logs for a "complex" issue.  That is, one with >20 worklogs.
		work = []

		# GET worklogs
		worklogs = self.jira.worklogs(issue)

		# parse/append
		for wl in worklogs:
			if str(wl.author) in names:
				workDate = parser.parse(str(wl.started))
				if self.workEndDate >= workDate and self.workStartDate <= workDate:
					wl.userDisplay = names[0]
					wl.userKey = names[1]
					wl.issueName = issue.key
					wl.issueId = issue.id
					wl.projectName = issue.fields.project.name
					wl.projectKey = issue.fields.project.key
					
					work.append(wl)

		return work


	def getWorklogs(self):
		# Returns detailed work logs for the issue.
		if self.issue.fields.worklog.total > 20:
			return self.user, self.getWorkComplex(issue = self.issue, names = self.names)
		else:
			return self.user, self.getWorkSimple(worklogs = self.issue.fields.worklog.worklogs, names = self.names)


	def getWorklogsForUser(self, namedIssue):
		names, issue = namedIssue[0], namedIssue[1]
		user = names[1]

		if issue.fields.worklog.total > 20:
			work = self.getWorkComplex(issue = issue, names = names[0])
		else:
			work = self.getWorkSimple(issue = issue, worklogs = issue.fields.worklog.worklogs, names = names[0])

		return user, work



	def getAllWorklogs(self, users, issueList):
		# Get all worklogs in a "simple" manner.

		pool = None

		if len(users) <= 1:
			pool = ThreadPool(len(users))
		else:
			pool = ThreadPool(os.cpu_count() * 2)

		work = []

		work = pool.map(self.getWorklogsForUser, issueList)
		pool.close()
		pool.join()

		return work

