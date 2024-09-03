from enum import Enum

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
