# Evolution API Webhook Integration

This project integrates the Evolution API with a Flask application that listens for incoming messages via a WhatsApp webhook and responds using a language model.

## Project Overview

This project provides an interface to handle incoming messages from a WhatsApp group, process them using a language model (such as Mistral), and send automated responses back to the group. It uses the Evolution API to interact with the WhatsApp business API.

## Features

- **Webhook Listener**: Listens to incoming messages from a WhatsApp group via Evolution API.
- **Message Handling**: Processes messages and retrieves the history of the conversation to generate context for responses.
- **Language Model Integration**: Uses the Mistral language model to generate human-like responses based on the conversation history.
- **Environment Variables**: Sensitive information such as API keys and database credentials are securely managed via environment variables.

## Prerequisites

Before running the project, ensure you have the following:

- Docker and Docker Compose installed on your machine.
- Python 3.x installed (for local testing, if necessary).
- Evolution API Docker image: `atendai/evolution-api:v2.1.0`.
- Redis Docker image: `redis:7`.
- `.env` file with all required environment variables (as listed below).

## Installation

1. Clone the repository:

    ```bash
    git clone <repository_url>
    cd <repository_directory>
    ```

3. **Start the services** using Docker Compose:

    ```bash
    docker-compose up
    ```

4. The application will run on port `5001`. The webhook will be accessible at:

    ```
    http://localhost:5001/webhook
    ```

    Ensure that this endpoint is properly configured in the Evolution API to receive the webhook events.

## Usage

Once the services are running, the Flask app will automatically listen for incoming webhook requests. When a message is received from a WhatsApp group, the app will:

1. Retrieve the latest conversation history.
2. Generate a response based on the current message and conversation history using the Mistral language model.
3. Send the response back to the group via the Evolution API.

### API Endpoints

#### `/webhook` (POST)

This is the endpoint where the Evolution API sends incoming messages from WhatsApp. It expects a JSON payload with the message details.

- **Example request body**:

    ```json
    {
      "event": "messages.upsert",
      "data": {
        "key": {
          "remoteJid": "group_id@g.us",
          "fromMe": false,
          "participant": "sender_number@whatsapp.net"
        },
        "message": {
          "conversation": "Hello, how are you?"
        }
      }
    }
    ```

- **Response**: The Flask app sends back an acknowledgment with the status `ok`.

## Configuration

The project requires several environment variables to be set for proper operation. These variables are listed below, and should be added to the `.env` file in the root directory.

### Required Environment Variables

