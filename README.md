# ![logo](https://upload.wikimedia.org/wikipedia/commons/d/d5/Slack_icon_2019.svg) [Slack](https://slack.com/) Bot @TaskBuddy

  

This bot was created as **Adobe Career Academy Project**

  

## Usage

Type `@TaskBuddy` to view all available commands and get started!

  

## Available commands

  

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



Type the command with a `city name` to display information about the requested city 🌆
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

The command will open a simple task app

## Database ("tasks.db")
Sample users' table structure
| userId | username | password | task_list | isActive |
|--------|----------|----------|-----------|----------|
| 1      | user1    | pass123  | [task1-1]    | 1      |
| 2      | user2    | pass456  | [task2-1, task2-2, task2-3]    | 0       |
| 3      | user3    | pass789  | [task3-1, task3-2]    | 1      |

## APIs were used
[Slack Bolt API](https://api.slack.com/tools/bolt)
[Open-Meteo API](https://open-meteo.com/)
