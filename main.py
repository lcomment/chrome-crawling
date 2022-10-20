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

    search("무월 강남점")

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

    menu_info = []
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    name_include_tag = soup.select('.inner_place > h2.tit_location')
    print(name_include_tag)
    # 태그 제거 → 이후 라이브러리로 변경 해야 함
    name = ''
    flag = False
    if len(name_include_tag) != 0:
        for c in str(name_include_tag[0]):
            if c == '>':
                flag = True
                continue
            if flag and c == '<':
                break
            if flag:
                name += c

            # print(c, ' ', name)

    menu_info.append(name)



    # 메뉴의 3가지 타입
    # menuonlyType = soup.select('.cont_menu > .list_menu > .menuonly_type')
    # nophotoType = soup.select('.cont_menu > .list_menu > .nophoto_type')
    # photoType = soup.select('.cont_menu > .list_menu > .photo_type')
    #
    # if len(menuonlyType) != 0:
    #     for menu in menuonlyType:
    #         menu_info.append(get_menu_info(menu))
    # if len(nophotoType) != 0:
    #     for menu in nophotoType:
    #         menu_info.append(get_menu_info(menu))
    # if len(photoType) != 0:
    #     for menu in photoType:
    #         menu_info.append(get_menu_info(menu))
    #
    # driver.close()
    # driver.switch_to.window(driver.window_handles[0])  # 검색 탭으로 전환

    return menu_info


def get_menu_info(menu):
    menuName = menu.select('.info_menu > .loss_word')[0].text
    menuPrices = menu.select('.info_menu > .price_menu')
    menuPrice = ''

    if len(menuPrices) != 0:

        menuPrice = menuPrices[0].text.split(' ')[1]

    return [menuName, menuPrice]


if __name__ == "__main__":
    main()