- **EVOLUTION_TOKEN**: Your Evolution API token.
- **GRUPO_ID_DESEJADO**: The WhatsApp group ID you want to interact with.
- **INSTANCE**: The instance name used for Evolution API (e.g., "Gustavo VSL").
- **URL_ENVIO**: The URL to send messages via Evolution API.
- **PROMPT**: The message prompt template used by the language model (Mistral or Llama).
- **SERVER_URL**: The URL for the Evolution API server.
- **DEL_INSTANCE**: Boolean flag to indicate whether the instance should be deleted (default `false`).
- **PROVIDER_ENABLED**: Set to `false` to disable external providers.
- **DATABASE_ENABLED**: Set to `true` to enable the use of a database (e.g., PostgreSQL).
- **DATABASE_PROVIDER**: The type of database to use (e.g., `postgresql`).
- **DATABASE_CONNECTION_URI**: The URI used to connect to the database (PostgreSQL example).
- **DATABASE_SAVE_DATA_INSTANCE**: Set to `true` to save instance data.
- **DATABASE_SAVE_DATA_NEW_MESSAGE**: Set to `true` to save new message data.
- **DATABASE_CONNECTION_CLIENT_NAME**: The client name for the database connection.
- **WA_BUSINESS_TOKEN_WEBHOOK**: The token for WhatsApp Business API webhook.
- **WA_BUSINESS_URL**: The base URL for the WhatsApp Business API.
- **WA_BUSINESS_VERSION**: The version of the WhatsApp Business API.
- **WA_BUSINESS_LANGUAGE**: The language code (e.g., `pt_BR` for Portuguese).
- **WEBHOOK_EVENTS_QRCODE_UPDATED**: Set to `true` to trigger events for updated QR codes.
- **WEBHOOK_EVENTS_MESSAGES_SET**: Set to `true` to trigger events for message sets.
- **WEBHOOK_EVENTS_MESSAGES_UPSERT**: Set to `true` to trigger events for message upserts.
- **WEBHOOK_EVENTS_MESSAGES_EDITED**: Set to `true` to trigger events for edited messages.
- **WEBHOOK_EVENTS_MESSAGES_UPDATE**: Set to `true` to trigger events for message updates.
- **WEBHOOK_EVENTS_MESSAGES_DELETE**: Set to `true` to trigger events for deleted messages.
- **WEBHOOK_EVENTS_SEND_MESSAGE**: Set to `true` to trigger events for sent messages.
- **WEBHOOK_EVENTS_CONTACTS_SET**: Set to `true` to trigger events for contact sets.
- **WEBHOOK_EVENTS_CONTACTS_UPSERT**: Set to `true` to trigger events for contact upserts.
- **WEBHOOK_EVENTS_CONTACTS_UPDATE**: Set to `true` to trigger events for contact updates.
- **WEBHOOK_EVENTS_PRESENCE_UPDATE**: Set to `true` to trigger events for presence updates.
- **WEBHOOK_EVENTS_CHATS_SET**: Set to `true` to trigger events for chat sets.
- **WEBHOOK_EVENTS_CHATS_UPSERT**: Set to `true` to trigger events for chat upserts.
- **WEBHOOK_EVENTS_CHATS_UPDATE**: Set to `true` to trigger events for chat updates.
- **WEBHOOK_EVENTS_CHATS_DELETE**: Set to `true` to trigger events for deleted chats.
- **WEBHOOK_EVENTS_GROUPS_UPSERT**: Set to `true` to trigger events for group upserts.
- **WEBHOOK_EVENTS_GROUPS_UPDATE**: Set to `true` to trigger events for group updates.
- **WEBHOOK_EVENTS_GROUP_PARTICIPANTS_UPDATE**: Set to `true` to trigger events for group participant updates.
- **WEBHOOK_EVENTS_CONNECTION_UPDATE**: Set to `true` to trigger events for connection updates.
- **WEBHOOK_EVENTS_CALL**: Set to `true` to trigger events for calls.
- **CONFIG_SESSION_PHONE_CLIENT**: The client for the session (e.g., `Whatsapp`).
- **CONFIG_SESSION_PHONE_NAME**: The name of the phone used for the session (e.g., `Chrome`).
- **CONFIG_SESSION_PHONE_VERSION**: The version of the phone used for the session.
- **QRCODE_LIMIT**: The maximum number of allowed QR codes (default `30`).
- **AUTHENTICATION_API_KEY**: API key used for authentication with the Evolution API.
- **AUTHENTICATION_EXPOSE_IN_FETCH_INSTANCES**: Set to `true` to expose instances when fetching.
- **CACHE_REDIS_ENABLED**: Set to `true` to enable Redis cache.
- **CACHE_REDIS_URI**: The URI for the Redis server.
- **CACHE_REDIS_PREFIX_KEY**: The prefix for the Redis cache keys.
- **CACHE_REDIS_SAVE_INSTANCES**: Set to `true` to save instances in Redis.
- **CACHE_LOCAL_ENABLED**: Set to `false` to disable local cache.
- **LANGUAGE**: The language setting (e.g., `pt_BR` for Portuguese).

## Development

1. Clone the repository and install dependencies locally if necessary.

2. Set up the `.env` file with your local configurations.

3. Run the Flask app locally for testing purposes:

    ```bash
    python app.py
    ```

4. The local server will be available at `http://localhost:5001`.

## Troubleshooting

- **Problem: Evolution API is not receiving webhook data.**

    - Make sure the `webhook` URL is correctly set in the Evolution API configuration.
    - Ensure that the Evolution API and Flask app are both running and accessible.

- **Problem: Model responses are not generated correctly.**

    - Ensure that the `llama` or Mistral model is properly set up and accessible in the environment.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
