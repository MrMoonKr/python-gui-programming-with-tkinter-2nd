import tkinter as tk


def main():
    root = tk.Tk()
    root.title("Tkinter Application")
    root.minsize(640, 480)
    
    def center_window( width: int, height: int ):
        screen_w = root.winfo_screenwidth()
        screen_h = root.winfo_screenheight()
        x = int((screen_w-width)/2)
        y = int((screen_h-height)/2)
        root.geometry(f"{width}x{height}+{x}+{y}")
    
    center_window(800, 600)
    
    root.mainloop()


if __name__ == "__main__":
    main()
    