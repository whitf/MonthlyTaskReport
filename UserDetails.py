#!/usr/bin/python3

import re, sys
from jira.exceptions import JIRAError

class UserDetails:

	jira = None


	def __init__(self, jira):
		self.jira = jira


	def getNames(self, user):
		# Return a list of possible names (display name, etc) for a given user.
		names = []
		userNames = self.jira.search_users(user)

		if len(userNames) < 1 :
			# User not found.
			print()
			print("User " + user + " not found.")
			print()
			sys.exit(2)

		# "Fix" users with "email address" names.
		if re.search('@', userNames[0].name):
			userNames[0].name = re.sub("@", '\\\\u0040', userNames[0].name)
		
		names.append(userNames[0].displayName)
		names.append(userNames[0].key)
		names.append(userNames[0].name)

		return (names, userNames[0].name)


	def getUsersInGroup(self, group):
		# Return a list of users in the group.
		if group == 'all':
			group = "jira-software-users"

		try:
			users = self.jira.group_members(str(group))
		except JIRAError as e:
			if e.status_code == 404:
				print()
				print("Group " + str(group) + " not found or has 0 users.")
				print()
				sys.exit(2)

		return users
