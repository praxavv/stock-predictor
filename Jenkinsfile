// Declarative Jenkinsfile for a Python project with Docker.
// This pipeline assumes that the Jenkins agent executing it has Docker installed.

pipeline {
    agent any

    environment {
        // Use the project directory name for the Docker image.
        // You can change this to a more specific name.
        DOCKER_IMAGE_NAME = "sp"
    }

    stages {
        stage('Checkout') {
            steps {
                // This step checks out your source code from version control.
                // It's automatically configured by Jenkins based on your pipeline job setup.
                checkout scm
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    // We build a Docker image from the Dockerfile in the repository.
                    // The image is tagged with the build ID to keep it unique.
                    echo "Building Docker image: ${DOCKER_IMAGE_NAME}:${env.BUILD_ID}"
                    docker.build("${DOCKER_IMAGE_NAME}:latest", ".")
                }
            }
        }

        stage('Linting') {
            // This stage runs inside the Docker container we just built.
            // This ensures that the linting environment is consistent with the application environment.
            agent {
                docker {
                    image "${DOCKER_IMAGE_NAME}:${env.BUILD_ID}"
                    reuseNode true // Run on the same agent as the main pipeline
                }
            }
            steps {
                // Add your linting commands here.
                // Example using flake8. You might need to add flake8 to your requirements.txt
                // or install it here.
                sh 'flake8 . --count --show-source --statistics || true'
            }
        }

        stage('Testing') {
            // This stage also runs inside the built Docker container.
            agent {
                docker {
                    image "${DOCKER_IMAGE_NAME}:${env.BUILD_ID}"
                    reuseNode true
                }
            }
            steps {
                // Add your test commands here.
                // This is a placeholder since no test framework is configured.
                // Example for pytest (you would need to add it to requirements.txt):
                // sh 'pip install pytest'
                // sh 'pytest'
                echo "No tests found. This is a placeholder stage."
            }
        }

        // INSERT DEPLOY STAGE HERE ⬇️⬇️⬇️
        stage('Deploy') {
            steps {
                script {
                    sh 'docker stop stock_app || true'
                    sh 'docker rm stock_app || true'
                    sh 'docker run -d -p 8501:8501 --name stock_app sp:latest'
                }
            }
        }
        // INSERT DEPLOY STAGE HERE ⬆️⬆️⬆️

    }

    post {
        always {
            echo 'Pipeline execution finished.'
            // Optional: Clean up the Docker image created during the build.
            // Be cautious enabling this on shared Jenkins agents.
            // script {
            //     sh "docker rmi ${DOCKER_IMAGE_NAME}:${env.BUILD_ID}"
            // }
        }
    }
}
