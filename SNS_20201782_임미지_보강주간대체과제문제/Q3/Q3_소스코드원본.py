# Q3. pixabay 사이트의 이미지 다운로드하기
# 특정 키워드 입력하여 이미지 검색 후 컴퓨터의 지정 폴더에 다운로드받기
# pixabay : https://pixabay.com/ko/

# 모듈&라이브러리 로딩
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import urllib.request
import time
import os 

# 검색 키워드와 저장할 사진 갯수 입력
print("=" *80)
query_txt = 'pixabay'
query_keyword = input("검색하고 싶은 이미지의 키워드를 입력하세요. : ")
query_num = int(input("저장할 이미지 수를 입력하세요. : "))
f_dir = input("파일로 저장할 폴더 이름을 쓰세요.(예:c:\\data\\): ")
print("=" *80)

# 저장될 파일위치와 이름을 지정
n = time.localtime()
s = '%04d-%02d-%02d-%02d-%02d-%02d' % (n.tm_year, n.tm_mon, n.tm_mday, n.tm_hour, n.tm_min, n.tm_sec)

save_path = f_dir+s+'-'+query_txt+'-'+query_keyword
os.makedirs(save_path)
os.chdir(save_path)

options = webdriver.ChromeOptions()
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

# 웹 브라우저 실행
s_time = time.time( )
driver = webdriver.Chrome()
driver.implicitly_wait(5)
driver.maximize_window()

driver.get('https://pixabay.com/ko/')
time.sleep(2)

search = driver.find_element(By.NAME, "search")
search.click()
search.send_keys(query_keyword)
search.send_keys(Keys.ENTER)

driver.implicitly_wait(5)

# 자동 스크롤 다운
def scroll_down(driver):
    driver.execute_script("window.scrollTo(0,document.body.scrollHeight);")
    time.sleep(2)

scroll_down(driver) 

img_src2=[]
file_no = 0                                
count = 1

while file_no < query_num:
    scroll_down(driver)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    img_tags = soup.find_all('img')

    for img_tag in img_tags:
        img_src = img_tag.get('src') or img_tag.get('data-src')
        if img_src and img_src not in img_src2:
            img_src2.append(img_src)
            try:
                urllib.request.urlretrieve(img_src, f"{file_no}.jpg")
                file_no += 1
                time.sleep(0.5)
                print(f"{file_no} 번째 이미지 저장중입니다=======")
                if file_no >= query_num:
                    break
            except Exception as e:
                print(f"이미지 저장 중 오류 발생: {e}")
                continue

# 요약 정보 출력             
e_time = time.time( )
t_time = e_time - s_time

store_cnt = file_no -1

print("=" *70)
print("총 소요시간은 %s 초 입니다 " %round(t_time,1))
print("총 저장 건수는 %s 건 입니다 " %file_no)
print("파일 저장 경로: %s 입니다" %save_path)
print("=" *70)

driver.close( )