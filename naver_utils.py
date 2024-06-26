import random
import re
import pyperclip
import time
from bs4 import BeautifulSoup
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (NoSuchElementException, TimeoutException,
                                        ElementClickInterceptedException, StaleElementReferenceException,
                                        )
from program_actions import find_element_with_retry
from bs4 import BeautifulSoup
from mutil import element_random_click, random_wait, random_click, random_move, scroll_to_element


def is_logged_in(driver):
    try:
        WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.XPATH, "//button[contains(text(), '로그아웃')]")))
        logout_button = driver.find_elements(By.XPATH, "//button[contains(text(), '로그아웃')]")
        
        if logout_button:
            return True
    except Exception as e:
        return False

    return False


def login_to_naver(driver, username, password):
    driver.get("https://nid.naver.com/nidlogin.login?mode=form&url=https://www.naver.com")
    driver.get("https://nid.naver.com/nidlogin.login?mode=form&url=https://nid.naver.com/user2/help/myInfoV2?lang=ko_KR")
    try:
        username_input = find_element_with_retry(driver, By.CSS_SELECTOR, "#id")
        username_input.click()
        pyperclip.copy(username)
        ActionChains(driver).key_down(Keys.CONTROL).send_keys("v").key_up(Keys.CONTROL).perform()
        
        password_input = find_element_with_retry(driver, By.CSS_SELECTOR, "#pw")
        password_input.click()
        pyperclip.copy(password)
        ActionChains(driver).key_down(Keys.CONTROL).send_keys("v").key_up(Keys.CONTROL).perform()
        
        login_button = find_element_with_retry(driver, By.CSS_SELECTOR, "#log\\.login")
        if login_button:
            login_button.click()
                
        return True
    except NoSuchElementException:
        print("\n\n로그인 버튼을 찾을 수 없습니다.")
        return False
    except TimeoutException:
        print("\n\n로그인 페이지가 로드되는데 시간이 너무 오래 걸립니다.")
        return False
    except Exception as e:
        print(f"\n\n로그인 시도중 오류 발생 : {e}")
        return False



def scrape_my_blog_details(driver):

    driver.get("https://m.blog.naver.com/sjhyo7400?categoryNo=7&tab=1")
    # driver.get("https://m.blog.naver.com/skykum2004?categoryNo=24&tab=1")
    # driver.get("https://m.blog.naver.com/skykum2004?categoryNo=23&tab=1")

    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        # random_move(driver, direction="down", count=10, isMobile=True)

        try:
            # 새로운 콘텐츠가 로드될 때까지 기다리기
            WebDriverWait(driver, 10).until(lambda d: d.execute_script("return document.body.scrollHeight") > last_height)
            new_height = driver.execute_script("return document.body.scrollHeight")
            last_height = new_height
        except TimeoutException:
            # 더 이상 새로운 콘텐츠가 없는 경우
            break

    blog_posts = []

    # 블로그 포스트의 최상위 요소인 'card__WjujK' 클래스를 가진 div들을 모두 찾습니다.
    cards = driver.find_elements(By.CSS_SELECTOR, "div.card__WjujK")
    for card in cards:
        try:
            # 각 카드 안에서 댓글 아이콘 다음에 나오는 텍스트 노드를 찾습니다.
            # 댓글 개수가 포함된 요소의 부모를 찾기 위한 XPath
            parent_xpath = ".//i[contains(@class, 'icon_comment__mDZGi')]/.."
            # 해당 XPath를 사용하여 부모 요소 찾기
            parent_element = card.find_element(By.XPATH, parent_xpath)
            # 부모 요소의 전체 텍스트를 가져오고, 숫자만 추출하기
            full_text = parent_element.text
            comment_count = ''.join(filter(str.isdigit, full_text))

        except NoSuchElementException:
            pass

        try:
            # 각 카드 안에서 포스트의 제목과 관련된 요소를 찾습니다.
            title_element = card.find_element(By.CSS_SELECTOR, "strong.title__tl7L1 span")
            title = title_element.text
            # 각 카드 안에서 포스트의 URL을 찾습니다.
            post_link_element = card.find_element(By.CSS_SELECTOR, "a.link__iGhdI")
            post_url = post_link_element.get_attribute('href')
            # 포스트의 작성 날짜를 찾습니다.
            post_date_element = card.find_element(By.XPATH, ".//ancestor::div[3]/descendant::span[contains(@class, 'time__MHDWV')]")
            post_date = post_date_element.text if post_date_element else "날짜 못찾음"
        except NoSuchElementException:
            print(f"'{title if 'title' in locals() else '알 수 없는'}' 포스트는 필요한 요소가 없어 건너뜁니다.")
            continue
        
        if comment_count == '0':
            print(f"'{title}' 포스트는 댓글이 없어 건너뜁니다.")
            continue

        blog_posts.append({
            'url': post_url,
            'title': title,
            'date': post_date
        })


    print(f"가져온 URL 개수 : {len(cards)}")
    print('-----------------------------------------------')
    return blog_posts



