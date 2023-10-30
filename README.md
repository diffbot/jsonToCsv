# JSON to CSV Converter

A very fast and unopinionated JSON to CSV converter built with [msgspec](https://jcristharif.com/msgspec/index.html). 

* **Accepts all types of JSON.** Even large and complicated ones.
* **Customizable.** Choose only the columns you need.
* **Open source.** Self-host and run the app entirely offline.

Just need the conversion script? See `jsonToCsv.py`.

## Getting Started
The easiest way to get started is to use the hosted tool at [json.diffbot.com](https://json.diffbot.com). No login is required and it's completely free to use.

If you have a large JSON file to convert (>2gb), or if privacy is necessary, clone this repo locally and follow the instructions below to run and install locally.

## How to Run Locally

### Install Dependencies
```sh
npm install
pip install requirements.txt
```

### Start the App
Frontend
```sh
npx vite build --watch
```
Backend
```sh
flask run
```

## Acknowledgements
Many thanks to Jim Crist-Harif for [msgspec](https://jcristharif.com/msgspec/index.html) and [Diffbot](https://www.diffbot.com) for hosting this tool.