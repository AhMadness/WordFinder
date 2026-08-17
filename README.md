# WordFinder

WordFinder is a compact PyQt6 desktop tool that uses OpenAI Whisper to find
words or phrases in audio and video. It writes each matching transcript segment
and its timestamp to a text file beside the source media.

## Features

- Drag-and-drop audio and video input
- Comma-separated word and phrase matching
- Local transcription with Whisper's `base` model
- Timestamped UTF-8 text output
- Background processing that keeps the interface responsive

## Screenshots

### Search

![WordFinder search interface](https://github.com/AhMadness/WordFinder/assets/48402736/ca045bcb-6f56-445f-b7c5-1d2835ee962d)

### Results

![Timestamped WordFinder results](https://github.com/AhMadness/WordFinder/assets/48402736/9fbc6fca-921e-4633-a722-2a4ffd77d576)

## Requirements

- Python 3.10 or newer
- [FFmpeg](https://ffmpeg.org/download.html) available on `PATH`

Whisper downloads the `base` model the first time WordFinder transcribes a
file. Transcription runs locally after the model is available.

## Run Locally

```powershell
git clone https://github.com/AhMadness/WordFinder.git
cd WordFinder
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python main.py
```

Drop a media file into the window, enter comma-separated search terms, and
select **Find**. WordFinder creates a `.txt` file beside the media file and
opens it automatically on Windows.

## Tests

```powershell
python -m unittest discover -s tests -v
```

## License

[MIT](LICENSE)
