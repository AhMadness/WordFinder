# Standard library imports
import os
import sys
from datetime import timedelta

# Third party imports
from PyQt6.QtWidgets import QApplication, QPushButton, QVBoxLayout, QWidget, QLineEdit, QMessageBox, QHBoxLayout, \
    QLabel, QTextEdit
from PyQt6.QtGui import QPalette, QColor, QTextOption
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal

# Local imports
import whisper


# Function definitions
def format_timestamp(seconds: float, always_include_hours: bool = False, decimal_marker: str = '.'):
    """ Converts seconds into a string timestamp. """
    assert seconds >= 0, "Non-negative timestamp expected"
    time_delta = timedelta(seconds=seconds)
    total_milliseconds = int(time_delta.total_seconds() * 1000)
    milliseconds = total_milliseconds % 1000

    hours, remainder = divmod(total_milliseconds, 3600000)
    minutes, seconds = divmod(remainder, 60000)
    seconds //= 1000  # Convert milliseconds to seconds

    hours_marker = f"{hours:02d}:" if always_include_hours or hours > 0 else ""
    return f"{hours_marker}{minutes:02d}:{seconds:02d}{decimal_marker}{milliseconds:03d}"


class FileEdit(QLineEdit):
    def __init__(self):
        super().__init__()
        self.setDragEnabled(True)
        self.setFixedWidth(29)

    def dragEnterEvent(self, e):
        if e.mimeData().hasUrls():
            e.accept()
        else:
            e.ignore()

    def dragMoveEvent(self, e):
        if e.mimeData().hasUrls():
            e.setDropAction(Qt.DropAction.CopyAction)
            e.accept()
        else:
            e.ignore()

    def dropEvent(self, e):
        if e.mimeData().hasUrls():
            e.setDropAction(Qt.DropAction.CopyAction)
            e.accept()
            for url in e.mimeData().urls():
                filepath = str(url.toLocalFile())
                self.setText(filepath)

                # Bring the application window to the front and give it focus
                self.window().raise_()
                self.window().activateWindow()

                # Set focus to the QLineEdit after a small delay
                QTimer.singleShot(100, self.setFocus)
        else:
            e.ignore()


# Class definitions
class Worker(QThread):
    """ Thread worker to process audio and emit progress. """
    progress = pyqtSignal(str)

    def __init__(self, input_text, wordsList):
        super().__init__()
        self.input_text = input_text
        self.wordsList = wordsList

    def run(self):
        """ Main execution method for the thread. """
        base_name = os.path.basename(self.input_text)
        name, ext = os.path.splitext(base_name)
        out_file = os.path.join(os.path.dirname(self.input_text), f"{name}.txt")

        try:
            segments = self.process_audio(self.input_text)
            self.write_file(out_file, segments)
            self.progress.emit(out_file)
        except Exception as e:
            self.progress.emit('Error: ' + str(e))

    def process_audio(self, file_path):
        """ Processes audio and extracts segments containing specific words. """
        model = whisper.load_model("base")
        input = model.transcribe(file_path, language="en", fp16=False, verbose=True)
        # Setting verbose = True adds the real-time transcript. Setting it to false adds the progress bar.
        segments = []

        for segment in input["segments"]:
            segment["start"] = format_timestamp(segment['start'])
            segment["start"] = segment["start"].replace('[', '').replace(']', '').replace('.', '').replace(' --> ', ' - ')
            segment["start"] = segment["start"][0:5]

            # Convert the text to lower case for case-insensitive comparison
            segment_text_lower = segment['text'].lower()

            # Check if any word in words list is in segment's text
            if any(word.lower() in segment_text_lower for word in self.wordsList):
                # Add to list
                segments.append(f"{segment['start']} - {segment['text']}\n\n")

        return segments

    @staticmethod
    def write_file(file_path, segments):
        """ Writes segments to a file. """
        with open(file_path, "w") as output_file:
            for segment in segments:
                output_file.write(segment)


