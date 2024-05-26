pipeline {
    agent any

    options {
        // Max number of build logs to keep and days to keep
        buildDiscarder(logRotator(numToKeepStr: '5', daysToKeepStr: '5'))
        // Enable timestamp at each job in the pipeline
        timestamps()
    }

    environment {
        registry = 'antrinh/product-search'
        registryCredential = 'dockerhub'
        OPENAI_API_KEY = credentials('OPENAI_API_KEY') // assign Jenkins credentials to env variables
        PINECONE_API_KEY = credentials('PINECONE_API_KEY')
    }

    stages {
        stage("Test") {
            agent {
                docker {
                    image "python:3.10-slim"
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
                            dockerImage.push('lts')
                    }
                }
            }
        }
        stage("Deploy") {
            agent {
                kubernetes {
                    containerTemplate {
                        name 'helm' // Name of the container to be used for helm upgrade
                        image 'antrinh/jenkins-docker-k8s:lts' // The image containing helm
                        alwaysPullImage true // Always pull image in case of using the same tag
                    }
                }
            }
            steps {
                script {
                    container('helm') {
                        sh '''
                            kubectl create namespace product-search || true
                            helm upgrade --install app --namespace product-search \
                            --set openai_api_key=OPENAI_API_KEY \
                            --set pinecone_api_key=PINECONE_API_KEY\
                            ./helm/app_chart_nginx_ingress
                        '''
                    }
                }
            }
        }
    }
}