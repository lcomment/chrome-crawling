import os
from time import sleep

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import ElementNotInteractableException
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup

options = webdriver.ChromeOptions()
options.add_argument('headless')
options.add_argument('lang=ko_KR')
chromedriver_path = "chromedriver"
driver = webdriver.Chrome(os.path.join(os.getcwd(), chromedriver_path), options=options)  # chromedriver 열기


def main():
    global driver

    driver.implicitly_wait(4)  # 렌더링 될 때까지 기다린다 4초
    driver.get('https://map.kakao.com/')  # 주소 가져오기

    search("스타벅스")

    driver.quit()
    print("finish")


def search(place):
    global driver

    search_area = driver.find_element(By.XPATH, '//*[@id="search.keyword.query"]')  # 검색 창
    search_area.send_keys(place)  # 검색어 입력
    driver.find_element(By.XPATH, '//*[@id="search.keyword.submit"]').send_keys(Keys.ENTER)  # Enter로 검색
    sleep(1)

    # 검색된 정보가 있는 경우만 탐색
    # 1번 페이지 place list 읽기
    html = driver.page_source

    soup = BeautifulSoup(html, 'html.parser')
    place_lists = soup.select('.placelist > .PlaceItem')  # 검색된 장소 목록

    # 검색된 첫 페이지 장소 목록 크롤링
    crawling(place_lists)
    search_area.clear()

    try:
        # 장소 더보기
        driver.find_element(By.XPATH, '//*[@id="info.search.place.more"]').send_keys(Keys.ENTER)
        sleep(1)

        # 2~ 5페이지 읽기
        for i in range(2, 6):
            # 페이지 넘기기
            xPath = '//*[@id="info.search.page.no' + str(i) + '"]'
            driver.find_element(By.XPATH, xPath).send_keys(Keys.ENTER)
            sleep(1)

            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            place_lists = soup.select('.placelist > .PlaceItem')  # 장소 목록 list

            crawling(place_lists)

    except ElementNotInteractableException:
        print('not found')
    finally:
        search_area.clear()


def crawling(place_lists):
    for i, place in enumerate(place_lists):
        menu_info = get_menu_board(i, driver)
        print(menu_info)
        # print(i, " ", place, " ", menu_info, "\n")


def get_menu_board(i, driver):
    # 상세페이지로 가서 메뉴 찾기
    detail_page_xpath = '//*[@id="info.search.place.list"]/li[' + str(i + 1) + ']/div[5]/div[4]/a[1]'
    driver.find_element(By.XPATH, detail_page_xpath).send_keys(Keys.ENTER)
    driver.switch_to.window(driver.window_handles[-1])  # 상세정보 탭으로 변환
    sleep(5)

    place_info = []
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    # 이름
    name_include_tag = soup.select('.inner_place > h2.tit_location')
    place_info.append(name_include_tag[0].text)

    # 종류
    kind = soup.select('.inner_place > .location_evaluation > .txt_location')
    category = get_kind(kind)
    place_info.append(category)

    # 주소
    address = soup.select('.placeinfo_default > .location_detail > .txt_address')   # 도로명 주소
    addrnum = soup.select('div.placeinfo_default > .location_detail > .txt_addrnum')  # 지번 주소
    division = parse_address(address, addrnum)
    place_info.append(division)

    driver.close()
    driver.switch_to.window(driver.window_handles[0])  # 검색 탭으로 전환

    return place_info


def get_kind(kind):
    category = ''
    if len(kind) != 0:
        category = kind[0].text.split(' ')[1]
    return category.split(',')


def parse_address(address, addrnum):
    division = []

    if len(address) != 0:
        classification = address[0].text.split('\n')

        for idx, addr in enumerate(classification):
            rm_blank = addr.strip()
            if idx == 0:
                rm_blank = rm_blank.split(' ')

                for city in rm_blank:
                    division.append(city)
            else:
                division.append(rm_blank)

    if len(addrnum) != 0:
        division.append(addrnum[0].text[2:])
    return division


if __name__ == "__main__":
    main()