class AppDemo(QWidget):
    def __init__(self):
        super().__init__()

        # Set the window title
        self.setWindowTitle("WordFinder")

        mainLayout = QVBoxLayout()

        self.edit1 = FileEdit()
        self.edit1.returnPressed.connect(self.execute)
        self.edit1.setMaximumSize(100, 58)
        self.edit1.setPlaceholderText("Drop video here")

        self.btn2 = QPushButton('Find', clicked=self.execute)
        self.btn2.setMaximumSize(50, 25)
        self.btn2.setStyleSheet("color: black")

        hLayout = QHBoxLayout()
        hLayout.addStretch()
        hLayout.addWidget(self.edit1)
        hLayout.addStretch()

        self.wordsList = []  # List to store the words

        # Change QLineEdit to QTextEdit for word input
        self.wordsInput = QTextEdit()
        self.wordsInput.setPlaceholderText("Example:\nhello, there, general, kenobi")
        self.wordsInput.setMaximumHeight(58)
        self.wordsInput.setMaximumWidth(100)
        self.wordsInput.textChanged.connect(self.updateWordsList)  # Connect to the textChanged signal


        # Modify the layout to include new widgets
        wordsLayout = QHBoxLayout()
        wordsLayout.addWidget(self.wordsInput)

        mainLayout.addLayout(wordsLayout)  # Add the words layout to the main layout

        buttonLayout = QHBoxLayout()  # Create a new layout for the button
        buttonLayout.addStretch()
        buttonLayout.addWidget(self.btn2)
        buttonLayout.addStretch()

        mainLayout.addLayout(hLayout)
        mainLayout.addLayout(buttonLayout)  # Add the button layout to the main layout

        self.setLayout(mainLayout)
        self.setFixedSize(150, 200)

        self.mpos = None

    def mousePressEvent(self, event):
        self.mpos = event.globalPosition()

    def mouseMoveEvent(self, event):
        if self.mpos is not None:
            diff = event.globalPosition() - self.mpos
            newpos = self.pos() + diff.toPoint()
            self.move(newpos)
            self.mpos = event.globalPosition()

    def mouseReleaseEvent(self, event):
        self.mpos = None

    def updateWordsList(self):
        # Update the words list from the text input
        text = self.wordsInput.toPlainText()  # Use toPlainText to get the text
        self.wordsList = [word.strip() for word in text.split(',') if word.strip()]


    def execute(self):
        # In the execute method, you will need to process self.wordsList
        input_text = self.edit1.text()

        if not os.path.isfile(input_text):
            QMessageBox.critical(self, "Error", "File not found!")
            return

        # Pass the words list to the Worker thread
        self.worker = Worker(input_text, self.wordsList)  # Assuming you modify Worker to accept the words list
        self.worker.progress.connect(self.on_progress)
        self.worker.start()

        # Disable the input field and button while processing
        self.edit1.setEnabled(False)
        self.btn2.setEnabled(False)
        # Change the text on the button to "Searching"
        self.btn2.setText("Searching...")
        self.btn2.setMaximumSize(64, 25)  # Set the maximum size of the button
        self.btn2.setStyleSheet("background-color: #323232; color: white; border: 0px;")
        # Change the border color of the QLineEdit to red
        self.edit1.setStyleSheet("border: 1px solid red;")

    def on_progress(self, message):
        if message.startswith('Error: '):
            QMessageBox.critical(self, "Error", message[6:])
        else:
            self.edit1.setText('')
            os.startfile(message)

        # Enable the input field and button after processing
        self.edit1.setEnabled(True)
        self.btn2.setEnabled(True)
        # Change the text on the button back to "Transcribe"
        self.btn2.setText("Find")
        self.btn2.setMaximumSize(50, 25)  # Set the maximum size of the button
        self.btn2.setStyleSheet("color: black")
        # Change the border color of the QLineEdit back to the default
        self.edit1.setStyleSheet("")


def main():
    app = QApplication(sys.argv)

    # Set the palette to a dark theme.
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(50, 50, 50))
    palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
    app.setPalette(palette)

    # Set global stylesheet for the application
    app.setStyleSheet("QMessageBox QLabel{ color: black; } QMessageBox QPushButton{ color: black; }")

    demo = AppDemo()
    demo.show()

    sys.exit(app.exec())


if __name__ == '__main__':
    main()
