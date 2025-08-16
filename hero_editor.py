import json
import os
import sys

from PyQt5.QtWidgets import (
    QDialog, QLabel, QCheckBox, QSpinBox, QTextEdit, QComboBox, QApplication, QGroupBox, QStackedWidget, QWidget, QVBoxLayout, QPushButton
)
from PyQt5.QtGui import QPixmap, QSyntaxHighlighter, QTextCharFormat, QColor
from PyQt5.QtCore import Qt, pyqtSignal, QRegularExpression

from stat_processor import COMBAT_STATS, SURVIVAL_STATS, RESISTANCE_STATS, MAGIC_STATS, THRESHOLD_STATS, format_stats
from passive_ui import passive_widget_map

KEYWORD_COLORS = {
    "trophy": "#FFD700",
    "trophies": "#FFD700",
    "bone charm": "#FFD700",
    "Boss": "#FFD700",
    "Mini-Boss": "#FFD700",
    "treatise": "#FFD700",
    "treatises": "#FFD700",
    "Den or Hunting Ground": "#FFD700",
    "location visited": "#FFD700",
    "Butchering": "#B5E61D",
    "Heroism": "#B5E61D",
    "Optimism": "#B5E61D",
    "Second Wind": "#B5E61D",
    "Make a Halt": "#B5E61D",
    "Survival": "#B5E61D",
    "Vigor": "#B5E61D",
    "Weaponry trees": "#FFD700",
    "Sorcery trees": "#FFD700",
    "Utility trees": "#FFD700"
}

class PassiveHighlighter(QSyntaxHighlighter):
    def __init__(self, doc, token_colors: dict):
        super().__init__(doc)
        self.rules = []
        for word, hexcolor in token_colors.items():
            fmt = QTextCharFormat()
            fmt.setForeground(QColor(hexcolor))
            rx = QRegularExpression(rf"\b{QRegularExpression.escape(word)}\b")
            rx.setPatternOptions(QRegularExpression.CaseInsensitiveOption)
            self.rules.append((rx, fmt))

    def highlightBlock(self, text: str):
        for rx, fmt in self.rules:
            it = rx.globalMatch(text)
            while it.hasNext():
                m = it.next()
                self.setFormat(m.capturedStart(), m.capturedLength(), fmt)


