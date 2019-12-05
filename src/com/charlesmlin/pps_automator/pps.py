import os
import random
from pathlib import Path
from typing import List

from selenium import webdriver

from src.com.charlesmlin.pps_automator.gui_input import TkInput
from src.com.charlesmlin.pps_automator.page_processor import PageProcessor
from src.com.charlesmlin.pps_automator.util import Utils

PPS_WEBLINK = 'https://www.ppshk.com/pps/pps2/revamp2/template/pc/login_c.jsp'
MIN_CENTS = 0
MAX_CENTS = 4
EPSILON = 1e-6

MERCHANT_CODE = 24
AMOUNT_TO_PAY = 100.00


def get_payment_list(amount: float) -> List[float]:
    payment_list = []
    remaining_amount = amount
    payment = -1
    if amount > 3:
        last_random_value = 0
        while remaining_amount > 3:
            random_value = random.randint(MIN_CENTS, MAX_CENTS)
            while random_value == last_random_value:
                random_value = random.randint(MIN_CENTS, MAX_CENTS)
            payment = 1 + random_value / 100
            payment_list.append(round(payment, 2))
            remaining_amount -= payment
            last_random_value = random_value
    if remaining_amount > 2:
        final_payment = round(remaining_amount / 2, 2)
        while abs(payment - final_payment) < EPSILON or abs(remaining_amount - final_payment * 2) < EPSILON:
            final_payment -= 0.01
        payment_list.append(round(final_payment, 2))
        payment_list.append(round(remaining_amount - final_payment, 2))
    elif remaining_amount >= 1:
        payment_list.append(round(remaining_amount, 2))
    return payment_list


def main(weblink: str, user_input: TkInput) -> None:
    payment_list: List[float] = get_payment_list(user_input.get_payment_amount())
    print(f'Amount to pay = {"{:.2f}".format(sum(payment_list))}, payment times = {payment_list.__len__()}')
    print(f'Payment breakdown: {", ".join(map(lambda x: "{:.2f}".format(x), payment_list))}')

    with webdriver.Chrome() as driver:
        driver.get(weblink)
        processor = PageProcessor(driver)
        processor.process_login_page(user_input.get_username(), user_input.get_password())
        for payment in payment_list:
            print(f'Paying Merchant with code {user_input.get_merchant_code()} and amount {payment}')
            processor.process_merchant_list_page(user_input.get_merchant_code())
            processor.process_payment_page(payment)
            processor.process_confirm_payment_page()
            processor.process_pay_another_page()
    print('All Done')


if __name__ == '__main__':
    path: Path = Utils.get_project_path()
    if path is not None:
        os.environ['PATH'] += os.pathsep + str(path.joinpath('libs'))
    tk_input = TkInput()
    tk_input.show_front_end()
    main(PPS_WEBLINK, tk_input)
