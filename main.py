import sys
from PyQt5.QtWidgets import QApplication, QFileDialog, QMessageBox
from texture_viewer import TextureViewer
import os

def get_assets_path():
    QMessageBox.information(None, "Select Minecraft Assets Folder", "Please select your Minecraft Bedrock Edition Assets Folder.")
    selected_folder = QFileDialog.getExistingDirectory(None, "Select your Minecraft Bedrock Edition Assets Folder")
    if selected_folder:
        textures_path = os.path.join(selected_folder, 'textures')
        return textures_path
    return selected_folder

if __name__ == '__main__':
    app = QApplication(sys.argv)
    root_path = get_assets_path()
    viewer = TextureViewer(root_path)
    viewer.show()
    sys.exit(app.exec_()) 