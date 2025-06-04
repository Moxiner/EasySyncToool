import sys
import os
import shutil
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QTreeWidgetItem,
    QFileDialog,
    QVBoxLayout,
    QWidget,
    QMessageBox,
    QHBoxLayout,
)
from PyQt5.QtCore import Qt

from qfluentwidgets import TreeWidget, PushButton, PrimaryPushButton


class FileSyncTool(QMainWindow):
    def __init__(self):
        super().__init__()
        self.source_folder = ""
        self.initUI()

    def initUI(self):
        self.setWindowTitle("EasySyncTool")
        self.setGeometry(300, 300, 800, 600)

        # 创建组件
        self.tree = TreeWidget()
        self.tree.setHeaderLabel("目录结构")
        self.tree.setSelectionMode(TreeWidget.ExtendedSelection)

        self.btn_select = PushButton("选择文件夹")
        self.btn_export = PrimaryPushButton("导出同步包")

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

        # 获取目录内容并排序
        items = os.listdir(path)
        # 先文件夹后文件排序
        items = sorted(
            items, key=lambda x: (not os.path.isdir(os.path.join(path, x)), x)
        )

        for item in items:
            item_path = os.path.join(path, item)
            node = QTreeWidgetItem()
            node.setText(0, item)
            node.setData(0, Qt.UserRole, item_path)
            node.setCheckState(0, Qt.Unchecked)

            if os.path.isdir(item_path):
                root.addChild(node)
                self.add_tree_items(node, item_path)
            else:
                root.addChild(node)

    def add_tree_items(self, parent, path):
        try:
            # 获取目录内容并排序
            items = os.listdir(path)
            # 先文件夹后文件排序
            items = sorted(
                items, key=lambda x: (not os.path.isdir(os.path.join(path, x)), x)
            )

            for item in items:
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
            QMessageBox.warning(
                self,
                "权限错误",
                f"无法访问 {path}，请确认您有权限访问该文件夹",
            )

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
        if not self.get_checked_items():
            QMessageBox.warning(self, "错误", "请选择要导出的文件/文件夹")
            return
        if not self.source_folder:
            QMessageBox.warning(self, "错误", "请先选择源文件夹")
            return

        # 选择目标路径
        target_dir = QFileDialog.getExistingDirectory(self, "选择保存位置")
        if not target_dir:
            QMessageBox.warning(self, "错误", "请先选择保存位置")
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

            # 确保目标目录存在
            dest_dir = os.path.dirname(dest)
            if not os.path.exists(dest_dir):
                os.makedirs(dest_dir)

            if os.path.isfile(path):
                shutil.copy2(path, dest)
            elif os.path.isdir(path):
                shutil.copytree(path, dest)

        # 按照先文件夹后文件排序
        for root, dirs, files in os.walk(temp_dir):
            dirs.sort()  # 先对文件夹进行排序
            files.sort()  # 再对文件进行排序

        # 压缩目录
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        root_folder = self.source_folder.split("/")[-1]
        final_zip_name = f"[SyncPacket]{root_folder}_{timestamp}"
        zip_path = os.path.join(target_dir, final_zip_name)

        # 创建压缩包并删除临时目录
        shutil.make_archive(zip_path, "zip", temp_dir)
        # shutil.rmtree(temp_dir)
        QMessageBox.information(
            self,
            "导出完成",
            f"导出完成，同步包保存在：{zip_path}.zip",
        )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = FileSyncTool()
    ex.show()
    sys.exit(app.exec_())
