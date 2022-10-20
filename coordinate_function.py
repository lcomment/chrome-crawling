from time import sleep

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup


def get_coordinate(i, driver, address):
    driver.implicitly_wait(4)  # 렌더링 될 때까지 기다린다 4초
    driver.execute_script('window.open("https://address.dawul.co.kr/");')
    driver.switch_to.window(driver.window_handles[2])

    search_area = driver.find_element(By.XPATH, '//*[@id="input_juso"]')  # 검색 창
    search_area.send_keys(address)  # 검색어 입력
    driver.find_element(By.XPATH, '//*[@id="btnSch"]').click()  # Enter로 검색
    sleep(1)

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    coordinate = soup.select('#insert_data_5')

    if len(coordinate) != 0:
        xy = coordinate[0].text.split(', ')
        xy[0] = xy[0][3:]
        xy[1] = xy[1][3:]

    driver.close()
    driver.switch_to.window(driver.window_handles[1])  # 검색 탭으로 전환

    return xy
