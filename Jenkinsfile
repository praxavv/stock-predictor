pipeline {
agent any

```
environment {
    DOCKER_IMAGE_NAME = "sp"
    DOCKER_TAG = "${env.BUILD_ID}"
}

triggers {
    githubPush()
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
                sh "docker build -t ${DOCKER_IMAGE_NAME}:${DOCKER_TAG} ."
            }
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
            sh 'flake8 . --count --show-source --statistics || true'
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
            sh 'pytest test.py || true'
        }
    }

    stage('Deploy') {
        steps {
            script {
                sh 'docker stop stock_app || true'
                sh 'docker rm stock_app || true'
                sh "docker run -d -p 8501:8501 --name stock_app ${DOCKER_IMAGE_NAME}:${DOCKER_TAG}"
            }
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
        echo "Pipeline execution finished."
    }
}
```

}
