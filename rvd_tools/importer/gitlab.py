# -*- coding: utf-8 -*-
#
# Alias Robotics SL
# https://aliasrobotics.com

"""
Gitlab importer class, fetches tickets/flaws from Gitlab's
private repositories.

Requires ones to have the right configuration file at
    $HOME/.python-gitlab.cfg
"""

import re
from ..database.base import Base
import gitlab
import os
from ..utils import red
from ..database.flaw import Flaw
import yaml
from ..utils import yellow
import sys


class GitlabImporter(Base):
    def __init__(self, username="aliasrobotics", repo="RVD", project=15400852):
        """
        Imports tickets from Gitlab's private repos
        """
        super().__init__(username, repo)

        try:
            self.token = os.environ['GITLAB_TOKEN']
        except KeyError:
            red("ERROR, make sure that you've GITLAB_TOKEN exported")
            exit(1)

        # Initialize Gitlab's object
        self.repo = gitlab.Gitlab('https://gitlab.com', private_token=self.token)
        self.project = project

    def get_flaw(self, id):
        """
        Returns a flaw instance populated from the ticket with id number

        :param id, id number of the ticket
        :return Flaw
        """
        project = self.repo.projects.get(self.project)
        issue = project.issues.get(id)
        document_raw = issue.attributes['description'].replace('```yaml','').replace('```', '')
        document = yaml.load(document_raw, Loader=yaml.FullLoader)
        flaw = Flaw(document)
        labels = issue.attributes['labels']
        if not 'ready' in labels:
            yellow("Importing a ticket that's not 'ready' just yet")
            sys.exit(1)

        if "flaw" in labels:
            labels.remove("flaw")
        if "Offensive team" in labels:
            labels.remove('Offensive team')
        if "ready" in labels:
            labels.remove('ready')
        return flaw, labels

    def get_ready_flaws(self, labels):
        """
        Get all the tickets that include 'labels' and that have
        the 'ready' label

        :return [Flaw], list of Flaws
        """
        raise NotImplementedError

    def get_table(self, label):
        """
        Returns a tabulate ready table

        NOTE: Only open issues are considered for this source of information.

        :param label, tuple with labels, could be more than one
        :param is, status of the issues (could be "open", "closed" or "all")
        :return list[list]
        """
        table = []
        project = self.repo.projects.get(self.project)
        issues = project.issues.list()
        for issue in issues:
            if 'flaw' in issue.attributes['labels']:
                # print(issue.attributes['title'])
                # print(issue.attributes.keys())
                if label:
                    all_labels = True
                    for l in label:
                        if l in issue.attributes['labels']:
                            continue
                        else:
                            all_labels = False
                    if all_labels:
                        # print(issue.attributes['title'])
                        row = [0, issue.attributes['title']]
                        table.append(row)
                else:
                    row = [0, issue.attributes['title']]
                    table.append(row)

        return table
