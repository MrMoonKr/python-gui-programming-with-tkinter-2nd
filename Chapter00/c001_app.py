import tkinter as tk


class App(tk.Tk):
    
    def __init__(self):
        super().__init__()
        self.title("Tkinter Application ( 애플리케이션 )")
        self.minsize(640, 480)
        self.center_window(800,600)

    def center_window(self, width: int, height: int ):
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        x = int((screen_w-width)/2)
        y = int((screen_h-height)/2)
        self.geometry(f"{width}x{height}+{x}+{y}")


def main():
    app = App()
    app.mainloop()

if __name__ == "__main__":
    main()
    