def navigate_to_comment_page(driver, link):
    """블로그 글의 댓글 페이지로 이동"""
    try:
        
        url_parts = link.split('&')  # https://m.blog.naver.com/PostView.naver?blogId=u_many_yeon&logNo=223316337997&navType=by -> https://m.blog.naver.com/CommentList.naver?blogId=u_many_yeon&logNo=223316337997
        comment_page_link = link.replace("PostView.naver", "CommentList.naver").split('&')[0] + '&' + url_parts[1]
        print(f'댓글 페이지 : {comment_page_link}')
        # driver.get(comment_page_link)

        driver.get(link) # 댓글 페이지가 아닌 블로그 글로 일단 이동
        
        random_wait()
                
        댓글창_selector = "#ct > div._postView > div.section_t1 > div > div > a.btn_reply"
        try:
            scroll_to_element(driver, element_selector=댓글창_selector)
            random_click(driver,css_selector=댓글창_selector)
        except:
            print("댓글창 버튼을 클릭하지 못했습니다.")

        # 댓글 입력창이 로드될 때까지 최대 10초 대기
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".u_cbox_inbox"))
        )

        random_wait()
        
        return True
    except Exception as e:
        print(f"댓글 페이지로 이동하는 도중 오류가 발생했습니다: {e}")
        return False


def extract_comment_info(driver):
    # 댓글 정보 추출 로직
    comments_infos = []
    no_phone_comment_cnt = 0
    
    try:
        WebDriverWait(driver, 2).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".u_cbox_area")))
        comments = driver.find_elements(By.CSS_SELECTOR, ".u_cbox_area")
        print(f"댓글 개수 : {len(comments)}")
    except TimeoutException:
        print("댓글이 없습니다.")
        return comments_infos
    
    # 댓글 데이터를 먼저 모두 수집
    # comment_data_list = []
    for comment in comments:
        try:
            comment_content = comment.find_element(By.CSS_SELECTOR, ".u_cbox_contents").text
            phone_no = extract_phone_number(comment_content)
            if phone_no == '전화번호가 없습니다' : 
                no_phone_comment_cnt += 1
                print('전화번호가 없는 댓글은 정보를 수집하지 않고 다음 댓글로 넘어갑니다..')
                continue
            nickname = comment.find_element(By.CSS_SELECTOR, ".u_cbox_nick").text
            print(f"전화번호 있는 댓글 개수 : {len(comments) - no_phone_comment_cnt}")

            # # 댓글 작성자의 블로그 링크 추출
            blog_link_element = comment.find_element(By.CSS_SELECTOR, ".u_cbox_name")
            blog_link = blog_link_element.get_attribute("href") if blog_link_element else None

            # 댓글 단 사람의 블로그 방문해서 데이터 추출        
            # 해당 댓글로 이동
            scroll_to_element(driver, element=blog_link_element)
            # 댓글 작성자의 블로그 링크 클릭
            element_random_click(driver, element=blog_link_element)
            # 페이지 로드 대기
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "body")))
            bloggers_info = extract_bloggers_info(driver, blog_link)

            # 댓글 페이지가 다시  로드될 때까지
            WebDriverWait(driver, 4).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".u_cbox_area")))
            
            # 추출한 데이터를 리스트에 추가
            comments_infos.append({
                'nickname': nickname,
                'comment_content': comment_content,
                'phone_no': phone_no,
                'blog_link': blog_link,
                'email': blog_link.split('blogId=')[1] + "@naver.com",
                **bloggers_info
            })

        except StaleElementReferenceException:
            # 요소가 더 이상 현재 페이지에 존재하지 않는 경우
            print("요소가 더 이상 존재하지 않습니다.")
    
    return comments_infos


def extract_phone_number(comment_content):
    # '010'으로 시작하며, 하이픈(-) 또는 공백( )이 포함될 수도 있고, 그 다음에 숫자 4개, 다시 하이픈(-) 또는 공백( ), 마지막으로 숫자 4개가 이어지는 패턴 정의
    phone_pattern = re.compile(r'010[- ]?\d{4}[- ]?\d{4}')
    
    # 전화번호 찾기
    phone_match = phone_pattern.search(comment_content)
    
    # 전화번호가 있다면 추출하고 포매팅
    if phone_match:
        phone_no = phone_match.group()
        # 하이픈과 공백 제거
        phone_no = re.sub(r'[- ]', '', phone_no)
        # 포매팅: 010-xxxx-xxxx
        phone_no = f"{phone_no[:3]}-{phone_no[3:7]}-{phone_no[7:]}"
        return phone_no
    else:
        return '전화번호가 없습니다'

