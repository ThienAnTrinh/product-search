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
        OPENAI_API_KEY = credentials('OPENAI_API_KEY')
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
                    // withCredentials([
                    //     string(credentialsId: 'OPENAI_API_KEY', variable: 'OPENAI_API_KEY'),
                    //     string(credentialsId: 'PINECONE_API_KEY', variable: 'PINECONE_API_KEY')
                    // ]) {
                    //     container('helm') {
                    //     sh '''
                    //         export OPENAI_API_KEY=${OPEN_API_KEY}
                    //         export PINECONE_API_KEY=${PINECONE_API_KEY}
                    //         kubectl create namespace product-search || true
                    //         helm upgrade --install app --namespace product-search \
                    //         --set open_api_key=OPENAI_API_KEY \
                    //         --set pinecone_api_key=PINECONE_API_KEY\
                    //         ./helm/app_chart_nginx_ingress
                    //     '''
                    //     }
                    // }
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
        // stage('Monitor') {
        //     steps {
        //         script {
        //             // Update Helm repositories
        //             sh 'helm repo add prometheus-community https://prometheus-community.github.io/helm-charts'
        //             sh 'helm repo update'

        //             // Create Kubernetes namespace and install Prometheus stack
        //             sh '''
        //                 kubectl create namespace prometheus || true
        //                 helm install monitoring-stack \
        //                   --namespace prometheus \
        //                   prometheus-community/kube-prometheus-stack
        //             '''

        //             // Expose Prometheus and Grafana dashboards
        //             sh 'kubectl port-forward svc/monitoring-stack-kube-prom-prometheus 9090:9090 &'
        //             sh 'kubectl port-forward svc/monitoring-stack-grafana 8888:80 &'
        //         }
        //     }
        // }
    }
}