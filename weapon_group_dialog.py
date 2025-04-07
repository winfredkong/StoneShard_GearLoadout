
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QGridLayout, QToolButton, QLabel
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt, QSize
import os

class WeaponGroupDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Weapon Group")
        self.setFixedSize(1100, 900)
        self.selected = None

        layout = QVBoxLayout(self)

        # 무기군 카테고리 정의
        self.weapon_groups = {
            "ONE-HANDED": [
                "one_handed_sword", "one_handed_axe", "one_handed_mace",
                "one_handed_dagger", "one_handed_shield"
            ],
            "TWO-HANDED": [
                "two_handed_sword", "two_handed_axe", "two_handed_mace",
                "two_handed_spear", "two_handed_stave"
            ],
            "RANGED": [
                "two_handed_ranged_bow", "two_handed_ranged_crossbow"
            ]
        }

        for category, groups in self.weapon_groups.items():
            layout.addWidget(QLabel(f"<b>{category}</b>"))
            grid = QGridLayout()
            row, col = 0, 0
            for group in groups:
                btn = QToolButton()
                btn.setFixedSize(260, 130)
                btn.setIconSize(QSize(96, 96))
                img_path = os.path.join("assets", "weapon_group", f"{group}.png")
                if os.path.exists(img_path):
                    btn.setIcon(QIcon(QPixmap(img_path)))
                btn.setText(group.replace("_", " ").title())
                btn.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
                btn.clicked.connect(lambda _, g=group: self.select_group(g))
                grid.addWidget(btn, row, col)
                col += 1
                if col >= 4:
                    col = 0
                    row += 1
            layout.addLayout(grid)

    def select_group(self, group_name):
        self.selected = group_name
        self.accept()

    def selected_group(self):
        return self.selected
