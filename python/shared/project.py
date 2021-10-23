import logging

from github import Organization, Project, ProjectColumn

log = logging.getLogger(__name__)


def get_org_project(org: Organization, proj_number: int) -> Project:
    """
    Get the project with the given number in the given organization.

    :param org: the organization in which to find the project
    :param proj_number: the number of the project to find in the organization
    :return: the project being searched for
    :raise: ValueError if no project found with given number
    """

    log.info(f"Getting project {proj_number} in org {org.name or org.login}")
    projects = org.get_projects()
    project = next(proj for proj in projects if proj.number == proj_number)
    if project is None:
        log.error(f"No project was found with number {proj_number}.")
        raise ValueError("Project not found")
    return project


def get_project_column(proj: Project, col_name: str) -> ProjectColumn:
    """
    Get the project column with the given name in the given project.

    :param proj: the project in which to find the column
    :param col_name: the name of the project column to find in the project
    :return: the project column being searched for
    :raise: ValueError if no project column found with given name
    """

    log.info(f"Getting column {col_name} in project {proj.name}")
    columns = proj.get_columns()
    column = next(col for col in columns if col.name == col_name)
    if column is None:
        log.error(f"No column was found with name {col_name}.")
        raise ValueError("Column not found")
    return column
