pipeline {
    agent any
    environment {
		TELEGRAM_WEATHER_BOT_TOKEN = credentials('weather_tg_bot_token')
		OPENAI_API_KEY = credentials('openai_api_key')
		TTN_ACCESS_KEY = credentials('ttn_access_key')
		WEATHER_MQTT_USERNAME = credentials('weather_mqtt_username')
		WEATHER_MQTT_PASSWORD = credentials('weather_mqtt_password')

		DOCKER_IMAGE = 'vulchakpavlo/kursova_weather'
    }
    stages {
        stage('Start') {
            steps {
                echo 'Cursova_Bot: nginx/custom'
            }
        }

        stage('Build Weather services') {
            steps {
                sh 'export TELEGRAM_WEATHER_BOT_TOKEN=$TELEGRAM_WEATHER_BOT_TOKEN'
				sh 'export OPENAI_API_KEY=$OPENAI_API_KEY'
				sh 'export TTN_ACCESS_KEY=$TTN_ACCESS_KEY'
				sh 'export WEATHER_MQTT_USERNAME=$WEATHER_MQTT_USERNAME'
				sh 'export WEATHER_MQTT_PASSWORD=$WEATHER_MQTT_PASSWORD'
                dir("Weather_TgBot_Server_Website")
				{
					sh 'docker-compose build'
				}
				sh 'docker tag weather-tg_bot:latest $DOCKER_IMAGE:tg_bot-latest'
                sh 'docker tag weather-tg_bot:latest $DOCKER_IMAGE:tg_bot-$BUILD_NUMBER'
				sh 'docker tag weather-server:latest $DOCKER_IMAGE:server-latest'
                sh 'docker tag weather-server:latest $DOCKER_IMAGE:server-$BUILD_NUMBER'
				sh 'docker tag weather-website:latest $DOCKER_IMAGE:website-latest'
                sh 'docker tag weather-website:latest $DOCKER_IMAGE:website-$BUILD_NUMBER'

            }
            post{
                failure {
                    script {
                    // Send Telegram notification on success
                        telegramSend message: "Job Name: ${env.JOB_NAME}\n Branch: ${env.GIT_BRANCH}\nBuild #${env.BUILD_NUMBER}: ${currentBuild.currentResult}\n Failure stage: '${env.STAGE_NAME}'"
                    }
                }
            }
        }

        stage('Test Weather services') {
            steps {
                echo 'Pass'
            }
            post{
                failure {
                    script {
                    // Send Telegram notification on success
                        telegramSend message: "Job Name: ${env.JOB_NAME}\nBranch: ${env.GIT_BRANCH}\nBuild #${env.BUILD_NUMBER}: ${currentBuild.currentResult}\nFailure stage: '${env.STAGE_NAME}'"
                    }
                }
            }
        }

		stage('Push to registry') {
            steps {
                withDockerRegistry([ credentialsId: "dockerhub_token", url: "" ])
                {
                    sh "docker push $DOCKER_IMAGE:tg_bot-latest"
                    sh "docker push $DOCKER_IMAGE:tg_bot-$BUILD_NUMBER"
					sh "docker push $DOCKER_IMAGE:server-latest"
                    sh "docker push $DOCKER_IMAGE:server-$BUILD_NUMBER"
					sh "docker push $DOCKER_IMAGE:website-latest"
                    sh "docker push $DOCKER_IMAGE:website-$BUILD_NUMBER"
                }
            }
            post{
                failure {
                    script {
                    // Send Telegram notification on success
                        telegramSend message: "Job Name: ${env.JOB_NAME}\nBranch: ${env.GIT_BRANCH}\nBuild #${env.BUILD_NUMBER}: ${currentBuild.currentResult}\nFailure stage: '${env.STAGE_NAME}'"
                    }
                }
            }
        }

        stage('Deploy Weather services') {
            steps {
				dir("Weather_TgBot_Server_Website"){
					sh "docker-compose down"
                	sh "docker container prune --force"
                	sh "docker image prune --force"
                	sh "docker-compose up -d --build"
				}
            }
            post{
                failure {
                    script {
                    // Send Telegram notification on success
                        telegramSend message: "Job Name: ${env.JOB_NAME}\nBranch: ${env.GIT_BRANCH}\nBuild #${env.BUILD_NUMBER}: ${currentBuild.currentResult}\nFailure stage: '${env.STAGE_NAME}'"
                    }
                }
            }
        }
    }

    post {
        success {
            script {
                // Send Telegram notification on success
                telegramSend message: "Job Name: ${env.JOB_NAME}\n Branch: ${env.GIT_BRANCH}\nBuild #${env.BUILD_NUMBER}: ${currentBuild.currentResult}"
            }
        }
    }
}
