from program_actions import initialize_driver, save_excel_file, scroll_to_top
from naver_utils import (extract_comment_info, initialize_excel, login_to_naver, 
                         navigate_to_comment_page, scrape_my_blog_details,
                         logout_of_naver, write_to_excel)

# 메인 로직 함수
def main_logic(id, pw):
    
    try:
            
        print('\n\n===============  프로그램 작동중.... ===============')
        print('\n\n=== 화면은 가려져도 되지만 크롬 창 최소화는 하지 말아주세요 ===')

        # 웹드라이버 초기화
        driver = initialize_driver()

        # 로그인
        if not login_to_naver(driver, id, pw):
            print(f"\n계정 {id}으로 로그인에 실패했습니다.")
            return
        else :
            print(f"\n계정 {id}으로 로그인 하였습니다.")


        blog_posts = scrape_my_blog_details(driver)

        # 엑셀 파일 초기화
        wb, ws = initialize_excel()

        # 추출한 블로그 글들을 반복하여 돌면서 정보 수집
        for post in blog_posts:
            navigate_to_comment_page(driver, post['url'])
            scroll_to_top(driver)
            comments_infos = extract_comment_info(driver)
            
            # 엑셀 시트에 데이터 작성
            for info in comments_infos:
                data = [
                    post['title'],
                    post['date'],
                    info['nickname'],
                    info['blog_link'],
                    info['today_visitor_count'],
                    info['total_visitor_count'],
                    info['photo_count'],
                    info['character_count'],
                    info['email']
                ]
                write_to_excel(ws, data)

         # 로그아웃
        logout_of_naver(driver)

        # 엑셀 파일 저장
        save_excel_file(wb)
        
        print('===== ***** ===== *****  ===== ***** ===== *****')
        print('\n댓글 달기 및 좋아요 누르기 프로그램 실행이 모두 완료되었습니다.')
                
        driver.quit()

    except Exception as e:
        print(f"\n\n**** 프로그램 실행 오류 : {e}\n"
              "\n프로그램이 예기치 못하게 중단 되었습니다.")
        input()


    
   


