@Library('notify-job-result')_
pipeline {
    agent any
    stages{
        stage('Pull') { // for display purposes
            steps{
                sh '''
                    ssh root@171.244.57.184 << EOF
                        cd /root/code/crm
                        git checkout v3
                        git fetch
                        git pull --rebase
                        exit
                    EOF
                '''
            }
        }
        stage('Build ') {
            steps{
                sh '''
                    ssh root@171.244.57.184 << EOF
                        cd /root/code/crm
                        docker build -t crm-v3 -f service1 .
                        docker rm -vf crm-v3
                        docker run --name crm-v3 -d --net=host crm-v3
                        exit
                    EOF
                '''
            }
        }
        // stage('Clean') {
        //     steps{
        //         sh '''
        //             ssh root@171.244.57.184 << EOF
        //                 docker image prune -f
        //                 docker container prune -f
        //                 exit
        //             EOF
        //         '''
        //     }
        // }
    }

    post {
        failure {
          sendTelegram("Log: ${BUILD_URL}console\nJob: ${JOB_NAME}\nBuild # ${BUILD_NUMBER}\nStatus: failure")
        }
        success {
          sendTelegram("Log: ${BUILD_URL}console\nJob: ${JOB_NAME}\nBuild # ${BUILD_NUMBER}\nStatus: success")
        }
  }
}
