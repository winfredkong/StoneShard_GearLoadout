from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSpinBox, QCheckBox, QPushButton, QComboBox, QDialog, QGridLayout
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, pyqtSignal

class VelmirPassiveWidget(QWidget):
    stat_bonus_changed = pyqtSignal()
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(400, 300)
        self.setStyleSheet("background-color: #1D1A31; color: white;")

        self.boss_label = QLabel("Mini Bosses Killed : ", self)
        self.boss_label.move(20, 20)
        self.boss_label.setStyleSheet("font-size: 16px;")

        self.spin = QSpinBox(self)
        self.spin.setRange(0, 20)
        self.spin.move(170, 18)
        self.spin.valueChanged.connect(self.update_bonus)

        self.checkbox1 = QCheckBox("Ancient Troll", self)
        self.checkbox1.move(20, 175)
        self.checkbox1.setStyleSheet("background-color: #1D1A31;")
        self.checkbox1.stateChanged.connect(self.update_bonus)

        self.checkbox2 = QCheckBox("Manticore", self)
        self.checkbox2.move(200, 175)
        self.checkbox2.setStyleSheet("background-color: #1D1A31;")
        self.checkbox2.stateChanged.connect(self.update_bonus)

        self.boss1_img = QLabel(self)
        self.boss1_img.setPixmap(QPixmap("assets/passive_menu/Ancient_Troll.png").scaled(120, 120, Qt.KeepAspectRatio, Qt.FastTransformation))
        self.boss1_img.move(20, 50)

        self.boss2_img = QLabel(self)
        self.boss2_img.setPixmap(QPixmap("assets/passive_menu/Manticore.png").scaled(160, 160, Qt.KeepAspectRatio, Qt.FastTransformation))
        self.boss2_img.move(180, 40)

        self.bonus_label = QLabel("", self)
        self.bonus_label.move(20, 200)
        self.bonus_label.setFixedSize(360, 100)
        self.bonus_label.setStyleSheet("font-size: 16px;")
        self.bonus_label.setWordWrap(True)

        self._bonus = {}
        self.update_bonus()

    def update_bonus(self):        
        count = self.spin.value()
        exp = round(count * 0.015, 5)
        dmg = round(count * 0.015, 5)
        bosses = sum([self.checkbox1.isChecked(), self.checkbox2.isChecked()])
        rep = bosses * 10
        ap = bosses * 2

        self.boss_label.setText(f"Mini Bosses Killed : ")
        self.bonus_label.setText(
            f"+{exp * 100:.1f}% Experience Gain\n"
            f"+{dmg * 100:.1f}% Enemy Damage Taken\n"
            f"+{rep}% Reputation\n"
            f"+{ap} Stat Points"
        )

        self._bonus = {
            "combat": {"experience_gain": exp},
            "resistance": {},
            "survival": {},
            "magic": {}
        }
        self.stat_bonus_changed.emit()

    def get_stat_bonus(self):
        return self._bonus

    def get_bonus_points(self):
        bosses = sum([self.checkbox1.isChecked(), self.checkbox2.isChecked()])
        return {"ap": bosses * 2, "sp": 0}
    
