# ![logo](https://upload.wikimedia.org/wikipedia/commons/d/d5/Slack_icon_2019.svg) My TaskBuddy😽 Slack Bot  

  

  

This bot was created for **Adobe Career Academy 2023 Technical Project.**

  

  

## Usage

  Run on: `main.py`

In your Slack App, type `@TaskBuddy` to view all available commands!

  

  

## Commands

  

  

### 1. time

  

```bash

/time

```

  

The command will display current date and time 🕓

  

  

### 2. joke

  

```bash

/joke

```

  

The command will tell a joke 🙃

  

  

### 3. infocity

  
  
  

Type the command with a `city name` to display information about the input city 🌆

```bash

/infocity + a_name_of_a_city

```

  

### 4. translate

  
  

Type the command with a `message in a language which is not English` to translate the message to English 🇺🇸

```bash

/translate + a_message_in_a_lang_not_English

```

  

### 5. task

  

```bash

/task

```

  

The command will open a simple to-do list app 😽

  

## Database 

Sample users' table structure in tasks.db file

| userId | username  | password  | task_list       | isActive |
|--------|-----------|-----------|-----------------|----------|
| 1      | john  | ********  | ["Shopping", "Email"]|   1    |
| 2      | ben| ********  | ["Work", "Meetings"]  |   0     |
| 3      | alice  | ********  | ["Study", "Research"] |   1    |

__Notes__: `1` means user in a sign-in (active) state, `0` means user in a sign-out (in-active) state.

## APIs were used

[Slack Bolt API](https://api.slack.com/tools/bolt)<br>
[Slack API Socket Mode](https://api.slack.com/apis/connections/socket) <br>
[Open-Meteo API](https://open-meteo.com/)

## Adobe Express Presentation
[Project Presentation Page](https://express.adobe.com/page/itDRYn7Zxz5lZ/)