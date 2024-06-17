# Q1. 나라장터 - 대한민국 조달청에서 운영하는 나라장터 사이트에서 공고명과 기간을 입력하여
# 결과를 검색한 후 다양한 형식의 파일(txt, xls)로 저장하는 크롤러 만들기
# 나라장터 : https://www.g2b.go.kr/index.jsp

# 모듈&라이브러리 로딩
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import pandas as pd 
import requests
import numpy  
import time
import os  

# 공고명과 기간 입력
print("=" *80)
query_txt = '나라장터'
query_keyword = input("공고명으로 검색할 키워드는 무엇입니까? : ")
query_startTime = input("조회 시작일자를 입력해주세요.(ex. 2019/01/01) : ")
query_endTime = input("조회 종료일자를 입력해주세요.(ex. 2019/03/31) : ")
f_dir = input("파일로 저장할 폴더 이름을 쓰세요.(예:c:\\data\\): ")
print("=" *80)


# 저장될 파일위치와 이름을 지정
n = time.localtime()
s = '%04d-%02d-%02d-%02d-%02d-%02d' % (n.tm_year, n.tm_mon, n.tm_mday, n.tm_hour, n.tm_min, n.tm_sec)

save_path = f_dir+s+'-'+query_txt
os.makedirs(save_path)
os.chdir(save_path)

ff_name=save_path+'\\'+s+'-'+query_txt+'.txt'
fc_name=save_path+'\\'+s+'-'+query_txt+'.csv'
fx_name=save_path+'\\'+s+'-'+query_txt+'.xlsx'

# 웹 브라우저 실행
s_time = time.time( )
driver = webdriver.Chrome()

driver.implicitly_wait(5)
driver.maximize_window()

driver.get('https://www.g2b.go.kr/index.jsp')

time.sleep(2)

# 나라장터 페이지에 방문하면 정기점검 작업 안내 팝업창이 뜨므로 해당 팝업을 닫는 단계 추가함
# 현재 열려 있는 창의 수를 출력
print("Number of open windows before:", len(driver.window_handles))

# 첫 번째 창만 남기고 모두 닫기
for handle in driver.window_handles[1:]:
    driver.switch_to.window(handle)
    driver.close()

driver.switch_to.window(driver.window_handles[0])

# 열려 있는 창의 수 확인
print("Number of open windows after:", len(driver.window_handles))
assert len(driver.window_handles) == 1

time.sleep(2)

# 사용자가 입력한 공고명과 기간 입력 후 검색
search_k = driver.find_element(By.ID, "bidNm")
search_k.click()
search_k.send_keys(query_keyword)
search_s = driver.find_element(By.ID, "fromBidDt")
search_s.click()
search_s.send_keys(query_startTime)
search_e = driver.find_element(By.ID, "toBidDt")
search_e.click()
search_e.send_keys(query_endTime)
search = driver.find_element(By.CSS_SELECTOR, ".btn_dark")
search.send_keys(Keys.ENTER)

driver.implicitly_wait(5)

# 상세내용 추출하기
url = driver.page_source    # 페이지 소스 가져오기
soup = BeautifulSoup(url, 'html.parser')    # BeautifulSoup으로 페이지 소스 파싱

# 테이블에서 데이터 추출
table = soup.find("table")
if table:
    headers = [th.text.strip() for th in table.find_all('thead > tr > th')]
    rows = []
    for tr in table.find('tbody').find_all('tr'):
        row = [td.text.strip() for td in tr.find_all('td')]
        rows.append(row)
    print(rows)

    # 결과를 저장할 리스트 초기화
    results = []

    # 공고 목록을 반복하면서 데이터 추출
    for i, item in enumerate(table.find_all('tr')):
        columns = item.find_all('td')
        if len(columns) > 0:
            result = {
                '업무': columns[0].text,
                '공고번호-차수': columns[1].text,
                '분류': columns[2].text,
                '공고명': columns[3].text,
                'URL 주소': columns[3].find('a')['href'] if columns[3].find('a') else '',
                '공고기관': columns[4].text,
                '수요기관': columns[5].text,
                '계약방법': columns[6].text,
                '입력일시(입찰마감일시)': columns[7].text,
                '공동수급': columns[8].text,
                '투찰여부': columns[9].text
            }
            results.append(result)
            
            # 추출한 내용 출력
            print(f"==== {i}번째 공고 내용을 추출합니다. ====")
            print(f"1. 업무 : {result['업무']}")
            print(f"2. 공고번호-차수 : {result['공고번호-차수']}")
            print(f"3. 분류 : {result['분류']}")
            print(f"4. 공고명 : {result['공고명']}")
            print(f"5. URL 주소 : {result['URL 주소']}")
            print(f"6. 공고기관 : {result['공고기관']}")
            print(f"7. 수요기관 : {result['수요기관']}")
            print(f"8. 계약방법 : {result['계약방법']}")
            print(f"9. 입력일시 : {result['입력일시(입찰마감일시)']}")
            print(f"10. 공동수급 : {result['공동수급']}")
            print(f"11. 투찰여부 : {result['투찰여부']}")
            print("\n")

    # results 리스트가 비어있으면 오류가 발생할 수 있으므로 데이터가 제대로 추가되었는지 확인 필요
    if not results:
        print("추출된 데이터가 없습니다.")
    else:
        # DataFrame으로 변환
        df = pd.DataFrame(results)
        df.index = range(len(df))
        categories = ['업무', '공고번호-차수', '분류', '공고명', '공고기관', '수요기관', '계약방법', '입력일시(입찰마감일시)', '공동수급', '투찰']
        df.columns = categories
        
        # 파일로 저장
        df.to_csv(ff_name, encoding="utf-8-sig", sep='\t', index=False)   # txt 파일로 저장
        df.to_csv(fc_name, encoding="utf-8-sig", index=False)             # csv 파일로 저장
        df.to_excel(fx_name, index=False)                                 # xlsx 파일로 저장
else:
    print("테이블을 찾을 수 없습니다.")

# 웹 드라이버 종료
e_time = time.time()
t_time = e_time - s_time
driver.quit()

# 요약정보 보여주기
print("크롤링이 완료되었습니다.")
print("\n") 
print("=" * 80)
print("총 소요시간은 %s 초 입니다 " % round(t_time, 1))
print("파일 저장 완료: txt 파일명 : %s " % ff_name)
print("파일 저장 완료: csv 파일명 : %s " % fc_name)
print("파일 저장 완료: xls 파일명 : %s " % fx_name)
print("=" * 80)
