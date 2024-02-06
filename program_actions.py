
import datetime
import os
import random
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException



def get_system_user_agent():
    """시스템의 현재 user-agent를 가져옵니다."""
    temp_driver = webdriver.Chrome()
    temp_driver.get("about:blank")
    user_agent = temp_driver.execute_script("return navigator.userAgent;")
    temp_driver.quit()
    return user_agent


def initialize_driver():
    """user-agent를 사용하여 크롬 드라이버 초기화"""
    user_agent = get_system_user_agent()
    options = Options()
    options.add_argument(f"user-agent={user_agent}")

    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(5)
    return driver

   

def scroll_to_top(driver):
    """브라우저 스크롤을 맨 위로 이동하고 새로운 컨텐츠 로드될 때까지 반복"""
    while True:
        # 현재 스크롤 위치 저장
        current_scroll_position = driver.execute_script("return window.pageYOffset;")
        
        # 스크롤을 맨 위로 이동
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(0.5)  # 짧은 대기 시간

        # 새로운 스크롤 위치 확인
        new_scroll_position = driver.execute_script("return window.pageYOffset;")

        # 스크롤 위치가 변하지 않았다면 중단
        if current_scroll_position == new_scroll_position:
            break        



def find_element_with_retry(driver, by, value, delay=5):
    """요소가 나타날 때까지 찾기"""
    try:
        element = WebDriverWait(driver, delay).until(
            EC.element_to_be_clickable((by, value))
        )
        return element
    except TimeoutException:
        # 요소가 지정된 시간 내에 나타나지 않으면 None 반환하거나 예외 발생
        return None
        # 또는 필요에 따라 예외를 발생시킬 수 있습니다:
        # raise NoSuchElementException(f"요소가 {delay}초 동안 나타나지 않았습니다: {value}")



def save_excel_file(wb, folder_name='실행결과'):
    # 현재 시간을 기준으로 파일 이름 생성
    current_time = datetime.now().strftime('%y%m%d_%H%M')
    file_name = f"{current_time}_실행결과.xlsx"
    # 해당 폴더가 없으면 생성
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    # 파일 저장 경로 설정
    file_path = os.path.join(folder_name, file_name)
    # 엑셀 파일 저장
    wb.save(file_path)
    print(f"\n추출된 정보가 '{folder_name}' 폴더에 '{file_name}' 으로 저장 완료되었습니다.")
    return file_path


# 에러 발생 시 스크린샷을 저장하는 함수
def capture_screenshot(driver, error_message):
    screenshots_dir = "에러 스크린샷"
    if not os.path.exists(screenshots_dir):
        os.makedirs(screenshots_dir)  # 스크린샷을 저장할 폴더가 없으면 생성
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')  # 현재 시간으로 타임스탬프 생성
    screenshot_file = os.path.join(screenshots_dir, f"error_{timestamp}.png")
    driver.save_screenshot(screenshot_file)  # 스크린샷 저장
    print(f"\n에러 스크린샷이 {screenshots_dir} 폴더에 저장되었습니다.")
    print(f"에러 메시지: {error_message}")