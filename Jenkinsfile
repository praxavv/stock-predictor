// Declarative Jenkinsfile for a Python project with Docker.
// This pipeline assumes that the Jenkins agent executing it has Docker installed.

pipeline {
    agent any

    environment {
        DOCKER_IMAGE_NAME = "sp"
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    echo "Building Docker image: sp:latest"
                    sh "docker build -t sp:latest ."
                }
            }
        }

        stage('Linting') {
            agent {
                docker {
                    image "sp:latest"
                    reuseNode true
                }
            }
            steps {
                sh 'flake8 . --count --show-source --statistics || true'
            }
        }

        stage('Testing') {
            agent {
                docker {
                    image "sp:latest"
                    reuseNode true
                }
            }
            steps {
                echo "No tests found. This is a placeholder stage."
            }
        }

        stage('Deploy') {
            steps {
                script {
                    sh 'docker stop stock_app || true'
                    sh 'docker rm stock_app || true'
                    sh 'docker run -d -p 8501:8501 --name stock_app sp:latest'
                }
            }
        }
    }

    post {
        always {
            echo 'Pipeline execution finished.'
        }
    }
}
