from user_agents import parse
import datetime, os, pickle, random, time
import undetected_chromedriver as uc
from openpyxl import Workbook
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from mutil import random_move

def scroll_to_top(driver, isMobile=True):
    """브라우저 스크롤을 자연스럽게 맨 위로 이동"""
    while True:
        # 현재 스크롤 위치 저장
        current_scroll_position = driver.execute_script("return window.pageYOffset;")
        
        if current_scroll_position <= 0:
            break  # 이미 최상단에 도달한 경우 루프 중단

        random_move(driver, direction="up", count=1, isMobile=True)

        new_scroll_position = driver.execute_script("return window.pageYOffset;")

        if current_scroll_position == new_scroll_position:
            break   

def element_random_click(driver,element):
    el_width, el_height = element.size['width'], element.size['height']
    targetX = random.randint( -int(el_width * 0.4), int(el_width*0.4) )
    targetY = random.randint( -int(el_height *0.4), int(el_height*0.4))

    ActionChains(driver).move_to_element(element).pause(2).move_by_offset(targetX,targetY).click().perform()

def random_click(driver, css_selector):
    element = driver.find_element(By.CSS_SELECTOR, css_selector)
    el_width, el_height = element.size['width'], element.size['height']
    targetX = random.randint(-int(el_width(*0.40), int(el_width*0.40)))
    targetY = random.randint(-int(el_height(*0.40), int(el_height*0.40)))
    
    ActionChains(driver).move_to_element(element)\
        .pause(1).move_by_offset(targetX, targetY).clcik().perform()


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

# 엑셀 초기화 및 헤더 작성
def initialize_excel():
    wb = Workbook()
    ws = wb.active
    headers = ['제목', '작성일자', '닉네임', '전화번호', '블로그주소', '일방문자', '전체방문자', '이미지개수', '글자수', '이메일주소']
    ws.append(headers)
    return wb, ws

# 엑셀에 데이터 저장
def write_to_excel(ws, data):
    ws.append(data)

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
    driver.save_screenshot(screenshot_file)  # 스크린샷 저장s
    print(f"\n에러 스크린샷이 {screenshots_dir} 폴더에 저장되었습니다.")
    print(f"에러 메시지: {error_message}")

def load_cookies(driver):
    if os.path.exists('cookies.pkl'):
        with open('cookies.pkl', 'rb') as file:
            cookies, saved_domain = pickle.load(file)
        driver.get(saved_domain)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
        for cookie in cookies:
            driver.add_cookie(cookie)
        driver.refresh()
        return True  # 쿠키 로드 및 페이지 이동 성공
    return False  # 쿠키 파일 없음


def save_cookies(driver):
    cookies = driver.get_cookies()
    current_domain = driver.current_url
    with open('cookies.pkl', 'wb') as file:
        pickle.dump((cookies, current_domain), file)

