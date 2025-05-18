from __future__ import annotations
import threading
import tkinter as tk
import customtkinter as ctk


_popup_root: tk.Tk | None = None        
_txt_left:   tk.Text | None = None      
_txt_right:  tk.Text | None = None      
_popup_lock = threading.Lock()          
_pending: list[tuple[str, str]] = []    


def popup(transcript: str, new_qs: str, *, width: int = 950, height: int = 550):

    global _popup_root, _txt_left, _txt_right, _pending

    with _popup_lock:
        if _popup_root is None:

            def _tk_thread():
                global _popup_root, _txt_left, _txt_right

                ctk.set_appearance_mode("light")
                ctk.set_default_color_theme("blue")

                _popup_root = ctk.CTk()
                _popup_root.withdraw()                     

                win = ctk.CTkToplevel(_popup_root)
                win.title("Realtime Virtual Meeting Advisor")
                win.geometry(f"{width}x{height}")
                win.resizable(True, True)
                win.configure(fg_color="#F7F8FA")

                container = ctk.CTkFrame(win, fg_color="#F7F8FA",
                                         corner_radius=0)
                container.pack(fill="both", expand=True, padx=24, pady=24)

                container.grid_columnconfigure(0, weight=2, uniform="cols")
                container.grid_columnconfigure(1, weight=0)
                container.grid_columnconfigure(2, weight=1, uniform="cols")
                container.grid_rowconfigure(1, weight=1)

                header_font = ("Segoe UI Variable", 12)
                modern_font = ("Segoe UI Variable", 12)

                ctk.CTkLabel(container, text="Conversation",
                             font=header_font).grid(
                    row=0, column=0, sticky="w", pady=(0, 8))

                ctk.CTkFrame(container, width=1, fg_color="#E2E6EA").grid(
                    row=1, column=1, sticky="ns", padx=(12, 12))

                ctk.CTkLabel(container, text="Follow-up questions",
                             font=header_font).grid(
                    row=0, column=2, sticky="w", pady=(0, 8))

                _txt_left = ctk.CTkTextbox(
                    container, font=modern_font, wrap="word",
                    state="normal", fg_color="white", text_color="black",
                    border_width=1, border_color="#DDDFE2", corner_radius=6)
                _txt_left.grid(row=1, column=0, sticky="nsew")
                _txt_left.insert("0.0", transcript)
                _txt_left.configure(state="disabled")

                _txt_right = ctk.CTkTextbox(
                    container, font=modern_font, wrap="word",
                    state="normal", fg_color="white", text_color="black",
                    border_width=1, border_color="#DDDFE2", corner_radius=6)
                _txt_right.grid(row=1, column=2, sticky="nsew")
                _txt_right.insert("0.0", new_qs)
                _txt_right.configure(state="disabled")

                for t, q in _pending:
                    _update_ui(t, q)
                _pending.clear()

                _popup_root.mainloop()

            threading.Thread(target=_tk_thread, daemon=True).start()

    def _update_ui(tx: str, qs: str):
        if _txt_left:
            _txt_left.configure(state="normal")
            _txt_left.delete("0.0", "end")
            _txt_left.insert("end", tx)
            _txt_left.configure(state="disabled")
            _txt_left.yview_moveto(1.0)

        if _txt_right:
            _txt_right.configure(state="normal")
            _txt_right.delete("0.0", "end")
            if qs:
                _txt_right.insert("end", qs)
            _txt_right.configure(state="disabled")
            _txt_right.yview_moveto(1.0)

    if _popup_root and _txt_left and _txt_right:
        _popup_root.after(0, _update_ui, transcript, new_qs)
    else:
        _pending.append((transcript, new_qs))