class JorgrimPassiveWidget(QWidget):
    stat_bonus_changed = pyqtSignal()
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(400, 300)
        self.setStyleSheet("background-color: #1D1A31; color: white;")

        self.trophie_label = QLabel("Mini Bosses Trophies : ", self)
        self.trophie_label.move(20, 20)
        self.trophie_label.setStyleSheet("font-size: 16px; color : white;")

        self.spin = QSpinBox(self)
        self.spin.setRange(0, 15)
        self.spin.move(195, 18)
        self.spin.valueChanged.connect(self.update_bonus)

        self.trophie_img = QLabel(self)
        self.trophie_img.setPixmap(QPixmap("assets/passive_menu/Jorgrim.png").scaled(100, 100, Qt.KeepAspectRatio, Qt.FastTransformation))
        self.trophie_img.move(260, 70)

        # trophies 1~5
        self.trophie_icons = []
        for i in range(5):
            label = QLabel(self)
            label.setFixedSize(50, 50)
            label.move(20 + (i%3)*70, 70 + (i//3)*70)
            label.setAlignment(Qt.AlignCenter)
            self.trophie_icons.append(label)

        self.bonus_label = QLabel("", self)
        self.bonus_label.setStyleSheet("font-size: 16px;")
        self.bonus_label.setWordWrap(True)
        self.bonus_label.setFixedSize(360, 100)
        self.bonus_label.move(20, 200)
        

        self._bonus = {}
        self.update_bonus()

    def update_bonus(self):
        count = self.spin.value()
        self.trophie_label.setText(f"Mini Bosses Trophies : ")
        ap = count // 3
        weapon = round(count * 0.02, 5)

        for i in range(5):
            if count >= (i+1)*3:
                pix = QPixmap(f"assets/passive_menu/trophies_{i+1}.png")
                if not pix.isNull():
                    pix = pix.scaled(30, 30, Qt.KeepAspectRatio, Qt.FastTransformation)
                    self.trophie_icons[i].setPixmap(pix)
                else:
                    self.trophie_icons[i].clear()
            else:
                self.trophie_icons[i].clear()

        self.bonus_label.setText(
            f"+{weapon * 100:.1f}% Weapon Damage\n"
            f"+{ap} Stat Points"
        )

        self._bonus = {
            "combat": {"weapon_damage": weapon},
            "survival": {},
            "resistance": {},
            "magic": {}
        }
        self.stat_bonus_changed.emit()

    def get_stat_bonus(self):
        return self._bonus

    def get_bonus_points(self):
        return {"ap": self.spin.value() // 3, "sp": 0}

class ArnaPassiveWidget(QWidget):
    stat_bonus_changed = pyqtSignal()
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(400, 300)
        self.setStyleSheet("background-color: #1D1A31;")

        # 이미지 4장 배치 (2x2)
        images = ["Optimism.png", "Second_Wind.png", "Heroism.png", "Prudence.png"]
        positions = [(30, 30), (150, 30), (30, 150), (150, 150)]

        for img_file, (x, y) in zip(images, positions):
            label = QLabel(self)
            pixmap = QPixmap(f"assets/passive_menu/{img_file}")
            if not pixmap.isNull():
                label.setPixmap(pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.FastTransformation))
            else:
                label.setText("[No Image]")
            label.move(x, y)

    def get_stat_bonus(self):
        return {
            "combat": {},
            "survival": {},
            "resistance": {},
            "magic": {}
        }

    def get_bonus_points(self):
        return {"ap": 0, "sp": 0}

class DirwinPassiveWidget(QWidget):
    stat_bonus_changed = pyqtSignal()
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(400, 300)
        self.setStyleSheet("background-color: #1D1A31; color: white;")

        # Hunting Grounds
        self.hunt_label = QLabel("Hunting Grounds Visited:", self)
        self.hunt_label.move(120, 50)
        self.hunt_spin = QSpinBox(self)
        self.hunt_spin.setRange(0, 20)
        self.hunt_spin.move(320, 45)
        self.hunt_spin.valueChanged.connect(self.update_bonus)

        # Survival Skill
        self.skill_label = QLabel("Survival Skill Invested:", self)
        self.skill_label.move(120, 150)
        self.skill_spin = QSpinBox(self)
        self.skill_spin.setRange(1, 10)
        self.skill_spin.move(320, 145)
        self.skill_spin.valueChanged.connect(self.update_bonus)

        # 이미지 2개
        self.img1 = QLabel(self)
        self.img1.setPixmap(QPixmap("assets/passive_menu/POI_huntgrounds.png").scaled(80, 80, Qt.KeepAspectRatio, Qt.FastTransformation))
        self.img1.move(20, 20)

        self.img2 = QLabel(self)
        self.img2.setPixmap(QPixmap("assets/passive_menu/Make_a_Halt.png").scaled(80, 80, Qt.KeepAspectRatio, Qt.FastTransformation))
        self.img2.move(20, 120)

        # 보너스 출력
        self.bonus_label = QLabel("", self)
        self.bonus_label.setWordWrap(True)
        self.bonus_label.setFixedSize(360, 90)
        self.bonus_label.move(20, 210)
        self.bonus_label.setStyleSheet("font-size: 16px;")

        self._bonus = {}
        self.update_bonus()

    def update_bonus(self):        
        visited = self.hunt_spin.value()
        skill = self.skill_spin.value()
        pelt_chance = 20 + visited
        exp = visited * 0.01
        ap = (skill//3)
        sp = (skill//3)

        self.bonus_label.setText(
            f"Chance to Harvest Pelts: {pelt_chance}%\n"
            f"+{exp*100:.1f}% Experience Gain\n"
            f"+{ap} Stat Point(s)\n"
            f"+{sp} Ability Point(s)"
        )

        self._bonus = {
            "combat": {"experience_gain": exp},
            "survival": {},
            "resistance": {},
            "magic": {}
        }
        self._ap = ap
        self._sp = sp
        self.stat_bonus_changed.emit()

    def get_stat_bonus(self):
        return self._bonus

    def get_bonus_points(self):
        return {"ap": self._ap, "sp": self._sp}
    
class JonnaPassiveWidget(QWidget):
    stat_bonus_changed = pyqtSignal()
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(400, 300)
        self.setStyleSheet("background-color: #1D1A31; color: white;")

        # 학파 선택
        self.school_combo = QComboBox(self)
        self.school_combo.addItems(["Pyromantic", "Electromantic", "Geomantic"])
        self.school_combo.move(80, 40)
        self.school_combo.currentIndexChanged.connect(self.update_bonus)

        # 학파 이미지
        self.school_image = QLabel(self)
        self.school_image.setFixedSize(40, 80)
        self.school_image.move(20, 10)

        # treatise in inventory
        QLabel("Treatise in Inventory:", self).move(20, 100)
        self.inventory_spin = QSpinBox(self)
        self.inventory_spin.setRange(0, 4)
        self.inventory_spin.move(220, 100)
        self.inventory_spin.valueChanged.connect(self.update_bonus)

        # treatise read
        QLabel("Treatise Read:", self).move(20, 140)
        self.read_spin = QSpinBox(self)
        self.read_spin.setRange(0, 16)
        self.read_spin.move(220, 140)
        self.read_spin.valueChanged.connect(self.update_bonus)

        # sorcery AP
        QLabel("Sorcery AP:", self).move(20, 175)
        self.sorcery_ap_spin = QSpinBox(self)
        self.sorcery_ap_spin.setRange(0, 31)
        self.sorcery_ap_spin.move(220, 175)
        self.sorcery_ap_spin.setStyleSheet("font-size : 16px;")
        self.sorcery_ap_spin.valueChanged.connect(self.update_bonus)

        # 보너스
        self.bonus_label = QLabel("", self)
        self.bonus_label.setWordWrap(True)
        self.bonus_label.setFixedSize(360, 90)
        self.bonus_label.move(20, 200)
        self.bonus_label.setStyleSheet("font-size: 16px;")

        self._bonus = {}
        self.update_bonus()

    def update_school_image(self):
        school = self.school_combo.currentText()
        filename = {
            "Pyromantic": "Pyromantic_Treatise_IV.png",
            "Electromantic": "Electromantic_Treatise_IV.png",
            "Geomantic": "Geomantic_Treatise_IV.png"
        }.get(school, "")
        pixmap = QPixmap(f"assets/passive_menu/{filename}")
        if not pixmap.isNull():
            self.school_image.setPixmap(pixmap.scaled(40, 80, Qt.KeepAspectRatio, Qt.FastTransformation))

    def update_bonus(self):
        self.update_school_image()

        school = self.school_combo.currentText()
        inv = self.inventory_spin.value()
        read = self.read_spin.value()
        ap = self.sorcery_ap_spin.value()

        school_stat = {
            "Pyromantic": "pyromantic_power",
            "Electromantic": "electromagnetic_power",
            "Geomantic": "geomantic_power"
        }[school]

        school_bonus = round(inv * 0.05, 5)
        miracle = round(inv * 0.05, 5)
        backfire = round(read * -0.01, 5)
        exp = round(ap * 0.01, 5)

        self.bonus_label.setText(
            f"+{school_bonus*100:.1f}% {school} Power\n"
            f"+{miracle*100:.1f}% Miracle Potency\n"
            f"{backfire*100:.1f}% Backfire Chance\n"
            f"+{exp*100:.1f}% Experience Gain"
        )

        self._bonus = {
            "combat": {"experience_gain": exp},
            "magic": {
                school_stat: school_bonus,
                "miracle_potency": miracle,
                "backfire_chance": backfire
            },
            "survival": {},
            "resistance": {}
        }
        self.stat_bonus_changed.emit()

    def get_stat_bonus(self):
        return self._bonus

    def get_bonus_points(self):
        return {"ap": 0, "sp": 0}

class MahirPassiveWidget(QWidget):
    stat_bonus_changed = pyqtSignal()
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(400, 300)
        self.setStyleSheet("background-color: #1D1A31; color: white;")

        # 위치 수
        QLabel("Location Visited:", self).move(110, 50)
        self.poi_spin = QSpinBox(self)
        self.poi_spin.setRange(0, 100)
        self.poi_spin.move(340, 50)
        self.poi_spin.valueChanged.connect(self.update_bonus)

        # 트리 수
        QLabel("Each Skill Tree \ninvested more than 6AP:", self).move(110, 130)
        self.tree_spin = QSpinBox(self)
        self.tree_spin.setRange(0, 6)
        self.tree_spin.move(340, 150)
        self.tree_spin.valueChanged.connect(self.update_bonus)

        # 이미지
        self.poi_img = QLabel(self)
        self.poi_img.setPixmap(QPixmap("assets/passive_menu/POI_marker.png").scaled(75, 75, Qt.KeepAspectRatio, Qt.FastTransformation))
        self.poi_img.move(22, 22)

        self.step_img = QLabel(self)
        self.step_img.setPixmap(QPixmap("assets/passive_menu/Step_Aside.png").scaled(80, 80, Qt.KeepAspectRatio, Qt.FastTransformation))
        self.step_img.move(20, 110)

        # 보너스
        self.bonus_label = QLabel("", self)
        self.bonus_label.setWordWrap(True)
        self.bonus_label.setFixedSize(360, 100)
        self.bonus_label.move(20, 200)
        self.bonus_label.setStyleSheet("font-size: 16px;")

        self._bonus = {}
        self.update_bonus()

    def update_bonus(self):
        loc = self.poi_spin.value()
        tree = self.tree_spin.value()

        exp = round(loc * 0.0033, 5)
        fatigue = round(loc * 0.0033, 5)
        ap = tree

        self.bonus_label.setText(
            f"+{exp*100:.1f}% Experience Gain\n"
            f"+{fatigue*100:.1f}% Fatigue Resistance\n"
            f"+{ap} Ability Points"
        )

        self._bonus = {
            "combat": {"experience_gain": exp},
            "survival": {"fatigue_resistance": fatigue},
            "resistance": {},
            "magic": {}
        }
        self.stat_bonus_changed.emit()

    def get_stat_bonus(self):
        return self._bonus

    def get_bonus_points(self):
        return {"sp": self.tree_spin.value(), "sp": 0}

class LeosthenesPassiveWidget(QWidget):
    stat_bonus_changed = pyqtSignal()
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(400, 300)
        self.setStyleSheet("background-color: #1D1A31; color: white;")
        self.max_total_sp = 31

        # --- 아이콘 + 라벨 + 스핀박스 ---
        y_offsets = [20, 80, 140]
        icons = [
            ("Onslaught.png", "Weaponry SP : ", "weapon_spin"),
            ("Defensive_Tactic.png", "Utility SP : ", "utility_spin"),
            ("Seal_of_Reflection.png", "Sorcery SP : ", "sorcery_spin"),
        ]

        for i, (img, text, attr_name) in enumerate(icons):
            y = y_offsets[i]

            icon = QLabel(self)
            icon.setPixmap(QPixmap(f"assets/passive_menu/{img}").scaled(60, 60, Qt.KeepAspectRatio, Qt.FastTransformation))
            icon.move(20, y)

            label = QLabel(text, self)
            label.move(90, y + 18)  # 라벨은 아이콘보다 살짝 중앙에

            spin = QSpinBox(self)
            spin.setRange(0, 31)
            spin.move(220, y + 18)
            spin.valueChanged.connect(self.limit_spins)

            setattr(self, attr_name, spin)

        # --- 보너스 라벨 ---
        self.bonus_label = QLabel("", self)
        self.bonus_label.setWordWrap(True)
        self.bonus_label.setFixedSize(360, 100)
        self.bonus_label.move(20, 200)
        self.bonus_label.setStyleSheet("font-size: 16px;")

        self._bonus = {}
        self.limit_spins()

    def limit_spins(self):
        w = self.weapon_spin.value()
        s = self.sorcery_spin.value()
        u = self.utility_spin.value()

        if self.sender() == self.weapon_spin:
            self.sorcery_spin.setMaximum(self.max_total_sp - w - self.utility_spin.value())
            self.utility_spin.setMaximum(self.max_total_sp - w - self.sorcery_spin.value())
        elif self.sender() == self.sorcery_spin:
            self.weapon_spin.setMaximum(self.max_total_sp - s - self.utility_spin.value())
            self.utility_spin.setMaximum(self.max_total_sp - s - self.weapon_spin.value())
        elif self.sender() == self.utility_spin:
            self.weapon_spin.setMaximum(self.max_total_sp - u - self.sorcery_spin.value())
            self.sorcery_spin.setMaximum(self.max_total_sp - u - self.weapon_spin.value())

        self.update_bonus()

    def update_bonus(self):
        w = self.weapon_spin.value()
        s = self.sorcery_spin.value()
        u = self.utility_spin.value()

        mp = round(w * 0.015, 5)
        wd = round(s * 0.015, 5)
        exp = round(u * 0.02, 5)
        hp = u * 2
        en = u * 2

        self.bonus_label.setText(
            f"+{mp*100:.1f}% Magic Power\n"
            f"+{wd*100:.1f}% Weapon Damage\n"
            f"+{exp*100:.1f}% Experience Gain\n"
            f"+{hp} Max Health, +{en} Energy"
        )

        self._bonus = {
            "combat": {"weapon_damage": wd, "experience_gain": exp},
            "magic": {"magic_power": mp},
            "survival": {"max_health": hp, "energy": en},
            "resistance": {}
        }
        self.stat_bonus_changed.emit()

    def get_stat_bonus(self):
        return self._bonus

    def get_bonus_points(self):
        return {"ap": 0, "sp": 0}



# ✅ animal_data
animal_data = {
    "Gulon": ("life_drain", 0.02, 0.0033, 0.07),
    "Young Troll": ("total_damage_taken", -0.03, -0.005, -0.10),
    "Bear": ("weapon_damage", 0.03, 0.005, 0.10),
    "Harpy": ("dodge_chance", 0.03, 0.0025, 0.10),
    "Crawler": ("energy_drain", 0.03, 0.0025, 0.07),
    "Bison": ("max_health", 0.02, 0.005, 0.10),
    "Deer": ("energy", 0.02, 0.002, 0.08),
    "Wolf": ("skills_energy_cost", -0.02, -0.0025, -0.10),
    "Moose": ("magic_power", 0.03, 0.005, 0.15),
    "Boar": ("cooldowns_duration", -0.03, -0.0033, -0.10),
    "Ghoul": ("health_restoration", 0.03, 0.002, 0.10)
}

# AnimalSelectorDialog
class AnimalSelectorDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Bonus Animals")
        self.setFixedSize(950, 1000)
        self.setStyleSheet("background-color: #1D1A31; color: white;")
        self.selected_animals = {}
        self.checkboxes = {}

        self.positions = {
            "Deer": (40, 20), "Wolf": (250, 20), "Ghoul": (460, 20), "Boar": (670, 20),
            "Moose": (40, 300), "Crawler": (250, 300), "Harpy": (460, 300), "Gulon": (670, 300),
            "Bison": (40, 600), "Bear": (325, 600), "Young Troll": (610, 600)
        }

        self.checkbox_list = []

        for name, (x, y) in self.positions.items():
            stat, base, per_kill, max_bonus = animal_data[name]
            size = 260 if name in ["Bison", "Bear", "Young Troll"] else 200

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
            checkbox.move(x + 10, y + size + 10)
            checkbox.setStyleSheet("color: white;")
            checkbox.stateChanged.connect(self.limit_selection)
            self.checkbox_list.append(checkbox)

            # 스핀박스
            spin = QSpinBox(self)
            max_kills = int(abs((max_bonus - base) / per_kill))
            spin.setRange(0, max_kills)
            spin.setValue(0)
            spin.move(x + size - 40*(size//100), y + size + 10)
            spin.setStyleSheet("border : 0px")

            # 설명
            display_stat = stat.replace('_', ' ').title()
            stat_label = QLabel(f"Base: {base*100:.0f}% | {per_kill*100:.2f}%/kill \nMax stack : {round((max_bonus-base)/per_kill)}", self)
            stat_label.setStyleSheet("background-color: #2F3045; color: white; font-size: 18px;")
            stat_label.move(x, y + size - 42)
            stat_stats = QLabel(f"{display_stat}", self)
            stat_stats.setStyleSheet("background-color: #2F3045; color: lightgray; font-size: 18px; font-weight : bold;")
            stat_stats.move(x, y)
            

            self.checkboxes[name] = (checkbox, spin)

        # Confirm 버튼
        btn_ok = QPushButton("Confirm", self)
        btn_ok.clicked.connect(self.accept_selection)
        btn_ok.setFixedSize(120,40)
        btn_ok.move(400, 940)
        btn_ok.setStyleSheet("background-color : #2D3045; color: lightgray; font-weight: bold; font-size:20px;")

    def limit_selection(self):
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

# HildaPassiveWidget
class HildaPassiveWidget(QWidget):
    stat_bonus_changed = pyqtSignal()
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(400, 300)
        self.setStyleSheet("background-color: #1D1A31; color: white;")

        self.selected_animals = {}
        self._bonus = {}

        self.trinket = QLabel(self)
        self.trinket.setStyleSheet("background-color: #222023;")
        pix = QPixmap("assets/passive_menu/Hildatrinket.png")
        if not pix.isNull():
            self.trinket.setPixmap(pix.scaled(80, 200, Qt.KeepAspectRatio, Qt.FastTransformation))
        self.trinket.move(20, 120)
        self.trinket.mousePressEvent = self.open_dialog

        QLabel("Level :", self).move(20, 30)
        self.level_spin = QSpinBox(self)
        self.level_spin.setRange(1, 30)
        self.level_spin.move(90, 25)
        self.level_spin.setStyleSheet("border: 0px;")
        self.level_spin.valueChanged.connect(self.update_bonus)

        self.bonus_label = QLabel("", self)
        self.bonus_label.setWordWrap(True)
        self.bonus_label.setFixedSize(360, 40)
        self.bonus_label.move(20, 50)
        self.bonus_label.setStyleSheet("font-size: 16px;")

        self.bonus_slots = []
        for i in range(3):
            label = QLabel("-", self)
            label.setFixedSize(280, 50)
            label.move(110, 120 + i * 60)
            label.setStyleSheet("background-color: #231F3B;")
            self.bonus_slots.append(label)

        self.update_bonus()
        self.animal_selector_dialog = None

    def open_dialog(self, event):
        if self.animal_selector_dialog is None:
            self.animal_selector_dialog = AnimalSelectorDialog(self)

        if self.animal_selector_dialog.exec_():
            self.selected_animals = self.animal_selector_dialog.selected_animals
            self.update_bonus()

    def update_bonus(self):
        level = self.level_spin.value()
        threshold = (level - 1) * 0.5
        self.bonus_label.setText(f"+{threshold:.1f}% Increase Threshold \n(Hunger, Thirst, Pain, Intoxication, and Fatigue)")
        self.bonus_label.setStyleSheet("font-size: 16px;")

        self._bonus = {"combat": {}, "survival": {}, "resistance": {}, "magic": {}}

        for i, label in enumerate(self.bonus_slots):
            if i < len(self.selected_animals):
                animal = list(self.selected_animals.keys())[i]
                kills = self.selected_animals[animal]
                stat, base, per, max_ = animal_data[animal]
                bonus = round(base + kills * per, 5)
                bonus = min(bonus, max_) if per > 0 else max(bonus, max_)
                display_stat = stat.replace('_', ' ').title()
                label.setText(f"{animal} : {kills} kills\n{display_stat} : {bonus*100:.2f}%")
                self._bonus = self._merge_stat(self._bonus, stat, bonus)
            else:
                if i == 0:
                    label.setText("<- Click Bone Charm to start")
                else:
                    label.setText("-")
        self.stat_bonus_changed.emit()

    def _merge_stat(self, bonus, stat, value):
        for cat in bonus:
            if stat in bonus[cat]:
                bonus[cat][stat] += value
                return bonus
        if stat in ["weapon_damage", "experience_gain", "life_drain", "energy_drain"]:
            bonus["combat"][stat] = value
        elif stat in ["magic_power"]:
            bonus["magic"][stat] = value
        elif stat == "total_damage_taken":
            bonus["resistance"][stat] = value
        else:
            bonus["survival"][stat] = value
        return bonus

    def get_stat_bonus(self):
        return self._bonus

    def get_bonus_points(self):
        return {"ap": 0, "sp": 0}



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
    window.resize(400, 300)
    window.show()
    sys.exit(app.exec_())