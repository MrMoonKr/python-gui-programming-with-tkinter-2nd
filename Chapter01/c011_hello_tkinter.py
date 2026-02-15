import tkinter as tk


def main():
    root = tk.Tk()
    #root.minsize(480, 320)
    
    label = tk.Label(root, text="Hello World 안녕하세요 !!!") # 버튼 생성
    label.pack() # 버튼 배치
    
    root.mainloop()


if __name__ == "__main__":
    main()
    