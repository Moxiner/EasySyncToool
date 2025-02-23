import sys
import os
import shutil
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QTreeWidget,
    QTreeWidgetItem,
    QFileDialog,
    QPushButton,
    QVBoxLayout,
    QWidget,
)
from PyQt5.QtCore import Qt


class FileSyncTool(QMainWindow):
    def __init__(self):
        super().__init__()
        self.source_folder = ""
        self.initUI()

    def initUI(self):
        self.setWindowTitle("EasySyncTool")
        self.setGeometry(300, 300, 800, 600)

        # 创建组件
        self.tree = QTreeWidget()
        self.tree.setHeaderLabel("目录结构")
        self.tree.setSelectionMode(QTreeWidget.ExtendedSelection)

        self.btn_select = QPushButton("选择文件夹")
        self.btn_export = QPushButton("导出同步包")

        # 布局
        layout = QVBoxLayout()
        layout.addWidget(self.btn_select)
        layout.addWidget(self.tree)
        layout.addWidget(self.btn_export)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # 事件绑定
        self.btn_select.clicked.connect(self.select_folder)
        self.btn_export.clicked.connect(self.export_files)

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "选择源文件夹")
        if folder:
            self.source_folder = folder
            self.populate_tree(folder)

    def populate_tree(self, path):
        self.tree.clear()
        root = QTreeWidgetItem(self.tree)
        root.setText(0, os.path.basename(path))
        root.setData(0, Qt.UserRole, path)
        root.setCheckState(0, Qt.Unchecked)
        self.add_tree_items(root, path)

    def add_tree_items(self, parent, path):
        try:
            for item in os.listdir(path):
                item_path = os.path.join(path, item)
                node = QTreeWidgetItem()
                node.setText(0, item)
                node.setData(0, Qt.UserRole, item_path)
                node.setCheckState(0, Qt.Unchecked)

                if os.path.isdir(item_path):
                    parent.addChild(node)
                    self.add_tree_items(node, item_path)
                else:
                    parent.addChild(node)
        except PermissionError:
            pass

    def get_checked_items(self, parent=None, checked_paths=None):
        if checked_paths is None:
            checked_paths = []
        if parent is None:
            parent = self.tree.invisibleRootItem()

        for i in range(parent.childCount()):
            child = parent.child(i)
            if child.checkState(0) == Qt.Checked:
                checked_paths.append(child.data(0, Qt.UserRole))
            self.get_checked_items(child, checked_paths)
        return checked_paths

    def export_files(self):
        if not self.source_folder:
            return

        # 选择目标路径
        target_dir = QFileDialog.getExistingDirectory(self, "选择保存位置")
        if not target_dir:
            return

        # 创建临时目录（步骤5）
        temp_dir = os.path.join(target_dir, "synctemp")
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        os.makedirs(temp_dir)

        # 复制选中的文件/文件夹
        checked_paths = self.get_checked_items()
        for path in checked_paths:
            relative_path = os.path.relpath(path, self.source_folder)
            dest = os.path.join(temp_dir, relative_path)

            if os.path.isfile(path):
                shutil.copy2(path, dest)
            elif os.path.isdir(path):
                shutil.copytree(path, dest)

        # 压缩目录
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        root_folder = self.source_folder.split("/")[-1]
        final_zip_name = f"[SyncPacket]{root_folder}_{timestamp}"
        zip_path = os.path.join(target_dir, final_zip_name)

        # 创建压缩包并删除临时目录
        shutil.make_archive(zip_path, "zip", temp_dir)
        # shutil.rmtree(temp_dir)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = FileSyncTool()
    ex.show()
    sys.exit(app.exec_())
