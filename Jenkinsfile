pipeline {
    agent any

    option {
        // Max number of build logs to keep and days to keep
        buildDiscarder(logRotator(numToKeepStr: '5', daysToKeepStr: '5'))
        // Enable timestamp at each job in the pipeline
        timestamps()
    }

    environment {
        registry = 'antrinh/product-search'
        registryCredential = 'dockerhub'      
    }

    stages {
        stage("Test") {
            agent {
                docker {
                    image "python 3.10"
                }
            }
            steps {
                echo "Run unit tests.."
                sh "pip install -r requirements.txt && pytest"
            }
        }
        stage("Build") {
            steps {
                script {
                    echo "Building docker image.."
                    dockerImage = docker.build registry + ":$BUILD_NUMBER" 
                    echo 'Pushing image to dockerhub..'
                    docker.withRegistry( '', registryCredential ) {
                        dockerImage.push()
                        dockerImage.push('latest')
                }
            }
        }
    }
}