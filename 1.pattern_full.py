import time, random, sys
from pynput import mouse, keyboard
from threading import Thread

sx, sy, st = 0, 0, 0
current_time = time.time() # delay 기록

# 모바일 스크롤 수집
def on_click(x, y, button, pressed):
    global sx, sy, st

    if button == mouse.Button.left:
        print("왼쪽 클릭 : ", pressed, x, y)

        if pressed:
            st = time.time()
            sx = x
            sy = y
        else:
            with open("mobile_scroll.txt", "a") as f:
                rx = x - sx # record
                ry = y - sy
                rt = time.time() - st
                f.write(f"scroll#{rx}#{ry}#{rt}\n")

# PC 스크롤 수집
def on_scroll(x,y,dx, dy):
    global current_time
    print('Scorll했음 {0} at {1}'.format('down' if dy < 0 else 'up', (x,y) ))
    print(dx, dy)
    delay_time = time.time() - current_time
    current_time = time.time()
    with open("./pc_scroll.txt", "a") as f:
        f.write(f"scroll#{dx}#{dy}#{delay_time}\n")


# 종료 이벤트 처리
def on_release(key):
    if key == keyboard.Key.esc:
        # 사용자가 esc를 누르면 리스너를 중지시킵니다.
        return False

def main():
    # 마우스 리스너 스레드
    mouse_listener = mouse.Listener(on_click=on_click, on_scroll=on_scroll)
    mouse_listener.start()

    # 키보드 리스너 스레드
    with keyboard.Listener(on_release=on_release) as keyboard_listener:
        keyboard_listener.join()

    # 사용자가 esc를 누르면 마우스 리스너도 중지합니다.
    mouse_listener.stop()
    print('녹화가 종료됐습니다')

mainThread = Thread(target=main)
mainThread.start()