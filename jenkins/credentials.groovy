import com.cloudbees.plugins.credentials.domains.*
import com.cloudbees.plugins.credentials.impl.*
import com.cloudbees.plugins.credentials.*
import jenkins.model.*
import hudson.util.Secret
import org.jenkinsci.plugins.plaincredentials.impl.StringCredentialsImpl


// Функція для отримання змінних середовища
def getEnvVariable(String name) {
    return System.getenv(name)
}

def dockerUserName = getEnvVariable('DOCKERHUB_USERNAME')
def dockerPassword = getEnvVariable('DOCKERHUB_PASSWORD')

def weatherBotToken = getEnvVariable('TELEGRAM_WEATHER_BOT_TOKEN')
def openaiAPIkey = getEnvVariable('OPENAI_API_KEY')
def ttnAccessKey = getEnvVariable('TTN_ACCESS_KEY')
def mqttUsername = getEnvVariable('WEATHER_MQTT_USERNAME')
def mqttPassword = getEnvVariable('WEATHER_MQTT_PASSWORD')

def domain = Domain.global()
def store = Jenkins.instance.getExtensionList('com.cloudbees.plugins.credentials.SystemCredentialsProvider')[0].getStore()

def creds = new UsernamePasswordCredentialsImpl(CredentialsScope.GLOBAL, "dockerhub_token", "Description", dockerUserName, dockerPassword)
def weatherBotTokenCreds = new StringCredentialsImpl(CredentialsScope.GLOBAL, "weather_tg_bot_token", "Weather TG Bot Token", Secret.fromString(weatherBotToken))
def openaiAPIkeyCreds = new StringCredentialsImpl(CredentialsScope.GLOBAL, "openai_api_key", "Openai API key", Secret.fromString(openaiAPIkey))
def ttnAccessKeyCreds = new StringCredentialsImpl(CredentialsScope.GLOBAL, "ttn_access_key", "TTN access KEY", Secret.fromString(ttnAccessKey))
def mqttUsernameCreds = new StringCredentialsImpl(CredentialsScope.GLOBAL, "weather_mqtt_username", "Weather MQTT Username", Secret.fromString(mqttUsername))
def mqttPasswordCreds = new StringCredentialsImpl(CredentialsScope.GLOBAL, "weather_mqtt_password", "Weather MQTT Password", Secret.fromString(mqttPassword))

store.addCredentials(domain, creds)
store.addCredentials(domain, weatherBotTokenCreds)
store.addCredentials(domain, openaiAPIkeyCreds)
store.addCredentials(domain, ttnAccessKeyCreds)
store.addCredentials(domain, mqttUsernameCreds)
store.addCredentials(domain, mqttPasswordCreds)