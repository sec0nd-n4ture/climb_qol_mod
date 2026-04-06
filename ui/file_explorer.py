from soldat_extmod_api.graphics_helper.gui_addon import Container, Button
from soldat_extmod_api.mod_api import ModAPI, Color, FontStyle, Vector2D
from typing import Callable
from pathlib import Path

ROW_PADDING = Vector2D(0.0, 0.0)
ROW_START_PADDING_Y = 19.0

json_ignore_list = [
    "hotkey.json", "mod_config.json"
]

class FileExplorer(Container):
    def __init__(
            self, 
            mod_api: ModAPI, 
            padding_x: float, 
            padding_y: float, 
            file_pick_callback: Callable[[str], None]
        ):
        self.title_text = mod_api.create_interface_text(
            "Config Explorer",
            Vector2D.zero(),
            Color.from_hex("ffffffff"),
            Color.from_hex("000000ff"),
            1.0,
            Vector2D(0.8, 1.6),
            FontStyle.FONT_SMALL_BOLD,
            0.8
        )
        self.api = mod_api
        super().__init__(
            mod_api.get_gui_frame(), 
            padding_x, 
            padding_y, 
            mod_api.create_interface_image(
                "graphics/config_ui_back.png",
                scale=Vector2D(0.46, 0.46)
            ), 
            True
        )
        self.file_pick_callback: None | Callable[[str], None] = file_pick_callback
        self.file_rows: list[FileRow] = []
        for _ in range(9):
            self.add_row()
        self.hidden = False
        self.hide()

    def refresh_files(self):
        if self.hidden:
            return
        file_list = self.get_file_list()
        list_len = len(file_list)
        for i in range(9):
            if i < list_len:
                self.file_rows[i].set_file_name(file_list[i])
                self.file_rows[i].show()
            else:
                self.file_rows[i].hide()

    def get_file_list(self) -> list[str]:
        files = []
        cwd = Path.cwd()
        for file in cwd.iterdir():
            if file.name.endswith(".json") and file.name not in json_ignore_list:
                files.append(file.name)
        return files

    def set_pos(self, pos: Vector2D):
        super().set_pos(pos)
        self.title_text.set_pos(pos + Vector2D(38.0, 8.0))

    def add_row(self):
        row = FileRow(self.api, self, 0, 0)
        if self.file_rows:
            position = self.file_rows[-1].corner_bottom_left
        else:
            position = row.position.add(Vector2D(3.0, ROW_START_PADDING_Y))
        row.set_pos(position)
        self.file_rows.append(row)

    def element_click_action(self, file_name: str):
        if self.file_pick_callback:
            self.hide()
            self.file_pick_callback(file_name)

    def hide(self):
        if not self.hidden:
            self.hidden = True
            self.image.hide()
            self.title_text.hide()
            for row in self.file_rows:
                row.hide()

    def show(self):
        if self.hidden:
            self.hidden = False
            self.image.show()
            self.title_text.show()
            self.refresh_files()

    def destroy(self):
        self.hide()
        self.image.destroy()
        for row in self.file_rows:
            row.destroy()

class FileRow(Button):
    def __init__(self, mod_api: ModAPI, parent: FileExplorer, padding_x: float, padding_y: float):
        self.file_text = mod_api.create_interface_text(
            "",
            Vector2D.zero(),
            Color.from_hex("ffffffff"),
            Color.from_hex("000000ff"),
            1.0,
            Vector2D(0.5, 1),
            FontStyle.FONT_SMALLEST,
            0.5
        )
        super().__init__(
            mod_api, 
            parent, 
            padding_x, 
            padding_y, 
            mod_api.create_interface_image(
                "graphics/file_row.png",
                scale=Vector2D(0.46, 0.46)
            ), 
            False
        )
        self.file_name = ""
        self.hidden = False
        self.hide()

    def set_file_name(self, file_name: str):
        self.file_name = file_name
        if len(file_name) > 45:
            fname = file_name[:45] + "\n" + file_name[45:]
        else:
            fname = file_name
        self.file_text.set_text(fname)

    def on_mouse_release(self, position: Vector2D):
        if self.contains_point(position):
            self.parent.element_click_action(self.file_name)

    def on_cursor_enter(self):
        self.image.set_color(Color("80%", "80%", "80%", "100%"))

    def on_cursor_exit(self):
        self.image.set_color(Color.from_hex("ffffffff"))

    def hide(self):
        if not self.hidden:
            self.hidden = True
            self.unsubscribe()
            self.image.hide()
            self.file_text.hide()

    def show(self):
        if self.hidden:
            self.hidden = False
            self.subscribe()
            self.image.show()
            self.file_text.show()

    def destroy(self):
        self.hide()
        self.image.destroy()

    def set_pos(self, pos: Vector2D):
        super().set_pos(pos)
        self.file_text.set_pos(pos + Vector2D(4.0, 6.0))
