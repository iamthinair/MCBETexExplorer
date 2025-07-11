import os
import re
from PyQt5.QtWidgets import QMainWindow, QFileSystemModel, QTreeView, QLabel, QSplitter, QWidget, QVBoxLayout, QMenu, QMessageBox, QFileDialog
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt, QTimer
# from texture_viewer import setup_animation, setup_grid_animation, setup_multifile_animation
from imageutils import load_image_with_pillow
import sys
from texture_viewer import TextureViewer

class TextureViewer(QMainWindow):
    def __init__(self, root_path):
        super().__init__()
        self.setWindowTitle('Minecraft Bedrock Texture Viewer')
        icon_path = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), 'texicon.ico')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        self.resize(1000, 600)

        self.current_pixmap = None
        self.frames = []
        self.current_frame = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.next_frame)

        splitter = QSplitter(Qt.Horizontal)
        self.setCentralWidget(splitter)

        self.model = QFileSystemModel()
        self.model.setRootPath(root_path)
        self.model.setNameFilters(['*.png', '*.tga'])
        self.model.setNameFilterDisables(False)

        self.tree = QTreeView()
        self.tree.setModel(self.model)
        self.tree.setRootIndex(self.model.index(root_path))
        self.tree.setColumnWidth(0, 250)
        self.tree.clicked.connect(self.on_tree_clicked)
        splitter.addWidget(self.tree)

        image_widget = QWidget()
        vbox = QVBoxLayout()
        self.image_label = QLabel('Select a texture file to preview')
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setMinimumSize(400, 400)
        self.image_label.setStyleSheet('background: #222; color: #fff;')
        vbox.addWidget(self.image_label)
        image_widget.setLayout(vbox)
        splitter.addWidget(image_widget)

        self.image_label.setContextMenuPolicy(Qt.CustomContextMenu)
        self.image_label.customContextMenuRequested.connect(self.show_image_context_menu)

    def on_tree_clicked(self, index):
        file_path = self.model.filePath(index)
        if os.path.isfile(file_path) and (file_path.endswith('.png') or file_path.endswith('.tga')):
            pixmap = QPixmap(file_path)
            if pixmap.isNull() and file_path.lower().endswith('.tga'):
                pixmap = load_image_with_pillow(file_path)
            if not pixmap.isNull():
                self.current_pixmap = pixmap
                rel_path = os.path.relpath(file_path, self.model.rootPath())
                rel_path = rel_path.replace('\\', '/').replace('\\', '/')
                # Animation/special cases
                if rel_path == 'particle/campfire_smoke.png':
                    self.setup_animation(frame_count=12, orientation='Vertical')
                elif rel_path == 'flame_atlas.png':
                    self.setup_animation(frame_width=16, frame_height=16, orientation='Vertical', flame_atlas=True)
                elif rel_path == 'environment/moon_phases.png':
                    self.setup_grid_animation(columns=4, rows=2)
                elif re.match(r'environment/destroy_stage_\d+\.png', rel_path):
                    self.setup_multifile_animation(file_path, prefix_pattern=r'(destroy_stage_)\d+\.png', glob_prefix='destroy_stage_')
                elif re.match(r'blocks/beetroots_stage_\d+\.png', rel_path):
                    self.setup_multifile_animation(file_path, prefix_pattern=r'(beetroots_stage_)\d+\.png', glob_prefix='beetroots_stage_')
                elif re.match(r'blocks/carrots_stage_\d+\.png', rel_path):
                    self.setup_multifile_animation(file_path, prefix_pattern=r'(carrots_stage_)\d+\.png', glob_prefix='carrots_stage_')
                elif re.match(r'blocks/anvil_top_damaged_\d+\.png', rel_path):
                    self.setup_multifile_animation(file_path, prefix_pattern=r'(anvil_top_damaged_)\d+\.png', glob_prefix='anvil_top_damaged_')
                elif re.match(r'blocks/cocoa_stage_\d+\.png', rel_path):
                    self.setup_multifile_animation(file_path, prefix_pattern=r'(cocoa_stage_)\d+\.png', glob_prefix='cocoa_stage_')
                elif re.match(r'blocks/comparator_(on|off)\.png', rel_path):
                    self.setup_multifile_animation(file_path, prefix_pattern=r'(comparator_)(on|off)\.png', glob_prefix='comparator_', is_on_off=True)
                elif re.match(r'blocks/conduit_(closed|open)\.png', rel_path):
                    self.setup_multifile_animation(file_path, prefix_pattern=r'(conduit_)(closed|open)\.png', glob_prefix='conduit_', is_on_off=True)
                elif rel_path == 'blocks/campfire.png':
                    self.setup_animation(frame_count=8, orientation='Vertical')
                elif re.match(r'blocks/bubble_column_inner_.*\.png', rel_path) or re.match(r'blocks/bubble_column/inner_.*\.png', rel_path):
                    self.setup_animation(frame_count=32, orientation='Vertical')
                elif re.match(r'blocks/bubble_column_outer_.*\.png', rel_path) or re.match(r'blocks/bubble_column/outer_.*\.png', rel_path):
                    self.setup_animation(frame_count=32, orientation='Vertical')
                else:
                    self.timer.stop()
                    self.frames = [self.current_pixmap]
                    self.show_frame(0)
            else:
                self.image_label.setText('Failed to load image')
        else:
            self.image_label.setText('Select a texture file to preview')
            self.timer.stop()

    def show_frame(self, idx):
        if not self.frames:
            return
        frame = self.frames[idx % len(self.frames)]
        pixmap = frame.scaled(
            self.image_label.size(), Qt.KeepAspectRatio, Qt.FastTransformation)
        self.image_label.setPixmap(pixmap)

    def next_frame(self):
        self.current_frame = (self.current_frame + 1) % len(self.frames)
        self.show_frame(self.current_frame)

    def resizeEvent(self, event):
        if self.frames:
            self.show_frame(self.current_frame)
        elif self.image_label.pixmap():
            self.image_label.setPixmap(self.image_label.pixmap().scaled(
                self.image_label.size(), Qt.KeepAspectRatio, Qt.FastTransformation))
        super().resizeEvent(event)

    def show_image_context_menu(self, pos):
        if not self.frames or len(self.frames) <= 1:
            return
        menu = QMenu()
        export_action = menu.addAction('Export as GIF')
        action = menu.exec_(self.image_label.mapToGlobal(pos))
        if action == export_action:
            self.export_gif()

    def export_gif(self):
        if not self.frames or len(self.frames) <= 1:
            QMessageBox.information(self, 'Export as GIF', 'No animation to export.')
            return
        path, _ = QFileDialog.getSaveFileName(self, 'Save GIF', '', 'GIF Files (*.gif)')
        if not path:
            return
        images = []
        from PIL import Image
        for frame in self.frames:
            qimg = frame.toImage().convertToFormat(4)  # Format_ARGB32
            width = qimg.width()
            height = qimg.height()
            ptr = qimg.bits()
            ptr.setsize(qimg.byteCount())
            arr = bytes(ptr)
            img = Image.frombuffer('RGBA', (width, height), arr, 'raw', 'BGRA', 0, 1)
            images.append(img)
        images[0].save(path, save_all=True, append_images=images[1:], duration=100, loop=0, disposal=2)
        QMessageBox.information(self, 'Export as GIF', f'GIF saved to {path}') 