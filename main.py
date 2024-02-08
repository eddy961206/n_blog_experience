from program_actions import initialize_driver, initialize_excel, load_cookies, save_cookies, save_excel_file, scroll_to_top, write_to_excel
from naver_utils import (extract_comment_info, is_logged_in, login_to_naver, 
                         navigate_to_comment_page, scrape_my_blog_details,
                         logout_of_naver)

# 메인 로직 함수
def main_logic(id, pw):
    
    try:
            
        print('\n\n===============  프로그램 작동중.... ===============')
        print('\n\n=== 화면은 가려져도 되지만 크롬 창 최소화는 하지 말아주세요 ===')

        # 웹드라이버 초기화
        driver = initialize_driver()

        # 쿠키 로드 시도 및 결과 확인
        cookies_loaded = load_cookies(driver)

        # 쿠키 로드 성공 및 페이지 접근 시에만 로그인 상태 확인
        if cookies_loaded and not is_logged_in(driver):
            if not login_to_naver(driver, id, pw):
                print(f"\n계정 {id}으로 로그인에 실패했습니다.")
                return
            else:
                print(f"\n계정 {id}으로 로그인 하였습니다.")
                # 새로운 쿠키 저장
                save_cookies(driver)
        elif not cookies_loaded:
            # 쿠키 로드에 실패했거나 파일이 없는 경우, 직접 로그인 시도
            if login_to_naver(driver, id, pw):
                print(f"\n계정 {id}으로 로그인 하였습니다.")
                save_cookies(driver)
            else:
                print(f"\n계정 {id}으로 로그인에 실패했습니다.")
                return

        # # 로그인
        # if not login_to_naver(driver, id, pw):
        #     print(f"\n계정 {id}으로 로그인에 실패했습니다.")
        #     return
        # else :
        #     print(f"\n계정 {id}으로 로그인 하였습니다.")


        blog_posts = scrape_my_blog_details(driver)

        if not blog_posts:
            print("블로그 글이 없습니다.")
            return

        # 엑셀 파일 초기화
        wb, ws = initialize_excel()

        # 추출한 블로그 글들을 반복하여 돌면서 정보 수집
        for post in blog_posts:
            navigate_to_comment_page(driver, post['url'])
            scroll_to_top(driver)
            comments_infos = extract_comment_info(driver)

            if not comments_infos:
                print(f"댓글이 없는 포스트: {post['url']} - 다음 포스트로 넘어갑니다.")
                continue
            
            # 엑셀 시트에 데이터 작성
            for info in comments_infos:
                data = [
                    post['title'],
                    post['date'],
                    info['nickname'],
                    info['phone_no'],
                    info['blog_link'],
                    info['today_visitor_count'],
                    info['total_visitor_count'],
                    info['photo_count'],
                    info['character_count'],
                    info['email']
                ]

                print(data)
                write_to_excel(ws, data)

         # 로그아웃
        logout_of_naver(driver)

        # 엑셀 파일 저장
        save_excel_file(wb)
        
        print('===== ***** ===== *****  ===== ***** ===== *****')
        print('\n체험단 댓글 정보 추출 프로그램 실행이 모두 완료되었습니다.')
                
        driver.quit()

    except Exception as e:
        print(f"\n\n**** 프로그램 실행 오류 : {e}\n"
              "\n프로그램이 예기치 못하게 중단 되었습니다.")
        input()


    
   

