#!/usr/bin/python3

import configparser, datetime, getopt, netrc, sys, textwrap
from jira.client import JIRA
from calendar import monthrange
from dateutil import parser

class JiraReport:

	jira = None
	jiraHost, scriptVersion = None, None
	reportOptions, helpText = None, None
	jiraBrowseIssue, jiraBrowseWorklog = None, None


	def simpleGetMonth(self):
		# Return a simple month integer.
		today = datetime.date.today()
		return today.month

	def simpleGetYear(self):
		# Return a simple year integer
		today = datetime.date.today()
		return today.year

	def simpleGetDat(self):
		# Return a simple day integer
		today = datetime.date.today()
		return today.day

	def getConn(self):
		return self.jira

	def shouldParse(self):
		return self.reportOptions['shouldParse']


	def __init__(self):
		# Initialize configuration and set up connections.
		try:
			config = configparser.ConfigParser()
			config.read('jiraReport.conf')
			self.jiraHost = config.get('jira', 'host')
			self.scriptVersion = config.get('app', 'version')
			self.helpText = config.get('help', 'helpText')
		except configparser.Error as err:
			print()
			print("Error with configuration file (expecting ./jiraReport.conf).")
			print()
			print(err)
			print()
			sys.exit(1)

		self.reportOptions = {}
		self.reportOptions['month'] = self.simpleGetMonth()
		self.reportOptions['year'] = self.simpleGetYear()
		self.reportOptions['user'], self.reportOptions['group'] = None, None
		self.reportOptions['csv'] = False
		self.reportOptions['shouldParse'] = False
		self.reportOptions['end-date'], self.reportOptions['start-date'] = None, None
		self.reportOptions['end-date-string'], self.reportOptions['start-date-string'] = None, None

		self.jiraBrowseIssue = "https://" + self.jiraHost + "/browse/"

		try:
			nrc = netrc.netrc()
			authTokens = nrc.authenticators(self.jiraHost)
			authOptions = {'server': 'https://' + self.jiraHost}
			self.jira = JIRA(authOptions, basic_auth=(authTokens[0], authTokens[2]))
		except FileNotFoundError as err:
			print()
			print("Error reading .netrc.  Expecting a .netrc file at:")
			print("Linux - /home/<USER>/.netrc")
			print(err)
			print()
			print("https://docs.python.org/3/library/netrc.html")
			print()
			sys.exit(1)
		except Exception as err:
			print()
			print("Error reading .netrc.  File found but parsing and setting auth failed.")
			print(err)
			print()
			print("https://docs.python.org/3/library/netrc.html")
			print()
			sys.exit(1)


	def reportSettings(self, argv):
		# Parse command line options to figure out the month and user targets.
		# jiraReport.py -m <month> -y <year> -u <user_name>

		#@TODO add these options to the menu
		#@TODO add --startDate <date> and --endDate <date> flags to allow searching for a specific set of dates.
	
		#@TODO actually implement these options
		#@TODO add -q, --quiet flag to suppress all cli output.
		#@TODO add -v, --verbose flag to print additional information.
		#@TODO add -vv, --very-verbose to print lots of logging information.
		#@TODO add -p, --progress flag to provide progress information.

		try:
			opts, args = getopt.getopt(sys.argv[1:], "cf:g:hm:py:u:vvvq", ["csv", "end-date=", "file=", "group=", "help", "month=", "progress", "start-date=", "user=", "verbose", "very-verbose", "year=", "quiet"])

		except getopt.GetoptError as err:
			print(err)
			opts = "-h"

		for opt, arg in opts:
			if opt in ('-h', '--help'):
				print()
				print("JiraReports v." + str(self.scriptVersion))
				print(f"{self.helpText}")
				print()
				sys.exit(0)
			elif opt in ("-c", "--csv"):
				self.reportOptions['csv'] = True
				self.reportOptions['shouldParse'] = True
			elif opt in ("--end-date"):
				self.reportOptions['end-date'] = arg
			elif opt in ("-f", "--file"):
				self.reportOptions['file'] = arg
				self.reportOptions['shouldParse'] = True
			elif opt in ("-g", "--group"):
				self.reportOptions['group'] = arg
			elif opt in ("-m", "--month"):
				self.reportOptions['month'] = int(arg)
			elif opt in ("-p", "--progress"):
				print("Adding progress output.")
				print()
				print("Not yet implemented.")
				sys.exit(0)
			elif opt in ("--start-date"):
				self.reportOptions['start-date'] = arg
			elif opt in ("-u", "--user"):
				self.reportOptions['user'] = arg
			elif opt in ("-v", "--verbose"):
				print("Verbose output.")
				print()
				print("Not yet implmented.")
				sys.exit(0)
			elif opt in ("-vv", "--very-verbose"):
				print("Very verbose output.")
				print()
				print("Not yet implemented.")
				sys.exit(0)
			elif opt in ("-y", "--year"):
				self.reportOptions['year'] = int(arg)
			elif opt in ("-q", "--quiet"):
				print("Quiet output.")
				print()
				print("Not yet implmented.")
				sys.exit(0)
			
		if self.reportOptions['user'] != None and self.reportOptions['group'] != None:
			print()
			print("Ingoring user option, using group option.")
			print()
			self.reportOptions['user'] = None


		if self.reportOptions['user'] == None and self.reportOptions['group'] == None:
			print()
			print("A user name (-u <user>, --user <user>) or group name(-g <group>, --group <group>) is required.")
			print("Use -g all, --group all to run the report for all users.")
			print()
			print("Use -h, --help to see all options.")
			print()
			sys.exit(2)

		if self.reportOptions['end-date'] is not None:
			endDate = parser.parse(self.reportOptions['end-date'])
			self.reportOptions['end-date'] = endDate
			self.reportOptions['end-date-string'] = str(endDate.year) + "-" + str(endDate.month) + "-" + str(endDate.day)

		if self.reportOptions['start-date'] is not None:
			startDate = parser.parse(self.reportOptions['start-date'])
			self.reportOptions['start-date'] = startDate
			self.reportOptions['start-date-string'] = str(startDate.year) + "-" + str(startDate.month) + "-" + str(startDate.day)

			if self.reportOptions['end-date'] is None:
				endDate = datetime.datetime.today()
				self.reportOptions['end-date'] = endDate
				self.reportOptions['end-date-string'] = str(endDate.year) + "-" + str(endDate.month) + "-" + str(endDate.day)

		if self.reportOptions['end-date'] is not None and self.reportOptions['start-date'] == None:
			print("An end-date option requires a start-date.")
			exit(2)

		return self.reportOptions

	def parseWorkReportDetails(self, worklogs):
		# headers
		csv = []
		csv.append("user,issue,project,work_date,time_logged(s),time_logged(h),issue_link,worklog_link")

		for user in worklogs:
			for worklog in worklogs[user]:
				wlcsv = dict({})
				wlcsv['user'] = worklog.userDisplay
				wlcsv['issue'] = worklog.issueName
				wlcsv['issueId'] = worklog.issueId
				wlcsv['project'] = worklog.projectName
				wlcsv['projectKey'] = worklog.projectKey
				wlcsv['work_date'] = worklog.started
				wlcsv['time_logged(s)'] = worklog.timeSpentSeconds
				wlcsv['time_logged(h)'] =  "%.2f" % round(worklog.timeSpentSeconds/60.0/60.0,2)
				wlcsv['worklog_id'] = worklog.id
				wlcsv['issue_link'] = self.jiraBrowseIssue + worklog.issueName
				wlcsv['worklog_link'] = None

				line = ""
				line = (str(wlcsv['user']) +
					"," + str(wlcsv['issue']) +
					"," + str(wlcsv['project']) +
					"," + str(wlcsv['work_date']) + 
					"," + str(wlcsv['time_logged(s)']) +
					"," + str(wlcsv['time_logged(h)']) +
					"," + str(wlcsv['issue_link']))

				csv.append(line)


		if 'file' in self.reportOptions.keys():
			blank = open(self.reportOptions['file'], 'w')
			blank.write('')
			blank.close()


			with open(self.reportOptions['file'], 'a') as f:
				for line in csv:
					f.write(str(line) + "\n")

			print()
			print("Created file " + str(self.reportOptions['file']) + " with worklog details.")
			print()
		else:
			if self.reportOptions['csv']:
				print()
				for line in csv:
					print(line)
				print()

		return csv
		


	def formatWorkReport(self, worklogs):
		print("formatting a list of worklogs...")


		print(" ..done")

	def summarizeWork(self,worklogs):

		workTime = 0.00

		for wl in worklogs:
			workTime += wl.timeSpentSeconds

		return workTime


	def workPrettyPrint(self, worklogs):
		workTime = self.summarizeWork(worklogs)

		print("%.2f" % round(workTime,2))

