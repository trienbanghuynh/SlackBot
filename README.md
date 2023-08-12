# ![logo](https://upload.wikimedia.org/wikipedia/commons/d/d5/Slack_icon_2019.svg) My TaskBuddy😽 Slack Bot  

  

  

This bot was created for **Adobe Career Academy 2023 Technical Project.**

  

  

## Usage

  Run on: `main.py`

On Slack Workspace, type `@TaskBuddy` to view all available commands!

  

  

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

  

## Database ("tasks.db")

Sample users' table structure

| userId | username | password | task_list | isActive |

|--------|----------|----------|-----------|----------|

| 1 | user1 | pass123 | ["task11"] | 1 |

| 2 | user2 | pass456 | ["task21", "task22", "task23"] | 0 |

| 3 | user3 | pass789 | ["task31", "task32"] | 1 |

  

## APIs were used

[Slack Bolt API](https://api.slack.com/tools/bolt)
[Slack API Socket Mode](https://api.slack.com/apis/connections/socket) 
[Open-Meteo API](https://open-meteo.com/)

## Presentation
[Project Presentation](https://express.adobe.com/page/itDRYn7Zxz5lZ/)