def extract_bloggers_info(driver, blog_link):
    try:
        # driver.get(blog_link)
        print(f'방문 블로그 링크 : {blog_link}')
        
        random_wait() # 랜덤 대기

        try:
            WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.XPATH, "//i[contains(text(), '목록형 보기')]")))
            random_wait()
            list_view_button = driver.find_element(By.XPATH, "//i[contains(text(), '목록형 보기')]")

            try:
                scroll_to_element(driver, element=list_view_button)
                # 리스트 뷰 버튼 클릭
                element_random_click(driver, list_view_button)
            except (StaleElementReferenceException, NoSuchElementException):
                # 목록형 보기 버튼이 없거나 찾을 수 없는 경우
                print("목록형 보기 버튼이 없습니다.")
        except TimeoutException:
            # WebDriverWait 동안 "목록형 보기" 버튼이 나타나지 않는 경우
            print("블로그에 게시글이 없습니다.")

        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.count__LOiMv')))
        visitor_count_element = driver.find_element(By.CSS_SELECTOR, '.count__LOiMv')
        visitor_count_text = visitor_count_element.text
        today_visitor_count, total_visitor_count = re.findall(r'\d+', visitor_count_text.replace(',', ''))

        try:
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-ui-name="list"] > ul > li:nth-of-type(1)')))
            first_post = driver.find_element(By.CSS_SELECTOR, 'div[data-ui-name="list"] > ul > li:nth-of-type(1)')

            try:
                photo_count_element = first_post.find_element(By.XPATH, ".//span[.//span[contains(text(), '사진 개수')]]")
                photo_count = extract_number_of_photos(photo_count_element)
            except NoSuchElementException:
                # 사진 개수 요소가 없는 경우, 즉 사진이 없는 경우
                photo_count = '0'

            character_count = blog_content_character_count(driver, first_post)
        except TimeoutException:
            # 글이 없는 경우
            photo_count = '0'
            character_count = '0'

        # 뒤로가기 (댓글 페이지로)
        driver.execute_script("window.history.back();")

        return {
            'photo_count': photo_count,
            'character_count': character_count,
            'today_visitor_count': today_visitor_count,
            'total_visitor_count': total_visitor_count
        }
    except TimeoutException as e:
        print(f"요소의 존재를 기다리는 동안 시간이 초과되었습니다: {e}")
        return {}
    except Exception as e:
        print(f"오류가 발생했습니다: {e}")
        return {}



def extract_number_of_photos(photo_count_element):
    # 'photo_count_element'의 전체 텍스트에서 숫자만 추출
    photo_count_text = photo_count_element.text
    # 정규 표현식으로 숫자를 찾음
    matches = re.findall(r'\d+', photo_count_text)
    return matches[0] if matches else '0'  # 숫자가 있다면 첫 번째 매치를 반환, 없다면 '0'을 반환

 

def blog_content_character_count(driver, first_post_element):

    first_post_link = first_post_element.find_element(By.TAG_NAME, 'a').get_attribute('href')
    
    # 블로그 첫번째 게시글로 이동
    # driver.get(first_post_link)
    scroll_to_element(driver, element=first_post_element)
    element_random_click(driver, first_post_element)

    # 랜덤 스크롤
    random_move(driver, direction="down", count=5)

    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')
    blog_content_div = soup.find("div", class_="se-main-container")
    if not blog_content_div:
        return "블로그 본문 요소를 찾을 수 없습니다."
    
    blog_content = ''
    for element in blog_content_div.descendants:
        if element.name == 'span':
            if element.string:
                blog_content += element.string.strip() + ' '
    
    character_count = len(blog_content.replace(' ', ''))
    
    if not character_count:
        return "블로그 본문에 글자가 없습니다."
    
    # 뒤로가기 (댓글 단 블로거의 블로그 메인으로)
    driver.execute_script("window.history.back();")
    
    return character_count



def logout_of_naver(driver):
    """Logs out of Naver."""
    try:
        driver.get("https://www.naver.com/")
        logout_button = find_element_with_retry(driver, By.CSS_SELECTOR, ".MyView-module__btn_logout___bsTOJ")
        time.sleep(0.3)
        logout_button.click()
    except NoSuchElementException:
        print("로그아웃 버튼을 찾을 수 없습니다.")
    except ElementClickInterceptedException:
        print("로그아웃 버튼을 클릭할 수 없습니다.")


