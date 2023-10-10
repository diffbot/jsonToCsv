# JSON to CSV Converter

A very fast and unopinionated JSON to CSV converter built with [msgspec](https://jcristharif.com/msgspec/index.html). 

* **Accepts all types of JSON.** Even large and complicated ones.
* **Customizable.** Choose only the columns you need.
* **Open source.** Self-host and run the app entirely offline.

Just need the conversion script? See `jsonToCsv.py`.

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