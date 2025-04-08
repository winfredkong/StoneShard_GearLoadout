from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSpinBox, QCheckBox, QPushButton, QComboBox, QDialog, QGridLayout
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

class VelmirPassiveWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: #1D1A31; color: white;")
        layout = QVBoxLayout(self)

        self.spin = QSpinBox()
        self.spin.setRange(0, 20)
        self.spin.valueChanged.connect(self.update_bonus)

        self.boss_label = QLabel("Mini Bosses Killed: 0")
        self.boss_label.setStyleSheet("font-weight: bold; font-size: 14px;")

        layout.addWidget(self.boss_label)
        layout.addWidget(self.spin)

        # Boss images
        boss_layout = QHBoxLayout()

        self.checkbox1 = QCheckBox("Ancient Troll")
        self.checkbox1.stateChanged.connect(self.update_bonus)
        boss1_img = QLabel()
        boss1_img.setPixmap(QPixmap("assets/passive_menu/Ancient_Troll.png").scaled(120, 120, Qt.KeepAspectRatio))
        boss1_layout = QVBoxLayout()
        boss1_layout.addWidget(boss1_img)
        boss1_layout.addWidget(self.checkbox1)

        self.checkbox2 = QCheckBox("Manticore")
        self.checkbox2.stateChanged.connect(self.update_bonus)
        boss2_img = QLabel()
        boss2_img.setPixmap(QPixmap("assets/passive_menu/Manticore.png").scaled(120, 120, Qt.KeepAspectRatio))
        boss2_layout = QVBoxLayout()
        boss2_layout.addWidget(boss2_img)
        boss2_layout.addWidget(self.checkbox2)

        boss_layout.addLayout(boss1_layout)
        boss_layout.addLayout(boss2_layout)
        layout.addLayout(boss_layout)

        # Bonus display
        self.bonus_label = QLabel("")
        layout.addWidget(self.bonus_label)

        # 내부 보너스 저장
        self._bonus = {}

    def update_bonus(self):
        count = self.spin.value()
        exp = round(count * 0.015, 5)  # +1.5% per kill
        dmg_taken = round(count * 0.015, 5)

        bosses = sum([self.checkbox1.isChecked(), self.checkbox2.isChecked()])
        rep = bosses * 10
        ap = bosses * 2

        self.boss_label.setText(f"Mini Bosses Killed: {count}")
        self.bonus_label.setText(
            f"+{exp * 100:.1f}% Experience Gain\n"
            f"+{dmg_taken * 100:.1f}% Enemy Damage Taken\n"
            f"+{rep}% Reputation\n"
            f"+{ap} Ability Points"
        )

        # 스탯 보너스를 저장
        self._bonus = {
            "combat": {"experience_gain": exp},
            "resistance": {"total_damage_taken": dmg_taken},
            "survival": {},
            "magic": {}
        }
        
    def get_stat_bonus(self) -> dict:
        """외부에서 호출 시 현재 보너스 스탯을 반환"""
        return self._bonus
    
class JorgrimPassiveWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: #1D1A31; color: white;")
        layout = QVBoxLayout(self)

        # trophie 이미지 줄
        self.trophie_images = []
        trophy_layout = QHBoxLayout()
        for i in range(5):
            img_label = QLabel()
            img_label.setAlignment(Qt.AlignCenter)
            self.trophie_images.append(img_label)
            trophy_layout.addWidget(img_label)
        layout.addLayout(trophy_layout)

        # SpinBox + Label
        self.spin = QSpinBox()
        self.spin.setRange(0, 15)
        self.spin.valueChanged.connect(self.update_bonus)

        self.trophie_label = QLabel("Mini bosses trophies: 0")
        self.trophie_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(self.trophie_label)
        layout.addWidget(self.spin)

        # 오른쪽 보스 이미지
        right_layout = QHBoxLayout()
        right_inner = QVBoxLayout()

        self.jorgrim_img = QLabel()
        self.jorgrim_img.setPixmap(QPixmap("assets/passive_menu/Jorgrim.png").scaled(150, 150, Qt.KeepAspectRatio))
        self.jorgrim_img.setAlignment(Qt.AlignCenter)
        right_inner.addWidget(self.jorgrim_img)
        right_layout.addStretch()
        right_layout.addLayout(right_inner)
        right_layout.addStretch()
        layout.addLayout(right_layout)

        # 보너스 요약
        self.bonus_label = QLabel("")
        layout.addWidget(self.bonus_label)

        self._bonus = {}
        self.update_bonus()

    def update_bonus(self):
        n = self.spin.value()
        self.trophie_label.setText(f"Mini bosses trophies: {n}")

        # 이미지 업데이트 (3개당 1개씩 trophies_n.png)
        for i in range(5):
            if n >= (i + 1) * 3:
                pix = QPixmap(f"assets/passive_menu/trophies_{i + 1}.png").scaled(64, 64, Qt.KeepAspectRatio)
                self.trophie_images[i].setPixmap(pix)
            else:
                self.trophie_images[i].clear()

        weapon_damage = round(n * 0.02, 5)
        ap = n // 3

        self.bonus_label.setText(
            f"+{weapon_damage * 100:.1f}% Weapon Damage\n"
            f"+{ap} Ability Points"
        )

        self._bonus = {
            "combat": {"weapon_damage": weapon_damage},
            "survival": {},
            "resistance": {},
            "magic": {}
        }

    def get_stat_bonus(self):
        return self._bonus    

class ArnaPassiveWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: #1D1A31;")
        layout = QHBoxLayout(self)

        # 좌측 2개
        left_col = QVBoxLayout()
        left_col.addWidget(self.create_image("Optimism.png"))
        left_col.addWidget(self.create_image("Second_Wind.png"))

        # 우측 2개
        right_col = QVBoxLayout()
        right_col.addWidget(self.create_image("Heroism.png"))
        right_col.addWidget(self.create_image("Prudence.png"))

        layout.addLayout(left_col)
        layout.addLayout(right_col)

    def create_image(self, filename):
        label = QLabel()
        pixmap = QPixmap(f"assets/passive_menu/{filename}").scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        label.setPixmap(pixmap)
        label.setAlignment(Qt.AlignCenter)
        return label

    def get_stat_bonus(self):
        return {
            "combat": {},
            "survival": {},
            "resistance": {},
            "magic": {}
        }

class DirwinPassiveWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: #1D1A31; color: white;")
        main_layout = QHBoxLayout(self)

        # 좌측: 이미지 + spinbox
        image_layout = QVBoxLayout()
        self.hunt_img = self.create_image("POI_huntgrounds.png")
        self.rest_img = self.create_image("Make_a_Halt.png")
        image_layout.addWidget(self.hunt_img)
        image_layout.addWidget(self.rest_img)

        # 중앙: 입력 필드
        input_layout = QVBoxLayout()

        self.visited_spin = QSpinBox()
        self.visited_spin.setRange(0, 20)
        self.visited_spin.valueChanged.connect(self.update_bonus)

        self.visited_label = QLabel("Hunting ground visited: 0")

        self.skill_spin = QSpinBox()
        self.skill_spin.setRange(1, 10)
        self.skill_spin.valueChanged.connect(self.update_bonus)

        self.skill_label = QLabel("Survival skill invested: 1")

        input_layout.addWidget(self.visited_label)
        input_layout.addWidget(self.visited_spin)
        input_layout.addSpacing(20)
        input_layout.addWidget(self.skill_label)
        input_layout.addWidget(self.skill_spin)

        # 우측: 보너스 표시
        self.bonus_label = QLabel("")
        self.bonus_label.setStyleSheet("font-size: 14px;")
        self.bonus_label.setAlignment(Qt.AlignTop)
        self.bonus_label.setWordWrap(True)

        bonus_layout = QVBoxLayout()
        bonus_layout.addWidget(self.bonus_label)

        # 배치
        main_layout.addLayout(image_layout)
        main_layout.addLayout(input_layout)
        main_layout.addLayout(bonus_layout)

        self._bonus = {}
        self.update_bonus()

    def create_image(self, filename):
        label = QLabel()
        pixmap = QPixmap(f"assets/passive_menu/{filename}").scaled(100, 100, Qt.KeepAspectRatio)
        label.setPixmap(pixmap)
        label.setAlignment(Qt.AlignCenter)
        return label

    def update_bonus(self):
        visited = self.visited_spin.value()
        skill = self.skill_spin.value()

        base_pelt = 20
        pelt_bonus = visited  # +1% per visited
        exp_bonus = round(visited * 0.01, 5)

        ap_bonus = int(skill in [3, 6, 9])
        sp_bonus = int(skill in [3, 6, 9])

        # UI 업데이트
        self.visited_label.setText(f"Hunting ground visited: {visited}")
        self.skill_label.setText(f"Survival skill invested: {skill}")

        self.bonus_label.setText(
            f"Chance to Harvest Pelts: {base_pelt + pelt_bonus}%\n"
            f"+{exp_bonus * 100:.1f}% Experience Gain\n"
            f"+{ap_bonus} Ability Point(s)\n"
            f"+{sp_bonus} Skill Point(s)"
        )

        # stat 보너스 저장 (COMBAT만 적용 가능)
        self._bonus = {
            "combat": {"experience_gain": exp_bonus},
            "survival": {},
            "resistance": {},
            "magic": {}
        }

    def get_stat_bonus(self):
        return self._bonus
    
class JonnaPassiveWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: #1D1A31; color: white;")
        layout = QVBoxLayout(self)

        # 학파 선택
        self.school_combo = QComboBox()
        self.school_combo.addItems(["Pyromantic", "Electromantic", "Geomantic"])
        self.school_combo.currentIndexChanged.connect(self.update_bonus)

        self.school_image = QLabel()
        self.school_image.setAlignment(Qt.AlignCenter)
        self.update_school_image()

        # 스핀박스 3개
        self.inventory_spin = QSpinBox()
        self.inventory_spin.setRange(0, 4)
        self.inventory_spin.valueChanged.connect(self.update_bonus)

        self.read_spin = QSpinBox()
        self.read_spin.setRange(0, 16)
        self.read_spin.valueChanged.connect(self.update_bonus)

        self.sorcery_ap_spin = QSpinBox()
        self.sorcery_ap_spin.setRange(0, 31)
        self.sorcery_ap_spin.valueChanged.connect(self.update_bonus)

        # 라벨
        self.bonus_label = QLabel("")
        self.bonus_label.setStyleSheet("font-size: 13px;")
        self.bonus_label.setWordWrap(True)

        layout.addWidget(self.school_combo)
        layout.addWidget(self.school_image)
        layout.addWidget(QLabel("Magic treatise in the Inventory:"))
        layout.addWidget(self.inventory_spin)
        layout.addWidget(QLabel("Number of Magic treatis read:"))
        layout.addWidget(self.read_spin)
        layout.addWidget(QLabel("AP invested into Sorcery trees:"))
        layout.addWidget(self.sorcery_ap_spin)
        layout.addWidget(self.bonus_label)

        self._bonus = {}
        self.update_bonus()

    def update_school_image(self):
        school = self.school_combo.currentText()
        filename = {
            "Pyromantic": "Pyromantic_Treatise_IV.png",
            "Electromantic": "Electromantic_Treatise_IV.png",
            "Geomantic": "Geomantic_Treatise_IV.png"
        }.get(school, "")
        self.school_image.setPixmap(QPixmap(f"assets/passive_menu/{filename}").scaled(100, 100, Qt.KeepAspectRatio))

    def update_bonus(self):
        self.update_school_image()

        school = self.school_combo.currentText()
        inventory_count = self.inventory_spin.value()
        read_count = self.read_spin.value()
        ap_count = self.sorcery_ap_spin.value()

        # 대응되는 스탯 키
        school_stat = {
            "Pyromantic": "pyromantic_power",
            "Electromantic": "electromagnetic_power",
            "Geomantic": "geomantic_power"
        }[school]

        school_power_bonus = round(inventory_count * 0.05, 5)
        miracle_bonus = round(inventory_count * 0.05, 5)
        backfire_bonus = round(read_count * -0.01, 5)
        exp_bonus = round(ap_count * 0.01, 5)

        self.bonus_label.setText(
            f"+{school_power_bonus * 100:.1f}% {school} Power\n"
            f"+{miracle_bonus * 100:.1f}% Miracle Potency\n"
            f"{backfire_bonus * 100:.1f}% Backfire Chance\n"
            f"+{exp_bonus * 100:.1f}% Experience Gain"
        )

        self._bonus = {
            "combat": {"experience_gain": exp_bonus},
            "magic": {
                school_stat: school_power_bonus,
                "miracle_potency": miracle_bonus,
                "backfire_chance": backfire_bonus
            },
            "survival": {},
            "resistance": {}
        }

    def get_stat_bonus(self):
        return self._bonus

class MahirPassiveWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: #1D1A31; color: white;")
        layout = QHBoxLayout(self)

        # 좌측 이미지
        image_layout = QVBoxLayout()
        self.poi_image = self.create_image("POI_marker.png")
        self.step_image = self.create_image("Step_Aside.png")
        image_layout.addWidget(self.poi_image)
        image_layout.addWidget(self.step_image)

        # 중앙 입력
        input_layout = QVBoxLayout()

        self.poi_spin = QSpinBox()
        self.poi_spin.setRange(0, 100)
        self.poi_spin.valueChanged.connect(self.update_bonus)
        self.poi_label = QLabel("Location visited: 0")

        self.tree_spin = QSpinBox()
        self.tree_spin.setRange(0, 6)
        self.tree_spin.valueChanged.connect(self.update_bonus)
        self.tree_label = QLabel("Ability trees with >6 AP: 0")

        input_layout.addWidget(self.poi_label)
        input_layout.addWidget(self.poi_spin)
        input_layout.addSpacing(20)
        input_layout.addWidget(self.tree_label)
        input_layout.addWidget(self.tree_spin)

        # 보너스
        self.bonus_label = QLabel("")
        self.bonus_label.setStyleSheet("font-size: 13px;")
        self.bonus_label.setWordWrap(True)

        layout.addLayout(image_layout)
        layout.addLayout(input_layout)
        layout.addWidget(self.bonus_label)

        self._bonus = {}
        self.update_bonus()

    def create_image(self, filename):
        label = QLabel()
        pixmap = QPixmap(f"assets/passive_menu/{filename}").scaled(100, 100, Qt.KeepAspectRatio)
        label.setPixmap(pixmap)
        label.setAlignment(Qt.AlignCenter)
        return label

    def update_bonus(self):
        locations = self.poi_spin.value()
        trees = self.tree_spin.value()

        exp_bonus = round(locations * 0.0033, 5)
        fatigue_bonus = round(locations * 0.0033, 5)
        ap_bonus = trees  # UI 표시용

        self.poi_label.setText(f"Location visited: {locations}")
        self.tree_label.setText(f"Ability trees with >6 AP: {trees}")

        self.bonus_label.setText(
            f"+{exp_bonus * 100:.1f}% Experience Gain\n"
            f"+{fatigue_bonus * 100:.1f}% Fatigue Resistance\n"
            f"+{ap_bonus} Ability Points"
        )

        self._bonus = {
            "combat": {"experience_gain": exp_bonus},
            "survival": {"fatigue_resistance": fatigue_bonus},
            "resistance": {},
            "magic": {}
        }

    def get_stat_bonus(self):
        return self._bonus

class LeosthenesPassiveWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: #1D1A31; color: white;")
        layout = QVBoxLayout(self)

        # 이미지 + spin 3세트
        self.weapon_spin = QSpinBox()
        self.weapon_spin.setRange(0, 31)
        self.weapon_spin.valueChanged.connect(self.update_bonus)

        self.sorcery_spin = QSpinBox()
        self.sorcery_spin.setRange(0, 31)
        self.sorcery_spin.valueChanged.connect(self.update_bonus)

        self.utility_spin = QSpinBox()
        self.utility_spin.setRange(0, 31)
        self.utility_spin.valueChanged.connect(self.update_bonus)

        layout.addLayout(self.create_input_block("Onslaught.png", "AP invested into Weaponry trees:", self.weapon_spin))
        layout.addLayout(self.create_input_block("Defensive_Tactic.png", "AP invested into Sorcery trees:", self.sorcery_spin))
        layout.addLayout(self.create_input_block("Seal_of_Reflection.png", "AP invested into Utility trees:", self.utility_spin))

        self.warning_label = QLabel("")
        self.warning_label.setStyleSheet("color: #FF6666; font-weight: bold;")
        layout.addWidget(self.warning_label)

        self.bonus_label = QLabel("")
        self.bonus_label.setStyleSheet("font-size: 13px;")
        self.bonus_label.setWordWrap(True)
        layout.addWidget(self.bonus_label)

        self._bonus = {}
        self.update_bonus()
        self.setLayout(layout)

    def create_input_block(self, img_filename, label_text, spinbox):
        layout = QHBoxLayout()
        img_label = QLabel()
        pixmap = QPixmap(f"assets/passive_menu/{img_filename}").scaled(64, 64, Qt.KeepAspectRatio)
        img_label.setPixmap(pixmap)
        img_label.setAlignment(Qt.AlignCenter)

        text = QLabel(label_text)
        text.setMinimumWidth(220)
        layout.addWidget(img_label)
        layout.addWidget(text)
        layout.addWidget(spinbox)
        return layout

    def update_bonus(self):
        weapon = self.weapon_spin.value()
        sorcery = self.sorcery_spin.value()
        utility = self.utility_spin.value()

        total = weapon + sorcery + utility
        if total != 31:
            self.bonus_label.setText("")
            self._bonus = {
                "combat": {}, "survival": {}, "resistance": {}, "magic": {}
            }
            return
        else:
            self.warning_label.setText("")

        # 계산
        weapon_magic_bonus = round(weapon * 0.015, 5)
        sorcery_weapon_bonus = round(sorcery * 0.015, 5)
        exp_bonus = round(utility * 0.02, 5)
        health_bonus = utility * 2
        energy_bonus = utility * 2

        self.bonus_label.setText(
            f"+{weapon_magic_bonus*100:.1f}% Magic Power\n"
            f"+{sorcery_weapon_bonus*100:.1f}% Weapon Damage\n"
            f"+{exp_bonus*100:.1f}% Experience Gain\n"
            f"+{health_bonus} Max Health\n"
            f"+{energy_bonus} Energy"
        )

        self._bonus = {
            "combat": {"weapon_damage": sorcery_weapon_bonus, "experience_gain": exp_bonus},
            "magic": {"magic_power": weapon_magic_bonus},
            "survival": {
                "max_health": health_bonus,
                "energy": energy_bonus
            },
            "resistance": {}
        }

    def get_stat_bonus(self):
        return self._bonus


