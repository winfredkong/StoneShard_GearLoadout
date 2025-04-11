import sys
import os
import json

from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QTableWidget, QTableWidgetItem,
                             QHBoxLayout, QHeaderView, QDialog, QPushButton)
from PyQt5.QtGui import QPixmap, QColor, QIcon
from PyQt5.QtCore import Qt, pyqtSignal

from stat_processor import calculate_combined_stats, calculate_bodypart_resistances, is_dual_wielding,\
                    COMBAT_STATS, SURVIVAL_STATS, RESISTANCE_STATS, MAGIC_STATS,\
                    COMBAT_SUBGROUP, SURVIVAL_SUBGROUP, RESISTANCE_SUBGROUP, MAGIC_SUBGROUP
from weapon_group_dialog import WeaponGroupDialog
from hero_editor import HeroEditorDialog



class EquipmentUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("StoneShard Gear Loadout")
        self.setFixedSize(2200, 1100)
        self.two_handed_equipped = False
        self.hero_editor_dialog = None
        self.current_hero_bonus = {"combat": {}, "survival": {}, "resistance": {}, "magic": {}}
                
        main_layout = QHBoxLayout(self)
        
        #좌측 표
        self.table = QTableWidget()
        self.table.setMinimumWidth(850)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("background-color: #2F3045; alternate-background-color: #272340; color : white; gridline-color: #1D1A31;")
        self.table.verticalHeader().setVisible(False)
        self.table.cellClicked.connect(self.item_clicked)
        main_layout.addWidget(self.table)
        
        #우측 페널
        right_panel = QWidget()
        right_panel.setFixedSize(1090, 1200)
        right_panel.setStyleSheet("background-color: #2F3045; border: 1px solid black;")
        self.slot_area = right_panel
        self.slot_labels = {}
        self.combined_stats = {"combat": {}, "survival": {}, "resistance": {}, "magic": {}}
        self.setup_slots()
        
        # 부위별 저항력 슬롯
        self.resistance_boxes = []
        self.resistance_labels = {}
        body_parts = ["Head", "Torso", "Hand", "Leg"]
        for i, part in enumerate(body_parts):
            label = QLabel(part, self.slot_area)
            label.setGeometry(800, i*130, 280, 20)
            label.setStyleSheet("font-size: 16px; font-weight: bold; color: white; border: 2px gray; background-color: #1c202f;")
            label.setAlignment(Qt.AlignCenter)
            self.resistance_labels[part] = label
        for i in range(4):            
            resistance_box = QLabel(self.slot_area)
            resistance_box.setGeometry(800, 25 + i*130, 280, 100)
            resistance_box.setStyleSheet("background-color: #1D1A31; color : white ; border: 2px #2F3045; font-size: 16px; padding: 2px;")
            resistance_box.setAlignment(Qt.AlignTop | Qt.AlignLeft)
            resistance_box.setWordWrap(True)
            resistance_box.setEnabled(False)
            self.resistance_boxes.append(resistance_box)
            
        # 영웅 선택및 스탯 출력 버튼 생성
        self.hero_button = QPushButton("Edit\nCharacter", right_panel)
        self.hero_button.setGeometry(96, 440, 140, 64)
        self.hero_button.setStyleSheet("font-size: 16px; font-weight: bold; letter-spacing : 1px; background-color: #1D1A31; color: white;")
        self.hero_button.clicked.connect(self.open_hero_editor)
        
        #선택한 영웅 초상화 출력
        self.hero_portrait_label = QLabel(right_panel)
        self.hero_portrait_label.setGeometry(24, 440, 64, 64)
        self.hero_portrait_label.setStyleSheet("background-color: #1D1A31;")
        self.hero_portrait_label.setAlignment(Qt.AlignCenter)

        # 상태 오버레이
        self.hero_status_overlay = QLabel(self.hero_portrait_label)
        self.hero_status_overlay.setGeometry(0, 0, 20, 20)
        self.hero_status_overlay.setStyleSheet("font-weight: bold; font-size: 14px; color: lime; background-color: #1D1A31;")
        self.hero_status_overlay.setAlignment(Qt.AlignCenter)
        self.hero_status_overlay.hide()
        
        # 총 장비의 가격을 출력하기위한 레이블 생성
        self.total_cost_label = QLabel("Total Cost: 0", right_panel)
        self.total_cost_label.setGeometry(30, 380, 300, 40)
        self.total_cost_label.setStyleSheet("font-weight:bold; font-size: 20px; letter-spacing : 1px; color: white; border: 1px #2F3045;")
        
        # 스탯 출력을 위한 텍스트 전용 슬롯 4개 생성
        self.stat_boxes = []
        stat_titles = ["Combat", "Survival", "Resistance", "Magic"]
        stat_colors = ["#2f1c1c", "#1e2f1c", "#1c202f", "#2f1c2e"]
        for i, title in enumerate(stat_titles):
            title_label = QLabel(title, self.slot_area)
            title_label.setGeometry(10 + i * 270, 520, 260, 30)
            title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: white; border: 2px gray; background-color: {};".format(stat_colors[i]))
            title_label.setAlignment(Qt.AlignCenter)
        for i in range(4):
            stat_box = QLabel(self.slot_area)
            stat_box.setGeometry(10 + i * 270, 554, 260, 500)
            stat_box.setStyleSheet("background-color: #1D1A31; color : white ; border: 2px #2F3045; font-size: 18px; padding: 5px;")
            stat_box.setAlignment(Qt.AlignTop | Qt.AlignLeft)
            stat_box.setWordWrap(True)
            stat_box.setEnabled(False)
            self.stat_boxes.append(stat_box)      
        
        main_layout.addWidget(right_panel)

        self.column_config = {
            "weapon": ["Tier", "Icon", "Item", "Rarity", "Damage", "Durability", "Price", "Properties"],
            "armor": ["Tier", "Icon", "Item", "Rarity", "Class", "Protection", "Durability", "Price", "Properties"],
            "normal": ["Tier", "Icon", "Item", "Rarity", "Durability", "Price", "Properties"]
        }

        self.column_widths = {
            "Tier": 60,
            "Icon": 100,
            "Item": 130,
            "Rarity": 95,
            "Damage": 120,
            "Class": 90,
            "Protection": 110,
            "Durability": 95,
            "Price": 80,
            "Properties": 260,
        }

        self.last_clicked_slot = None
        self.loaded_items = []
        self.current_icon_folder = ""
        self.two_handed_equipped = False
           
    def update_total_cost(self):
        total = 0
        for label in self.slot_labels.values():
            item = getattr(label, "equipped_item", None)
            if item and "price" in item:
                total += item["price"]
        self.total_cost_label.setText(f"Total Cost: {total}")
        
        
    def sort_table_by_column(self, column_index):
        current_order = self.table.horizontalHeader().sortIndicatorOrder()
        self.table.sortItems(column_index, current_order)
    
    
    def setup_slots(self):
        self.slots = {
            "Main-Hand": (50, 20, 128, 334),
            "Chestpiece": (200, 20, 128, 192),
            "Cloak": (350, 20, 132, 192),
            "Headgear": (500, 20, 128, 128),
            "Belt": (500, 152, 128, 64),
            "Off-Hand": (650, 20, 128, 334),
            "Glove": (200, 220, 128, 132),
            "Ring 1": (350, 220, 64, 64),
            "Ring 2": (350, 288, 64, 64),
            "Amulet": (418, 220, 64, 132),
            "Boot": (500, 220, 128, 132),
        }
        for name, (x, y, w, h) in self.slots.items():
            label = ClickableLabel(name, self.slot_area)
            label.setGeometry(x, y, w, h)
            label.setStyleSheet("border: 3px #454766; background-color:#1D1A31; color: lightgray; font-size: 16px; font-weight: bold;")
            label.setAlignment(Qt.AlignCenter)
            label.clicked.connect(self.slot_clicked)
            label.rightClicked.connect(self.clear_slot)
            self.slot_labels[name] = label
    
    def update_stat_boxes(self):
        self.stat_boxes[0].setText(self.format_stats(self.combined_stats["combat"], "combat"))
        self.stat_boxes[1].setText(self.format_stats(self.combined_stats["survival"], "survival"))
        self.stat_boxes[2].setText(self.format_stats(self.combined_stats["resistance"], "resistance"))
        self.stat_boxes[3].setText(self.format_stats(self.combined_stats["magic"], "magic"))
    
    def update_resistance_boxes(self):
        self.resistance_boxes[0].setText(self.format_stats_simple(calculate_bodypart_resistances(self.slot_labels)["head"]))
        self.resistance_boxes[1].setText(self.format_stats_simple(calculate_bodypart_resistances(self.slot_labels)["torso"]))
        self.resistance_boxes[2].setText(self.format_stats_simple(calculate_bodypart_resistances(self.slot_labels)["hand"]))
        self.resistance_boxes[3].setText(self.format_stats_simple(calculate_bodypart_resistances(self.slot_labels)["leg"]))
        

    def slot_clicked(self, slot_name):
        
        self.last_clicked_slot = slot_name

        if slot_name in ["Main-Hand", "Off-Hand"]:
            dialog = WeaponGroupDialog(self)
            if dialog.exec_() == QDialog.Accepted:
                selected_group = dialog.selected_group()
                filename = f"{selected_group}.json"
            else:
                return
        else:
            json_map = {
                "Chestpiece": "chestpiece.json",
                "Cloak": "cloak.json",
                "Headgear": "headgear.json",
                "Belt": "belt.json",
                "Glove": "glove.json",
                "Boot": "boots.json",
                "Ring 1": "ring.json",
                "Ring 2": "ring.json",
                "Amulet": "amulet.json",
            }
            filename = json_map.get(slot_name)
            if not filename:
                return

        path = os.path.join("data", filename)
        if not os.path.exists(path):
            print(f"File not found: {path}")
            return
        with open(path, encoding='utf-8') as f:
            items = json.load(f)
            tier_order = {
            "Tier 1": 1,
            "Tier 2": 2,
            "Tier 3": 3,
            "Tier 4": 4,
            "Tier 5": 5
            }
            items.sort(key=lambda x: tier_order.get(x.get("tier", ""), 99))

        if not items:
            return

        self.loaded_items = items
        item_type = items[0].get("type", "normal")
        columns = self.column_config.get(item_type, self.column_config["normal"])

        self.table.setColumnCount(len(columns))
        self.table.setHorizontalHeaderLabels(columns)
        self.table.setRowCount(0)
        self.table.horizontalHeader().sectionClicked.connect(self.sort_table_by_column)
        header = self.table.horizontalHeader()
        header.setStyleSheet("QHeaderView::section { background-color: #1D1A31; color: white; font-weight: bold; border: 3px #2F3045; }")

        folder_name = os.path.splitext(filename)[0]
        self.current_icon_folder = folder_name

        for idx, col_name in enumerate(columns):
            self.table.setColumnWidth(idx, self.column_widths.get(col_name, 80))

        for row, item in enumerate(items):
            self.table.insertRow(row)

            row_height = max(100, 20 * (4 + len(item.get("stats", {}))))
            self.table.setRowHeight(row, row_height)

            for col, name in enumerate(columns):
                if name == "Tier":
                    value = item.get("tier", "?")
                    cell_item = QTableWidgetItem(value)
                    cell_item.setTextAlignment(Qt.AlignCenter)
                    self.table.setItem(row, col, cell_item)
                elif name == "Item":
                    value = item.get("name", "")
                    cell_item = QTableWidgetItem(value)
                    if name in ["Item", "Rarity"] and item.get("rarity") == "Unique":
                        cell_item.setForeground(QColor("#A020F0"))
                    self.table.setItem(row, col, cell_item)
                elif name == "Rarity":
                    value = item.get("rarity", "-")
                    cell_item = QTableWidgetItem(value)
                    cell_item.setTextAlignment(Qt.AlignCenter)
                    if name in ["Item", "Rarity"] and item.get("rarity") == "Unique":
                        cell_item.setForeground(QColor("#A020F0"))
                    self.table.setItem(row, col, cell_item)
                elif name == "Class":
                    value = item.get("class", "-")
                    cell_item = QTableWidgetItem(value)
                    cell_item.setTextAlignment(Qt.AlignCenter)
                    self.table.setItem(row, col, cell_item)
                elif name == "Protection":
                    value = str(item.get("protection", "-"))
                    cell_item = QTableWidgetItem(value)
                    cell_item.setTextAlignment(Qt.AlignCenter)
                    self.table.setItem(row, col, cell_item)
                elif name == "Durability":
                    value = str(item.get("durability", "-"))
                    cell_item = QTableWidgetItem(value)
                    cell_item.setTextAlignment(Qt.AlignCenter)
                    self.table.setItem(row, col, cell_item)
                elif name == "Price":
                    value = str(item.get("price", "-"))
                    cell_item = QTableWidgetItem(value)
                    cell_item.setTextAlignment(Qt.AlignCenter)
                    self.table.setItem(row, col, cell_item)
                elif name == "Damage":
                    value = self.extract_damage(item)
                    cell_item = QTableWidgetItem(value)
                    self.table.setItem(row, col, cell_item)
                elif name == "Properties":
                    value = self.format_stats_simple(item.get("stats", {}))
                    cell_item = QTableWidgetItem(value)
                    self.table.setItem(row, col, cell_item)
                elif name == "Icon":
                    icon_path = os.path.join("assets", folder_name, item.get("icon", ""))                    
                    if os.path.exists(icon_path):
                        label = QLabel()
                        pixmap = QPixmap(icon_path).scaled(96, 96, Qt.KeepAspectRatio, Qt.FastTransformation)
                        label.setPixmap(pixmap)
                        label.setAlignment(Qt.AlignCenter)
                        if row % 2 == 1:
                            label.setStyleSheet("background-color: #272340;")
                        else:
                            label.setStyleSheet("background-color: #2F3045;")
                        self.table.setCellWidget(row, col, label)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)


    def item_clicked(self, row, column):
        item = self.loaded_items[row]
        icon_file = item.get("icon")
            
        if not icon_file:
            return

        icon_path = os.path.join("assets", self.current_icon_folder, icon_file)
        if not os.path.exists(icon_path):
            return

        is_two_handed = item.get("handed") == "Two-Handed" or item.get("block_off_hand", False)

        if self.last_clicked_slot in ["Main-Hand", "Off-Hand"] and is_two_handed:
            # 해제
            self.clear_slot("Main-Hand")
            self.clear_slot("Off-Hand")

            # Main-Hand에 장착
            label = self.slot_labels.get("Main-Hand")
            if label:
                pixmap = QPixmap(icon_path).scaled(label.width(), label.height(), Qt.KeepAspectRatio, Qt.FastTransformation)
                label.setPixmap(pixmap)
                # Remove old overlays
                for child in label.findChildren(QLabel):
                    if child != label:
                        child.deleteLater()
            # Tier 오버레이
            tier = item.get("tier", "")
            tier_map = {
                "Tier 1": ("T1", "white"),
                "Tier 2": ("T2", "#B6FF9C"),
                "Tier 3": ("T3", "#66B2FF"),
                "Tier 4": ("T4", "#DA70D6"),
                "Tier 5": ("T5", "#FF7F7F") 
            }
            if tier in tier_map:
                tier_text, tier_color = tier_map[tier]
                tier_overlay = QLabel(tier_text, label)
                tier_overlay.setGeometry(4, 4, 24, 24)
                tier_overlay.setStyleSheet(
                    f"color: {tier_color}; font-weight: bold; background-color: rgba(0,0,0,160); "
                    "font-size: 12px; border-radius: 4px;"
                )
                tier_overlay.setAlignment(Qt.AlignCenter)
                tier_overlay.show()
            
            label.equipped_item = item
            self.combined_stats = calculate_combined_stats(self.slot_labels)
            self.recalculate_stats_with_hero_bonus()
            self.update_resistance_boxes()
            
            if item.get("type") == "weapon":
                damage_dict = item.get("damage", {})
                total_damage = sum(damage_dict.values())                   
                dual = is_dual_wielding(self.slot_labels)
                factor = 1.0
                if self.last_clicked_slot == "Main-Hand" and dual:
                    factor = 0.75
                elif self.last_clicked_slot == "Off-Hand" and dual:
                    factor = 0.5

                damage_dict = item.get("damage", {})
                total_damage = sum(v * factor for v in damage_dict.values())

                damage_overlay = QLabel(f"Damage : {total_damage:.0f}", label)
                damage_overlay.setGeometry(16, label.height() - 28, 96, 24)
                damage_overlay.setStyleSheet(
                    "color: lightgray; font-weight: bold; background-color: rgba(0,0,0,180); "
                    "font-size: 12px; border-radius: 4px;"
                )
                damage_overlay.setAlignment(Qt.AlignCenter)
                damage_overlay.show()


            if item.get("type") == "armor":
                armor_class = item.get("class", "").lower()
                class_letter = {"light": "L", "medium": "M", "heavy": "H"}.get(armor_class, "")
                if class_letter:
                    class_overlay = QLabel(class_letter, label)
                    class_overlay.setGeometry(4, 4, 24, 24)
                    class_overlay.setStyleSheet("color: white; font-weight: bold; background-color: rgba(0,0,0,128); font-size: 12px; border-radius: 4px;")
                    class_overlay.setAlignment(Qt.AlignCenter)
                    class_overlay.show()

                protection = item.get("protection", None)
                if protection is not None:
                    prot_overlay = QLabel(f"{protection:.0f}", label)
                    prot_overlay.setGeometry(label.width() - 28, 4, 24, 24)
                    prot_overlay.setStyleSheet("color: lightgreen; font-weight: bold; background-color: rgba(0,0,0,128); font-size: 12px; border-radius: 4px;")
                    prot_overlay.setAlignment(Qt.AlignCenter)
                    prot_overlay.show()

                label.equipped_item = item
                self.combined_stats = calculate_combined_stats(self.slot_labels)
                self.recalculate_stats_with_hero_bonus()
                self.update_resistance_boxes()
                label.setScaledContents(False)
                label.setAlignment(Qt.AlignCenter)

            # Off-hand 잠금
            self.slot_labels["Off-Hand"].setText("LOCKED")
            self.slot_labels["Off-Hand"].setEnabled(False)
            self.two_handed_equipped = True
            return

        if self.last_clicked_slot is None:
            print("No slot selected")
            return

        item = self.loaded_items[row]
        icon_file = item.get("icon")
        if not icon_file:
            return

        label = self.slot_labels.get(self.last_clicked_slot)
        if label:
            pixmap = QPixmap(icon_path).scaled(label.width(), label.height(), Qt.KeepAspectRatio, Qt.FastTransformation)
            label.setPixmap(pixmap)
            # Remove old overlays
            for child in label.findChildren(QLabel):
                if child != label:
                    child.deleteLater()
            # Tier 오버레이
            tier = item.get("tier", "")
            tier_map = {
                "Tier 1": ("T1", "white"),
                "Tier 2": ("T2", "#B6FF9C"),
                "Tier 3": ("T3", "#66B2FF"),
                "Tier 4": ("T4", "#DA70D6"),
                "Tier 5": ("T5", "#FF7F7F") 
            }
            if tier in tier_map:
                tier_text, tier_color = tier_map[tier]
                tier_overlay = QLabel(tier_text, label)
                tier_overlay.setGeometry(4, 4, 24, 24)
                tier_overlay.setStyleSheet(
                    f"color: {tier_color}; font-weight: bold; background-color: rgba(0,0,0,160); "
                    "font-size: 12px; border-radius: 4px;"
                )
                tier_overlay.setAlignment(Qt.AlignCenter)
                tier_overlay.show()
                
            if item.get("type") == "weapon":
                damage_dict = item.get("damage", {})
                total_damage = sum(damage_dict.values())

                dual = is_dual_wielding(self.slot_labels)
                factor = 1.0
                if self.last_clicked_slot == "Main-Hand" and dual:
                    factor = 0.75
                elif self.last_clicked_slot == "Off-Hand" and dual:
                    factor = 0.5

                damage_dict = item.get("damage", {})
                total_damage = sum(v * factor for v in damage_dict.values())

                damage_overlay = QLabel(f"Damage : {total_damage:.0f}", label)
                damage_overlay.setGeometry(16, label.height() - 28, 96, 24)
                damage_overlay.setStyleSheet(
                    "color: lightgray; font-weight: bold; background-color: rgba(0,0,0,180); "
                    "font-size: 12px; border-radius: 4px;"
                )
                damage_overlay.setAlignment(Qt.AlignCenter)
                damage_overlay.show()


            if item.get("type") == "armor":
                armor_class = item.get("class", "").lower()
                class_letter = {"light": "L", "medium": "M", "heavy": "H"}.get(armor_class, "")
                if class_letter:
                    class_overlay = QLabel(class_letter, label)
                    class_overlay.setGeometry(4, label.height()-28, 24, 24)

                    bg_color = {
                        "L": "limegreen",
                        "M": "blue",
                        "H": "red"
                    }.get(class_letter, "gray")

                    class_overlay.setStyleSheet(
                        f"color: white; font-weight: bold; background-color: {bg_color}; "
                        "font-size: 12px; border-radius: 4px;"
                    )
                    class_overlay.setAlignment(Qt.AlignCenter)
                    class_overlay.show()

            protection = item.get("protection", None)
            if protection is not None:
                prot_overlay = QLabel(f"{protection:.0f}", label)
                prot_overlay.setGeometry(label.width() - 28, label.height()-28, 24, 24)

                # Protection 색상 계산 (0~20)
                p = min(max(float(protection), 0), 20)
                red = int((p / 20) * 105+150)
                green = int((1 - p / 20) * 105+150)
                color = f"rgb({red},{green},0)"

                prot_overlay.setStyleSheet(
                    f"color: {color}; font-weight: bold; background-color: rgba(0,0,0,188); "
                    "font-size: 12px; border-radius: 4px;"
                )
                prot_overlay.setAlignment(Qt.AlignCenter)
                prot_overlay.show()


            label.equipped_item = item
            self.combined_stats = calculate_combined_stats(self.slot_labels)
            self.recalculate_stats_with_hero_bonus()
            self.update_resistance_boxes()
            label.setScaledContents(False)
            label.setAlignment(Qt.AlignCenter)
            self.update_total_cost()
        
        if self.last_clicked_slot == "Main-Hand" and not is_two_handed and self.two_handed_equipped:
            self.slot_labels["Off-Hand"].setEnabled(True)
            self.slot_labels["Off-Hand"].setText("Off-Hand")
            self.two_handed_equipped = False
            


    def clear_slot(self, slot_name):
        if slot_name == "Main-Hand" and self.two_handed_equipped:
            self.slot_labels["Off-Hand"].setEnabled(True)
            self.slot_labels["Off-Hand"].setText("Off-Hand")
            self.two_handed_equipped = False

        label = self.slot_labels.get(slot_name)
        if label:
            label.clear()
            for child in label.findChildren(QLabel):
                if child != label:
                    child.deleteLater()
            label.setText(slot_name)
            label.equipped_item = None
            self.combined_stats = calculate_combined_stats(self.slot_labels)
            self.recalculate_stats_with_hero_bonus()
            self.update_resistance_boxes()
            label.setStyleSheet("border: 3px #454766; background-color:#1D1A31; color: lightgray; font-size: 16px; font-weight: bold;")
            label.setAlignment(Qt.AlignCenter)
            self.update_total_cost()
            self.update_damage_overlays()
            
    def apply_hero_bonus_to_ui(self, bonus):
        self.current_hero_bonus = bonus or {"combat": {}, "survival": {}, "resistance": {}, "magic": {}}
        self.recalculate_stats_with_hero_bonus()

        # 스탯 적용 여부 표시
        applied = any(bool(v) for v in bonus.values())
        if applied:
            self.hero_status_overlay.setText("✓")
            self.hero_status_overlay.setStyleSheet("color: lime; background-color: rgba(0,0,0,150); border-radius: 4px; font-weight: bold; font-size: 14px;")
        else:
            self.hero_status_overlay.setText("✕")
            self.hero_status_overlay.setStyleSheet("color: red; background-color: rgba(0,0,0,150); border-radius: 4px; font-weight: bold; font-size: 14px;")
        self.hero_status_overlay.show()

        # 포트레이트 업데이트
        if self.hero_editor_dialog:
            icon_path = self.hero_editor_dialog.get_current_hero_icon()
            if icon_path and os.path.exists(icon_path):
                pixmap = QPixmap(icon_path).scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.hero_portrait_label.setPixmap(pixmap)
            else:
                self.hero_portrait_label.setText("?")
            

    def extract_damage(self, item):
        damage = item.get("damage", {})
        return "\n".join(f"{k.replace('_damage', '').capitalize()}: {v}" for k, v in damage.items())
    
    
    def update_damage_overlays(self):
        from stat_processor import is_dual_wielding

        dual = is_dual_wielding(self.slot_labels)

        for slot_name in ["Main-Hand", "Off-Hand"]:
            label = self.slot_labels.get(slot_name)
            if not label:
                continue

            item = getattr(label, "equipped_item", None)
            if not item or item.get("type") != "weapon":
                continue

            # Two-Handed 무기는 Off-Hand에서 제외
            if item.get("handed") == "Two-Handed" and slot_name == "Off-Hand":
                continue

            # 기존 Damage overlay만 제거
            for child in label.findChildren(QLabel):
                if child.objectName() == "damage_overlay":
                    child.deleteLater()

            # 배율 설정
            factor = 1.0
            if slot_name == "Main-Hand" and dual:
                factor = 0.75
            elif slot_name == "Off-Hand" and dual:
                factor = 0.5

            damage_dict = item.get("damage", {})
            total_damage = sum(v * factor for v in damage_dict.values())

            damage_overlay = QLabel(f"Damage : {total_damage:.0f}", label)
            damage_overlay.setObjectName("damage_overlay")
            damage_overlay.setGeometry(16, label.height() - 28, 96, 24)
            damage_overlay.setStyleSheet(
                "color: lightgray; font-weight: bold; background-color: rgba(0,0,0,180); "
                "font-size: 12px; border-radius: 4px;"
            )
            damage_overlay.setAlignment(Qt.AlignCenter)
            damage_overlay.show()
    

    def open_hero_editor(self):
        if self.hero_editor_dialog is None:
            self.hero_editor_dialog = HeroEditorDialog(self)
            self.hero_editor_dialog.stat_bonus_updated.connect(self.apply_hero_bonus_to_ui)

        self.hero_editor_dialog.exec_()

    def format_stats(self, stats, category=None):
        lines = []

        if category == "combat":
            for subgroup in COMBAT_SUBGROUP:
                for key in subgroup:
                    if key in stats:
                        lines.append(self.format_stat_line(key, stats[key]))
                lines.append("")
        elif category == "survival":
            for subgroup in SURVIVAL_SUBGROUP:
                for key in subgroup:
                    if key in stats:
                        lines.append(self.format_stat_line(key, stats[key]))
                lines.append("")
        elif category == "resistance":
            for subgroup in RESISTANCE_SUBGROUP:
                for key in subgroup:
                    if key in stats:
                        lines.append(self.format_stat_line(key, stats[key]))
                lines.append("")
        elif category == "magic":
            for subgroup in MAGIC_SUBGROUP:
                for key in subgroup:
                    if key in stats:
                        lines.append(self.format_stat_line(key, stats[key]))
                lines.append("")

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
    
    def format_stats_simple(self, stats):
        lines = []
        DISPLAY_WIDTH = 28

        for key, value in stats.items():
            if any(key.endswith(suffix) for suffix in ("_torso", "_head", "_hand", "_leg")):
                label = key.rsplit('_', 1)[0].replace('_', ' ').capitalize() + " *"
            else:
                label = key.replace('_', ' ').capitalize()

            sign = "+" if value > 0 else "-" if value < 0 else ""

            if isinstance(value, float) and not value.is_integer():
                formatted = f"{sign}{abs(round(value * 100, 1))}%"
            else:
                formatted = f"{sign}{int(abs(value))}"

            padding = DISPLAY_WIDTH - len(label) - 2
            line = f"{label} :".ljust(DISPLAY_WIDTH - len(formatted)) + formatted
            lines.append(line)

        return "\n".join(lines)
    
    def recalculate_stats_with_hero_bonus(self):
        # stat_processor에서 가져온 계산 함수 사용
        from stat_processor import calculate_combined_stats

        combined = calculate_combined_stats(self.slot_labels)

        # 영웅 보너스 반영
        for category in combined:
            for stat, value in self.current_hero_bonus.get(category, {}).items():
                combined[category][stat] = combined[category].get(stat, 0) + value

        self.combined_stats = combined
        self.update_stat_boxes()
        self.update_damage_overlays()
    



class ClickableLabel(QLabel):
    clicked = pyqtSignal(str)
    rightClicked = pyqtSignal(str)

    def __init__(self, slot_name, parent=None):
        super().__init__(slot_name, parent)
        self.slot_name = slot_name

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.slot_name)
        elif event.button() == Qt.RightButton:
            self.rightClicked.emit(self.slot_name)
    
    
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("assets/icon/icon.ico"))
    window = EquipmentUI()
    window.show()
    sys.exit(app.exec_())
    


