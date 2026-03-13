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

triggers {
        githubPush()
    }

environment {
    DOCKER_IMAGE_NAME = "sp"
    DOCKER_TAG = "${env.BUILD_ID}"
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
                echo "Building Docker image: ${DOCKER_IMAGE_NAME}:${DOCKER_TAG}"
                docker.build("${DOCKER_IMAGE_NAME}:${DOCKER_TAG}", ".")
            }
 bbcf139 (update pipeline)
        }
    }

    stage('Linting') {
        agent {
            docker {
                image "${DOCKER_IMAGE_NAME}:${DOCKER_TAG}"
                reuseNode true
            }
        }
        steps {
            sh 'pip install flake8'
            sh 'flake8 . --count --show-source --statistics'
        }
    }

    stage('Testing') {
        agent {
            docker {
                image "${DOCKER_IMAGE_NAME}:${DOCKER_TAG}"
                reuseNode true
            }
        }
        steps {
            sh 'pip install pytest'
            sh 'pytest test.py'
        }
    }

    stage('Push Docker Image') {
        steps {
            script {
                docker.withRegistry('https://registry.hub.docker.com', 'dockerhub-credentials') {
                    docker.image("${DOCKER_IMAGE_NAME}:${DOCKER_TAG}").push()
                    docker.image("${DOCKER_IMAGE_NAME}:${DOCKER_TAG}").push("latest")
                }
            }
        }
    }

    stage('Deploy Application') {
        steps {
            echo "Deploying application using docker-compose..."
            sh 'docker-compose down || true'
            sh 'docker-compose up -d --build'
        }
    }

}

post {
    success {
        echo "Pipeline completed successfully 🚀"
    }

    failure {
        echo "Pipeline failed ❌"
    }

    always {
        echo "Cleaning workspace..."
        cleanWs()
    }
}

}
