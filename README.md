# 🏫 SchoolDigger MCP Server

An MCP server to interact with [SchoolDigger's](https://www.schooldigger.com/) school and district data API.

## Features

- 🔍 Search schools by name and location
- 📊 Get detailed school information
- 📍Find schools by zip code
- 🏆 Get best ranked schools by city
- 🏛️ Search school districts
- 🎯 Filter schools within districts

## Quick start

Add the following to your MCP config file

```bash
{
  "mcpServers": {
    "schooldigger": {
      "command": "uv",
      "args": [
        "--directory",
        "/ABSOLUTE/PATH/TO/PARENT/FOLDER/schooldigger-mcp",
        "run",
        "server.py"
      ],
      "env": {
        "SCHOOLDIGGER_API_ID": "<API ID>",
        "SCHOOLDIGGER_API_KEY": "<API KEY>"
      }
    }
  }
```


## Installation
1. Clone the repo

```bash
git clone https://github.com/pajaydev/schooldigger-mcp.git
cd schooldigger-mcp
```

2. Install the dependencies

```bash
uv sync
uv add pytest  # For testing
```

2. Run the server

```bash
# Stdio mode
uv run server.py

# HTTP server mode
uv run server.py --http --port 8080
```

👋 Appreciate if you can create an issue if you see any problem running this MCP