class HeroEditorDialog(QDialog):
    stat_bonus_updated = pyqtSignal(dict)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Hero Editor")
        self.setFixedSize(1300, 850)
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
            spin.valueChanged.connect(self.update_stat_points)
            self.stat_spinboxes[name] = spin
            
        # SP 제한 해제 체크박스
        self.SP_checkbox = QCheckBox("Enable SP limit", self)
        self.SP_checkbox.setGeometry(240, 270, 180, 30) 
        self.SP_checkbox.setStyleSheet("color : white;")   
        
        # AP
        self.stat_point = QLabel("SP : ", self)
        self.stat_point.setGeometry(240, 235, 90, 30)
        self.stat_point.setStyleSheet("font-weight: bold; letter-spacing: 1px;")
        
        # 체크박스
        self.apply_checkbox = QCheckBox("Apply stats to GearLoadout", self)
        self.apply_checkbox.setGeometry(30, 340, 330, 50)
        self.apply_checkbox.setStyleSheet("font-size: 18px; font-weight: bold; letter-spacing: 1px;")
        self.apply_checkbox.stateChanged.connect(self.update_hero_bonus_stats)
        
        # 패시브 이름
        self.passive_name = QLabel("passive name", self)
        self.passive_name.setGeometry(450, 30, 800, 30)
        self.passive_name.setStyleSheet("font-weight: bold; font-size: 16px; letter-spacing: 1px; border : 1px #1c202f; background-color: #1c202f;")
        self.passive_name.setAlignment(Qt.AlignCenter)

        # 패시브 설명
        self.passive_description = QTextEdit("passive description", self)
        self.passive_description.setGeometry(450, 65, 390, 300)
        self.passive_description.setStyleSheet("letter-spacing: 1px; border : 2px #2F3045; background-color: #1c202f;")
        self.passive_description.setReadOnly(True)

        # 패시브 메뉴 자리 표시
        self.passive_stack = QStackedWidget(self)
        self.passive_stack.setGeometry(850, 65, 400, 300)
        self.passive_stack.setStyleSheet("background-color: #1c202f; border: 1px #1c202f;")

        
        # 스탯 카테고리 4개 (Combat, Survival, Resistance, Magic)
        self.stat_boxes = []
        stat_categories = ["Combat", "Survival", "Resistance", "Magic"]
        stat_colors_2 = ["#2f1c1c", "#1e2f1c", "#1c202f", "#2f1c2e"]
        for i, title in enumerate(stat_categories):
            title_label = QLabel(title, self)
            title_label.setGeometry(30 + i * 310, 400, 300, 30)
            title_label.setStyleSheet("font-size: 20px; font-weight: bold; letter-spacing: 1px; color: white; border: 2px gray; background-color: {};".format(stat_colors_2[i]))
            title_label.setAlignment(Qt.AlignCenter)
        for i in range(4):
            stat_box = QLabel(self)
            stat_box.setGeometry(30 + i * 310, 435, 300, 400)
            stat_box.setStyleSheet("background-color: #1D1A31; color : white ; letter-spacing: 0.5px; border: 2px #2F3045; font-size: 18px; padding: 5px;")
            stat_box.setAlignment(Qt.AlignTop | Qt.AlignLeft)
            stat_box.setWordWrap(True)
            stat_box.setEnabled(False)
            self.stat_boxes.append(stat_box)
        self.heroes = []
        self.load_heroes()
    
    def create_passive_widget(self, hero_name):
        widget_class = passive_widget_map.get(hero_name)
        if widget_class:
            widget = widget_class(self)
            widget.stat_bonus_changed.connect(self.update_hero_bonus_stats)
            widget.stat_bonus_changed.connect(self.update_stat_points)
            return widget
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
        
        #패시브 정보 컬러링
        self.passive_highlighter = PassiveHighlighter(self.passive_description.document(), KEYWORD_COLORS)

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
            
    def update_stat_points(self):
        total = sum(spin.value() for spin in self.stat_spinboxes.values())

        current_widget = self.passive_stack.currentWidget()
        passive_sp = 0
        if hasattr(current_widget, "get_bonus_points"):
            passive_sp = current_widget.get_bonus_points().get("ap", 0)

        max_sp = 0
        if self.SP_checkbox.isChecked():
            max_sp = 999
        else:
            max_sp = 82 + passive_sp
        remaining = max_sp - total

        if self.SP_checkbox.isChecked():
            self.stat_point.setText("SP : -")
        else:
            self.stat_point.setText(f"SP : {remaining}")

        for stat, spin in self.stat_spinboxes.items():
            current = spin.value()          
            if remaining <= 0:
                spin.setMaximum(current)
            else:
                spin.setMaximum(30)
        self.update_hero_bonus_stats()
                    
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

        for i, category in enumerate(["combat", "survival", "resistance", "magic"]):
            self.stat_boxes[i].setText(self.format_stats(bonuses.get(category, {})))

        # ✅ 체크박스에 따라 영웅 스탯 반영 여부 결정
        if self.apply_checkbox.isChecked():
            self.stat_bonus_updated.emit(bonuses)
        else:
            self.stat_bonus_updated.emit({"combat": {}, "survival": {}, "resistance": {}, "magic": {}})

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
    
    def format_stats(self, stat_dict: dict, category: str = None) -> str:
        from stat_processor import COMBAT_SUBGROUP, SURVIVAL_SUBGROUP, RESISTANCE_SUBGROUP, MAGIC_SUBGROUP
        lines = []

        if category == "combat":
            for subgroup in COMBAT_SUBGROUP:
                for key in subgroup:
                    if key in stat_dict:
                        lines.append(self.format_stat_line(key, stat_dict[key]))
                lines.append("")
        elif category == "survival":
            for subgroup in SURVIVAL_SUBGROUP:
                for key in subgroup:
                    if key in stat_dict:
                        lines.append(self.format_stat_line(key, stat_dict[key]))
                lines.append("")
        elif category == "resistance":
            for subgroup in RESISTANCE_SUBGROUP:
                for key in subgroup:
                    if key in stat_dict:
                        lines.append(self.format_stat_line(key, stat_dict[key]))
                lines.append("")
        elif category == "magic":
            for subgroup in MAGIC_SUBGROUP:
                for key in subgroup:
                    if key in stat_dict:
                        lines.append(self.format_stat_line(key, stat_dict[key]))
                lines.append("")
        else:
            for k, v in sorted(stat_dict.items()):
                lines.append(self.format_stat_line(k, v))

        return "\n".join(lines).strip()

    def format_stat_line(self, key, value):
        display_name = key.replace('_', ' ').capitalize()

        if any(key.endswith(suffix) for suffix in ("_head", "_torso", "_hand", "_leg")):
            display_name = display_name.rsplit(' ', 1)[0] + " *"

        if isinstance(value, float):
            if abs(value) < 1:
                formatted = f"{'+' if value >= 0 else ''}{round(value * 100)}%"
            else:
                formatted = f"{'+' if value >= 0 else ''}{round(value)}"
        else:
            formatted = f"{'+' if value >= 0 else ''}{value}"

        return f"{display_name} : {formatted}"

    def update_hero_bonus_stats(self):
        stat_values = {
            "strength": self.stat_spinboxes["Strength"].value(),
            "agility": self.stat_spinboxes["Agility"].value(),
            "perception": self.stat_spinboxes["Perception"].value(),
            "vitality": self.stat_spinboxes["Vitality"].value(),
            "willpower": self.stat_spinboxes["Willpower"].value()
        }
        bonuses = self.calculate_stat_bonuses(stat_values)

        current_widget = self.passive_stack.currentWidget()
        if hasattr(current_widget, "get_stat_bonus"):
            passive_bonus = current_widget.get_stat_bonus()
            for category in bonuses:
                for stat, value in passive_bonus.get(category, {}).items():
                    bonuses[category][stat] = bonuses[category].get(stat, 0) + value

        for i, category in enumerate(["combat", "survival", "resistance", "magic"]):
            self.stat_boxes[i].setText(self.format_stats(bonuses.get(category, {}), category))

        if self.apply_checkbox.isChecked():
            self.stat_bonus_updated.emit(bonuses)
        else:
            self.stat_bonus_updated.emit({"combat": {}, "survival": {}, "resistance": {}, "magic": {}})
    
    def get_current_hero_icon(self):
        index = self.name_dropdown.currentIndex()
        if index < 0 or index >= len(self.heroes):
            return None
        hero = self.heroes[index]
        return os.path.join("assets", "portrait", hero["icon"])
    
    

            
# 독립 실행용
if __name__ == "__main__":
    app = QApplication(sys.argv)
    dialog = HeroEditorDialog()
    dialog.show()
    sys.exit(app.exec_())