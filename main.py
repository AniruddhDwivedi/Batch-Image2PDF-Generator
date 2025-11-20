from PIL import Image
import sys
from PyQt6.QtWidgets import QDialog, QLineEdit, QDialogButtonBox, QApplication, QMainWindow, QWidget, QHBoxLayout, QPushButton, QVBoxLayout, QLabel, QFileDialog
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QIcon
import os
import webbrowser
import re
from PyPDF2 import PdfMerger

HERE = os.path.dirname(os.path.abspath(__file__))
dir_list = []

def list_dirs(root_dir):
    for dirpath, dirnames, filenames in os.walk(root_dir):
        if not dirnames:
            dir_list.append(dirpath)

def merge_pdfs_in_directory(directory_path, output_filename="example.pdf"):
    merger = PdfMerger()
    pdf_files = sorted([os.path.join(directory_path, f) for f in os.listdir(directory_path) if f.endswith(".pdf")])

    for pdf_file in pdf_files:
        merger.append(pdf_file)

    with open(os.path.join(directory_path, output_filename), "wb") as output_file:
        merger.write(output_file)
    merger.close()

def images_to_pdf(folder_path, output_pdf_name="output.pdf", export_path=HERE):
    images = []
    fileList = os.listdir(folder_path)
    sortedList = []
    for i in range(0, len(fileList)):
        try:
            thisFile = int(fileList[i][0:-4])
            sortedList.append(thisFile)
        except:
            print("There may be a non-image file, please remove that");
            return

    sortedList.sort()

    for filename in sortedList:
        filepath = os.path.join(folder_path, str(filename) + ".png")
        if os.path.exists(filepath):
            img = Image.open(filepath).convert('RGB')
            images.append(img)


    if not images:
       print("No images found in the specified folder.")
       return

    images[0].save(os.path.join(export_path, output_pdf_name), save_all=True, append_images=images[1:])

def create_pdfs(fp, ex):
    for i in range(len(dir_list)):
        temp = str("out_" + str(i) + ".pdf")
        images_to_pdf(dir_list[i], temp, ex)

def mainExec(folder_path, output_pdf_name="output.pdf", export_path=HERE):
    list_dirs(folder_path)
    create_pdfs(folder_path, export_path)

    merge_pdfs_in_directory(export_path, output_pdf_name)
    clue = r"^out_\d+\.pdf$"
    for file in os.listdir(export_path):
        if re.match(clue, file):
            file_path = os.path.join(export_path, file)
            os.remove(file_path)

prevText = """Create a pdf from several (numbered) images"""

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Batch Image2PDF Generator")
        self.set_centered_geometry(1200, 400)
        widget = QWidget()
        self.setCentralWidget(widget)
        self.folder_path = ""
        self.export_folder_path = os.getcwd()
        self.exported_file = ""

        layout = QVBoxLayout()

        self.title = QLabel(prevText)
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.title)

        self.open_folder_button = QPushButton("Select Folder")
        self.open_folder_button.clicked.connect(self.open_file_dialog)
        self.open_folder_button.setFixedSize(1200, 30)
        layout.addWidget(self.open_folder_button)

        self.create_pdf_button = QPushButton("Create PDF")
        self.create_pdf_button.clicked.connect(self.create_pdf)
        self.create_pdf_button.setFixedSize(1200, 30)
        layout.addWidget(self.create_pdf_button)
        self.create_pdf_button.hide()

        self.preview = QLabel("Preview will appear here")
        self.preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview.setFixedHeight(300)
        layout.addWidget(self.preview)

        sublayout = QHBoxLayout()
        
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Enter Converted PDF Name")
        self.title_input.setFixedSize(800, 30)
        sublayout.addWidget(self.title_input)
        self.title_input.hide()

        self.export_folder_select = QPushButton("Select Export Folder")
        self.export_folder_select.clicked.connect(self.select_export_dir)
        self.export_folder_select.setFixedSize(400, 30)
        sublayout.addWidget(self.export_folder_select)
        self.export_folder_select.hide()

        self.export_folder = QLabel()
        layout.addWidget(self.export_folder)

        self.view_file_button = QPushButton("View PDF")
        self.view_file_button.clicked.connect(self.open_file)
        self.view_file_button.setFixedSize(1200, 40)
        layout.addWidget(self.view_file_button)
        self.view_file_button.hide()

        layout.addLayout(sublayout)
        widget.setLayout(layout)

    def open_file(self):
        should_be_here = os.path.join(self.export_folder_path, self.exported_file)
        if os.path.exists(should_be_here):
            webbrowser.open_new_tab(should_be_here)

    def open_file_dialog(self):
        self.folder_path = QFileDialog.getExistingDirectory(self, "Select Directory")
        if self.folder_path:
            print(f"Selected folder: {self.folder_path}")
            filenum = len(os.listdir(self.folder_path))
            self.preview.setText(f"There are {filenum} files in selected folder")

            self.title_input.show()
            self.export_folder_select.show()

        else:
            print("No folder selected.")
    
    def select_export_dir(self):
        self.export_folder_path = QFileDialog.getExistingDirectory(self, "Select Export Directory")
        if self.export_folder_path:
            print(f"Selected Export folder: {self.export_folder_path}")
            self.preview.setText(self.preview.text() + f"\n\n Export Folder Selected: \n{self.export_folder_path}")
            self.create_pdf_button.show()
        else:
            print("No folder selected.")

    def create_pdf(self):
        docName = self.title_input.text().strip() if self.title_input.text() != "" else "test.pdf"
        target_dir = self.folder_path
        export_path = HERE if not self.export_folder_path else self.export_folder_path

        if docName[-4:] != ".pdf":
            docName += ".pdf"
        self.exported_file = docName
        
        mainExec(target_dir, docName, export_path) 

        self.preview.setText("PDF Created")
        self.title_input.hide()
        self.export_folder_select.hide()
        self.create_pdf_button.hide()
        self.view_file_button.show()

    def set_centered_geometry(self, w: int, h: int):
        screen = QApplication.primaryScreen().availableGeometry()
        x = (screen.width() - w) // 2
        y = (screen.height() - h) // 2
        self.setGeometry(x, y, w, h)

app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec())