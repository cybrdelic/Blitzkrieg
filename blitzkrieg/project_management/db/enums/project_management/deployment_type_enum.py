from enum import Enum

from blitzkrieg.project_management.db.connection import get_db_engine, get_db_session

session = get_db_session()
engine = get_db_engine()

class DeploymentType(Enum):
    PIP = 'pip'
    DOCKER = 'docker'
    KUBERNETES = 'kubernetes'
    AWS = 'aws'
    AZURE = 'azure'
    GCP = 'gcp'
    HEROKU = 'heroku'
    NETLIFY = 'netlify'
    VERCCEL = 'vercel'
    CIRCLECI = 'circleci'
    TRAVIS = 'travis'
    JENKINS = 'jenkins'
    GITLAB = 'gitlab'
    GITHUB = 'github'
    BITBUCKET = 'bitbucket'
