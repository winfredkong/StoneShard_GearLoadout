import json
import os
import sys

from PyQt5.QtWidgets import (
    QDialog, QLabel, QCheckBox, QSpinBox, QTextEdit, QComboBox, QApplication, QGroupBox, QStackedWidget, QWidget, QVBoxLayout, QPushButton
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

from stat_processor import COMBAT_STATS, SURVIVAL_STATS, RESISTANCE_STATS, MAGIC_STATS, THRESHOLD_STATS, format_stats
from passive_ui import passive_widget_map


class HeroEditorDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Hero Editor")
        self.setFixedSize(1160, 650)
        self.setStyleSheet("background-color: #2F3045; color: white;")

        # 좌측 상단 - 초상화
        self.portrait_label = QLabel("portrait", self)
        self.portrait_label.setGeometry(30, 30, 200, 200)
        self.portrait_label.setStyleSheet("background-color: #1c202f;")
        self.portrait_label.setAlignment(Qt.AlignCenter)

        # 좌측 하단 - 영웅 이름
        self.name_dropdown = QComboBox(self)
        self.name_dropdown.setGeometry(30, 235, 200, 30)
        self.name_dropdown.currentIndexChanged.connect(self.hero_selected)
        self.name_dropdown.setStyleSheet("font-weight : bold; color : white; letter-spacing: 1.5px; border : 1px #1c202f; background-color: #1c202f")

        # 기본 스탯 (STR ~ WIL)
        stat_names = ["Strength", "Agility", "Perception", "Vitality", "Willpower"]
        self.stat_spinboxes = {}
        for i, name in enumerate(stat_names):
            label = QLabel(name, self)
            label.setGeometry(240, 30 + i * 40, 120, 35)
            label.setStyleSheet("font-weight : bold; color : #9B776E; letter-spacing: 1px; background-color: #1c202f;")

            spin = QSpinBox(self)
            spin.setGeometry(360, 30 + i * 40, 60, 35)
            spin.setStyleSheet("font-weight : bold; color : white; letter-spacing: 1px; border : 1px #1c202f; background-color: #1c202f")
            spin.setRange(10, 30)
            spin.setValue(10)
            spin.valueChanged.connect(self.update_ability_points)
            self.stat_spinboxes[name] = spin
            
            
        # AP
        self.ability_point = QLabel("AP", self)
        self.ability_point.setGeometry(240, 230, 150, 30)
        self.ability_point.setStyleSheet("font-weight: bold; letter-spacing: 1px;")

        # 체크박스
        self.apply_checkbox = QCheckBox("Apply stats to GearLoadout", self)
        self.apply_checkbox.setGeometry(30, 280, 260, 30)

        # 패시브 이름
        self.passive_name = QLabel("passive name", self)
        self.passive_name.setGeometry(500, 30, 600, 30)
        self.passive_name.setStyleSheet("font-weight: bold; font-size: 16px; letter-spacing: 1px; border : 1px #1c202f; background-color: #1c202f;")
        self.passive_name.setAlignment(Qt.AlignCenter)

        # 패시브 설명
        self.passive_description = QTextEdit("passive description", self)
        self.passive_description.setGeometry(500, 65, 290, 250)
        self.passive_description.setStyleSheet("letter-spacing: 1px; border : 2px #2F3045; background-color: #1c202f;")
        self.passive_description.setReadOnly(True)

        # 패시브 메뉴 자리 표시
        self.passive_stack = QStackedWidget(self)
        self.passive_stack.setGeometry(800, 65, 300, 250)
        self.passive_stack.setStyleSheet("background-color: #1c202f; border: 1px #1c202f;")
        
        # 스탯 카테고리 4개 (Combat, Survival, Resistance, Magic)
        self.stat_boxes = []
        stat_categories = ["Combat", "Survival", "Resistance", "Magic"]
        stat_colors_2 = ["#2f1c1c", "#1e2f1c", "#1c202f", "#2f1c2e"]
        for i, title in enumerate(stat_categories):
            title_label = QLabel(title, self)
            title_label.setGeometry(30 + i * 270, 330, 260, 30)
            title_label.setStyleSheet("font-size: 20px; font-weight: bold; letter-spacing: 1px; color: white; border: 2px gray; background-color: {};".format(stat_colors_2[i]))
            title_label.setAlignment(Qt.AlignCenter)
        for i in range(4):
            stat_box = QLabel(self)
            stat_box.setGeometry(30 + i * 270, 365, 260, 270)
            stat_box.setStyleSheet("background-color: #1D1A31; color : white ; letter-spacing: 0.5px; border: 2px #2F3045; font-size: 17px; padding: 5px;")
            stat_box.setAlignment(Qt.AlignTop | Qt.AlignLeft)
            stat_box.setWordWrap(True)
            stat_box.setEnabled(False)
            self.stat_boxes.append(stat_box)
        self.heroes = []
        self.load_heroes()
    
    def create_passive_widget(self, hero_name):
        widget_class = passive_widget_map.get(hero_name)
        if widget_class:
            return widget_class(self)
        else:
            return QLabel(f"{hero_name}의 패시브 메뉴 없음")
            
            
    def load_heroes(self):
        json_path = os.path.join("data", "heroes.json")
        if not os.path.exists(json_path):
            print("heroes.json not found.")
            return

        with open(json_path, encoding="utf-8") as f:
            data = json.load(f)
            self.heroes = data

        for hero in self.heroes:
            self.name_dropdown.addItem(hero["name"])
            passive_widget = self.create_passive_widget(hero["name"])
            self.passive_stack.addWidget(passive_widget)
    
    def hero_selected(self, index):
        if index < 0 or index >= len(self.heroes):
            return

        hero = self.heroes[index]

        # 패시브 정보 출력
        self.passive_name.setText(hero["passive_name"])
        self.passive_description.setText(hero["passive_description"])
        self.passive_stack.setCurrentIndex(index)

        # 초상화 이미지 표시
        portrait_path = os.path.join("assets", "portrait", hero["icon"])
        if os.path.exists(portrait_path):
            pixmap = QPixmap(portrait_path).scaled(
                self.portrait_label.width(),
                self.portrait_label.height(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.portrait_label.setPixmap(pixmap)
        else:
            self.portrait_label.setText("No Image")
        stat_map = {
            "Strength": "strength",
            "Agility": "agility",
            "Perception": "perception",
            "Vitality": "vitality",
            "Willpower": "willpower"
        }

        for label_name, json_key in stat_map.items():
            value = hero["stats"].get(json_key, 10)
            self.stat_spinboxes[label_name].setValue(value) 
            
    def update_ability_points(self):
        total = sum(spin.value() for spin in self.stat_spinboxes.values())
        remaining = 82 - total
        self.ability_point.setText(f"AP: {remaining}")
        self.update_hero_bonus_stats()

        for stat, spin in self.stat_spinboxes.items():
            current = spin.value()
            if remaining <= 0:
                spin.setMaximum(current)  # 증가 불가, 현재값까지만 허용
            else:
                spin.setMaximum(30)  # 다시 증가 허용
                    
    def update_hero_bonus_stats(self):
        stat_values = {
            "strength": self.stat_spinboxes["Strength"].value(),
            "agility": self.stat_spinboxes["Agility"].value(),
            "perception": self.stat_spinboxes["Perception"].value(),
            "vitality": self.stat_spinboxes["Vitality"].value(),
            "willpower": self.stat_spinboxes["Willpower"].value()
        }
        bonuses = self.calculate_stat_bonuses(stat_values)

        # 패시브 UI에서 보너스 가져오기
        current_widget = self.passive_stack.currentWidget()
        if hasattr(current_widget, "get_stat_bonus"):
            passive_bonus = current_widget.get_stat_bonus()
            for category in bonuses:
                for stat, value in passive_bonus.get(category, {}).items():
                    bonuses[category][stat] = bonuses[category].get(stat, 0) + value

        # UI에 적용
        for i, category in enumerate(["combat", "survival", "resistance", "magic"]):
            self.stat_boxes[i].setText(self.format_stats(bonuses.get(category, {})))

    def calculate_stat_bonuses(self, stat_values: dict) -> dict:
        STAT_TO_BONUSES = {
            "strength": {
                "block_chance": 0.015,
                "weapon_damage": 0.015,
                "bodypart_damage": 0.075,
                "crit_efficiency": 0.1,
                "armor_damage": 0.15
            },
            "agility": {
                "counter_chance": 0.015,
                "fumble_chance": -0.015,
                "backfire_chance": -0.015,
                "dodge_chance": 0.05,
                "main_hand_efficiency": 0.025,
                "move_resistance": 0.075
            },
            "perception": {
                "accuracy": 0.015,
                "armor_penetration": 0.015,
                "vision": 1,
                "bonus_range": 1,
                "crit_chance": 0.05,
                "miracle_chance": 0.05
            },
            "vitality": {
                "energy": 4,
                "energy_restoration": 0.02,
                "max_health": 15.0,
                "block_power_recovery": 0.05,
                "control_resistance": 0.075
            },
            "willpower": {
                "cooldowns_duration": -0.015,
                "skills_energy_cost": -0.015,
                "magic_power": 0.075,
                "pain_resistance": 0.075,
                "fortitude": 0.075
            }
        } 
        
        bonus_result = {"combat": {}, "survival": {}, "resistance": {}, "magic": {}}

        for stat_name, base_value in stat_values.items():
            if stat_name not in STAT_TO_BONUSES or base_value <= 10:
                continue
            
            bonuses = STAT_TO_BONUSES[stat_name]
            
            for effect, per_point_value in bonuses.items():
                if effect in THRESHOLD_STATS:
                    # 계단식 threshold 보너스 (15부터 시작)
                    if base_value >= 15:
                        steps = (base_value - 15) // 5 + 1
                        value = per_point_value * steps
                    else:
                        value = 0
                else:
                    # 일반 보정 (10부터 시작)
                    if base_value > 10:
                        effective_value = base_value - 10
                        value = per_point_value * effective_value
                    else:
                        value = 0

                if effect in COMBAT_STATS:
                    bonus_result["combat"][effect] = bonus_result["combat"].get(effect, 0) + value
                elif effect in SURVIVAL_STATS:
                    bonus_result["survival"][effect] = bonus_result["survival"].get(effect, 0) + value
                elif effect in RESISTANCE_STATS:
                    bonus_result["resistance"][effect] = bonus_result["resistance"].get(effect, 0) + value
                elif effect in MAGIC_STATS:
                    bonus_result["magic"][effect] = bonus_result["magic"].get(effect, 0) + value

        return bonus_result
    
    def get_stat_bonus_if_applied(self):
        if self.apply_checkbox.isChecked():
            stat_values = {
                "strength": self.stat_spinboxes["Strength"].value(),
                "agility": self.stat_spinboxes["Agility"].value(),
                "perception": self.stat_spinboxes["Perception"].value(),
                "vitality": self.stat_spinboxes["Vitality"].value(),
                "willpower": self.stat_spinboxes["Willpower"].value()
            }
            return self.calculate_stat_bonuses(stat_values)
        else:
            return None
    
    def format_stats(self, stat_dict: dict) -> str:
        lines = []
        for k, v in sorted(stat_dict.items()):
            label = k.replace('_', ' ').capitalize()
            if isinstance(v, float):
                sign = "+" if v > 0 else "-" if v < 0 else ""
                text = f"{sign}{abs(round(v * 100, 1))}%"
            else:
                sign = "+" if v > 0 else "-" if v < 0 else ""
                text = f"{sign}{abs(int(v))}"
            lines.append(f"{label}: {text}")
        return "\n".join(lines)

            
# 독립 실행용
if __name__ == "__main__":
    app = QApplication(sys.argv)
    dialog = HeroEditorDialog()
    dialog.show()
    sys.exit(app.exec_())