animal_data = {
    "Gulon": ("life_drain", 0.0033, 0.07),
    "Young Troll": ("total_damage_taken", -0.005, -0.10),
    "Bear": ("weapon_damage", 0.005, 0.10),
    "Harpy": ("dodge_chance", 0.0025, 0.10),
    "Crawler": ("energy_drain", 0.0025, 0.07),
    "Bison": ("max_health", 0.005, 0.10),
    "Deer": ("energy", 0.002, 0.08),
    "Wolf": ("skills_energy_cost", -0.0025, -0.10),
    "Moose": ("magic_power", 0.005, 0.15),
    "Boar": ("cooldowns_duration", -0.0033, -0.10),
    "Ghoul": ("health_restoration", 0.002, 0.10)
}

        #동물 검색
class AnimalSelectorDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Bonus Animals")
        self.setFixedSize(1000, 1000)
        self.setStyleSheet("background-color: #1D1A31; color: white;")
        self.selected_animals = {}
        self.checkboxes = {}

        self.positions = {
            "Deer": (40, 20), "Wolf": (250, 20), "Ghoul": (460, 20), "Boar": (670, 20),
            "Moose": (40, 300), "Crawler": (250, 300), "Harpy": (460, 300), "Gulon": (670, 300),
            "Bison": (60, 600), "Bear": (350, 600), "Young Troll": (640, 600)
        }

        self.checkbox_list = []

        for name, (x, y) in self.positions.items():
            stat, per_kill, max_bonus = animal_data[name]
            size = 280 if name in ["Bison", "Bear", "Young Troll"] else 200

            # 이미지
            img = QLabel(self)
            img_path = f"assets/passive_menu/{name.replace(' ', '_')}.png"
            pixmap = QPixmap(img_path)
            if pixmap.isNull():
                img.setText(f"[No Image]")
                img.setStyleSheet("color: red; font-size: 10px;")
                img.setAlignment(Qt.AlignCenter)
            else:
                pixmap = pixmap.scaled(size - 60, size - 60, Qt.KeepAspectRatio, Qt.FastTransformation)
                img.setPixmap(pixmap)
                img.setStyleSheet("background-color: #2F3045; color: white;")
                img.setAlignment(Qt.AlignCenter)
            img.setFixedSize(size, size)
            img.move(x, y)

            # 체크박스
            checkbox = QCheckBox(name, self)
            checkbox.move(x + 10, y + size + 15)
            checkbox.setStyleSheet("background-color: #2F3045; color: white;")
            checkbox.stateChanged.connect(self.limit_selection)
            self.checkbox_list.append(checkbox)

            # 스핀박스
            spin = QSpinBox(self)
            spin.setRange(0, int(abs(max_bonus / per_kill)))
            spin.setValue(0)
            spin.move(x + size - 40*(size//100), y + size + 15)

            # 설명
            display_stat = stat.replace('_', ' ').title()
            stat_label = QLabel(f"{display_stat}\n({per_kill*100:.2f}%/kill, max {round(max_bonus/per_kill)})", self)
            stat_label.setStyleSheet("background-color: #2F3045; color: white; font-size: 18px;")
            stat_label.move(x, y + size - 40)

            self.checkboxes[name] = (checkbox, spin)

        # Confirm 버튼
        btn_ok = QPushButton("Confirm", self)
        btn_ok.clicked.connect(self.accept_selection)
        btn_ok.setFixedWidth(120)
        btn_ok.move(400, 950)

    def limit_selection(self):
        # 현재 선택된 수
        checked = [cb for cb in self.checkbox_list if cb.isChecked()]
        if len(checked) >= 3:
            for cb in self.checkbox_list:
                if not cb.isChecked():
                    cb.setEnabled(False)
        else:
            for cb in self.checkbox_list:
                cb.setEnabled(True)

    def accept_selection(self):
        self.selected_animals = {
            name: spin.value()
            for name, (cb, spin) in self.checkboxes.items()
            if cb.isChecked()
        }
        self.accept()

# --- Hilda 메인 위젯 ---
class HildaPassiveWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: #1D1A31; color: white;")
        self.selected_animals = {}
        self._bonus = {}

        main_layout = QHBoxLayout(self)

        # Trinket image
        self.trinket_label = QLabel()
        pix = QPixmap("assets/passive_menu/Hildatrinket.png").scaled(150, 150, Qt.KeepAspectRatio)
        self.trinket_label.setPixmap(pix)
        self.trinket_label.mousePressEvent = self.open_animal_dialog
        main_layout.addWidget(self.trinket_label)

        # 우측: Level + 동물 보너스
        right_layout = QVBoxLayout()

        self.level_spin = QSpinBox()
        self.level_spin.setRange(1, 30)
        self.level_spin.valueChanged.connect(self.update_bonus)
        self.level_label = QLabel("Level: 1")

        right_layout.addWidget(self.level_label)
        right_layout.addWidget(self.level_spin)

        right_layout.addWidget(QLabel("[ Bonus Animals ]"))
        self.bonus_labels = []
        for _ in range(3):
            label = QLabel("-")
            self.bonus_labels.append(label)
            right_layout.addWidget(label)

        main_layout.addLayout(right_layout)
        self.update_bonus()

    def open_animal_dialog(self, event):
        dialog = AnimalSelectorDialog(self)
        if dialog.exec_():
            self.selected_animals = dialog.selected_animals
            self.update_bonus()

    def update_bonus(self):
        level = self.level_spin.value()
        self.level_label.setText(f"Level: {level}")

        # 기본 보너스 (UI 출력용)
        threshold_resistance = (level - 1) * 0.5
        bonus_lines = [f"Level bonus: +{threshold_resistance:.1f}% threshold resistance"]

        # 동물 보너스
        self._bonus = {
            "combat": {},
            "survival": {},
            "resistance": {},
            "magic": {}
        }

        for idx, label in enumerate(self.bonus_labels):
            if idx < len(self.selected_animals):
                animal_name = list(self.selected_animals.keys())[idx]
                kill_count = self.selected_animals[animal_name]
                stat, per_kill, max_bonus = animal_data[animal_name]
                raw_bonus = round(kill_count * per_kill, 5)

                # clamp to max
                if per_kill > 0:
                    raw_bonus = min(raw_bonus, max_bonus)
                else:
                    raw_bonus = max(raw_bonus, max_bonus)
                display_stat = stat.replace('_', ' ').title()
                label.setText(f"{animal_name}: {kill_count} kill(s) → {display_stat} {raw_bonus*100:.2f}%")
                # 스탯 범주 판별
                for cat in self._bonus:
                    if stat in self._bonus[cat]:
                        self._bonus[cat][stat] += raw_bonus
                        break
                    elif cat == "combat" and stat in ["weapon_damage", "experience_gain"]:
                        self._bonus[cat][stat] = raw_bonus
                    elif cat == "magic" and stat in ["magic_power", "life_drain", "energy_drain"]:
                        self._bonus[cat][stat] = raw_bonus
                    elif cat == "resistance" and stat == "total_damage_taken":
                        self._bonus[cat][stat] = raw_bonus
                    elif cat == "survival":
                        self._bonus[cat][stat] = raw_bonus
            else:
                label.setText("-")

    def get_stat_bonus(self):
        return self._bonus


passive_widget_map = {
    "Velmir": VelmirPassiveWidget,
    "Jorgrim": JorgrimPassiveWidget,
    "Arna": ArnaPassiveWidget,
    "Dirwin": DirwinPassiveWidget,
    "Jonna": JonnaPassiveWidget,
    "Mahir": MahirPassiveWidget,
    "Leosthenes": LeosthenesPassiveWidget,
    "Hilda": HildaPassiveWidget,
}
    

if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    window = HildaPassiveWidget()
    window.setWindowTitle("Velmir Passive UI Test")
    window.resize(400, 400)
    window.show()
    sys.exit(app.exec_())