import streamlit as st
import httpx
import asyncio
from datetime import datetime
from httpx import HTTPStatusError
from jose import JWTError
from streamlit_cookies_controller import CookieController


BASE_URL = "http://127.0.0.1:8000"
controller = CookieController()
ROLES = ["Спортсмен", "Тренер"]


async def get_current_role():
    url = f"{BASE_URL}/auth/me/"
    async with httpx.AsyncClient() as client:
        response = await client.get(url, cookies={"users_access_token": controller.get("users_access_token")})
        data = response.json()
        return data['role']

async def token_is_correct():
    url = f"{BASE_URL}/auth/token_correct/"
    async with httpx.AsyncClient() as client:
        try:
            await client.get(url, cookies={"users_access_token": controller.get("users_access_token")})
            return True
        except JWTError:
            return False

async def athlete_profile():
    st.header("Личный кабинет спортсмена")
    st.divider()
    url = f"{BASE_URL}/auth/me/"
    async with httpx.AsyncClient() as client:
        response = await client.get(url, cookies={"users_access_token": controller.get("users_access_token")})
        if response.status_code == 200:
            data = response.json()
            new_data = {
                "Ваше имя": data.get('first_name'),
                "Ваша фамилия": data.get('last_name'),
                "Номер телефона": data.get('phone_number'),
            }
            st.write("Ваши данные:")
            st.dataframe(new_data)
        else:
            st.error(f"Ошибка: {response.status_code}, {response.text}")
    st.divider()


    # Получение дополнительной информации
    additional_info_url = f"{BASE_URL}/athletes/additional_info/{data.get('id')}/"  # data['id'] — id спортсмена
    async with httpx.AsyncClient() as client:
        additional_response = await client.get(additional_info_url,
                                               cookies={"users_access_token": controller.get("users_access_token")})
        if additional_response.status_code == 200:
            additional_data = additional_response.json()
            athlete_id = additional_data.get("athlete_id")
            age = additional_data.get("age")
            weight = additional_data.get("weight")
            height = additional_data.get("height")
        else:
            st.error(f"Ошибка при загрузке дополнительных данных: {additional_response.status_code}, {additional_response.text}")
            return

    # Форма для редактирования данных
    st.write("Дополнительные данные:")
    age_input = st.number_input("Возраст", value=age if age else 0, min_value=0, step=1)
    weight_input = st.number_input("Вес (кг)", value=weight if weight else 0, min_value=0, step=1)
    height_input = st.number_input("Рост (см)", value=height if height else 0, min_value=0, step=1)

    if st.button("Сохранить дополнительные данные"):
        update_url = f"{BASE_URL}/athletes/additional_info/"
        payload = {
            "athleteId": athlete_id,  # ID спортсмена
            "age": age_input,
            "weight": weight_input,
            "height": height_input,
        }
        async with httpx.AsyncClient() as client:
            update_response = await client.post(update_url, json=payload,
                                                cookies={"users_access_token": controller.get("users_access_token")})
            if update_response.status_code == 200:
                st.success("Данные успешно обновлены!")
            else:
                st.error(f"Ошибка обновления данных: {update_response.status_code}, {update_response.text}")

    st.divider()


    url = f"{BASE_URL}/athletes/athlete/"
    async with httpx.AsyncClient() as client:
        response = await client.get(url, cookies={"users_access_token": controller.get("users_access_token")})
        if response.status_code == 200:
            athlete_data = response.json()
        else:
            st.error(f"Ошибка при загрузке тренеров: {response.status_code}, {response.text}")
            return

    if athlete_data.get('trainerId') is None:
        # Получение списка тренеров
        url = f"{BASE_URL}/trainers/all_trainers/"
        async with httpx.AsyncClient() as client:
            trainer_response = await client.get(url,
                                              cookies={"users_access_token": controller.get("users_access_token")})
            if trainer_response.status_code == 200:
                coaches_data = trainer_response.json()
                coach_options = {f"{coach['first_name']} {coach['last_name']}": coach['id'] for coach in coaches_data}
            else:
                st.error(f"Ошибка при загрузке тренеров: {trainer_response.status_code}, {trainer_response.text}")
                return
        # Выбор тренера
        st.write("Выберите тренера для подписки:")
        selected_coach = st.selectbox("Тренеры", list(coach_options.keys()))
        # Подписка на тренера
        if st.button("Подписаться"):
            selected_coach_id = coach_options[selected_coach]
            subscribe_url = f"{BASE_URL}/athletes/subscribe/{selected_coach_id}/"
            async with httpx.AsyncClient() as client:
                subscribe_response = await client.post(subscribe_url, cookies={
                    "users_access_token": controller.get("users_access_token")})
                if subscribe_response.status_code == 200:
                    st.success("Вы успешно подписались на тренера!")
                else:
                    st.error(f"Ошибка подписки: {subscribe_response.status_code}, {subscribe_response.text}")
    else:
        url = f"{BASE_URL}/trainers/user_info_by_trainer_id/{athlete_data.get('trainerId')}/"
        async with httpx.AsyncClient() as client:
            response = await client.get(url, cookies={"users_access_token": controller.get("users_access_token")})
            if response.status_code == 200:
                user_data = response.json()
            else:
                st.error(f"Ошибка при загрузке данных пользователя: {response.status_code}, {response.text}")
                return
        st.write(f"Вы уже подписаны на тренера, ваш тренер: {user_data['first_name']} {user_data['last_name']}")
    st.divider()

    # Получение списка планов
    st.write("Ваши тренировочные планы:")
    plans_url = f"{BASE_URL}/athletes/my_plans/"
    async with httpx.AsyncClient() as client:
        plans_response = await client.get(plans_url, cookies={"users_access_token": controller.get("users_access_token")})
        if plans_response.status_code == 200:
            plans_data = plans_response.json()
            if not plans_data:
                st.info("У вас пока нет доступных планов.")
            else:
                # Отображение списка планов
                plan_options = {
                    f"План, выданный: {datetime.fromisoformat(plan['created_at']).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}":
                        (plan['data'], int(plan['id']))
                    for plan in plans_data
                }
                selected_plan = st.selectbox("Выберите план для просмотра:", list(plan_options.keys()))
                st.divider()
                # Отображение содержимого плана
                if selected_plan:
                    selected_plan_data = plan_options[selected_plan][0]
                    selected_plan_id = plan_options[selected_plan][1]
                    st.write(f"Детали плана:")
                    st.write(selected_plan_data)
                    st.divider()
                    report = st.text_area("Поле для формирования отчета:")
                    # Отправка отчета
                    if st.button(f"Отправить отчет по выбранному плану"):
                        report_url = f"{BASE_URL}/reports/report/"
                        async with httpx.AsyncClient() as client:
                            report_response = await client.post(report_url, cookies={
                                "users_access_token": controller.get("users_access_token")},
                                                                json={"data": report, "planId": selected_plan_id})
                            if report_response.status_code == 200:
                                st.success("Отчет успешно отправлен!")
                            else:
                                st.error(
                                    f"Ошибка при отправке отчета: {report_response.status_code}, {report_response.text}")
        else:
            st.error(f"Ошибка при загрузке планов: {plans_response.status_code}, {plans_response.text}")

    st.divider()
    st.write("Информация о соревнованиях:")
    url = f"{BASE_URL}/athletes/my_competitions/"
    async with httpx.AsyncClient() as client:
        competitions = await client.get(url, cookies={"users_access_token": controller.get("users_access_token")})
        if competitions.status_code == 200:
            data = competitions.json()
            if data:
                # Отображаем данные в виде таблицы
                st.dataframe(data)
            else:
                st.write("Нет данных о соревнованиях.")
        else:
            st.error(f"Ошибка при загрузке соревнований: {competitions.status_code}, {competitions.text}")


    st.divider()
    if st.button("Выйти"):
        controller.remove("users_access_token")
        del st.session_state.logged_in
        st.success("Вы успешно вышли из аккаунта!")
        if st.button("Страница входа"):
            pass

async def trainer_profile():
    st.header("Личный кабинет тренера")
    st.divider()
    url = f"{BASE_URL}/auth/me/"
    #данные пользователя
    async with httpx.AsyncClient() as client:
        response = await client.get(url, cookies={"users_access_token": controller.get("users_access_token")})
        if response.status_code == 200:
            data = response.json()
            new_data = {
                "Ваше имя": data['first_name'],
                "Ваша фамилия": data['last_name'],
                "Номер телефона": data['phone_number'],
            }
            st.write("Ваши данные:")
            st.dataframe(new_data)
        else:
            st.error(f"Ошибка: {response.status_code}, {response.text}")
    st.divider()

    url = f"{BASE_URL}/trainers/signed_athletes/"
    async with httpx.AsyncClient() as client:
        athletes = await client.get(url, cookies={"users_access_token": controller.get("users_access_token")})
        if athletes.status_code == 200:
            data = athletes.json()
            athlete_names = [f"{athlete['first_name']} {athlete['last_name']}" for athlete in data]
        else:
            st.error(f"Ошибка при загрузке тренеров: {athletes.status_code}, {athletes.text}")
            return

    if data:
        selected_athlete = st.selectbox("Выберите спортсмена для отправки задания", athlete_names)
        # Получаем выбранного спортсмена
        athlete_id = next(athlete['id'] for athlete in data if
                          f"{athlete['first_name']} {athlete['last_name']}" == selected_athlete)
        # Форма для отправки задания
        plan = st.text_area("Задание для спортсмена:")
        if st.button("Отправить задание"):
            if plan:
                try:
                    url = f"{BASE_URL}/athletes/athlete_by_user_id/{athlete_id}/"
                    async with httpx.AsyncClient() as client:
                        response = await client.get(url)
                        response.raise_for_status()
                        data = response.json()

                    # # Отправка задания на сервер
                    url = f"{BASE_URL}/trainers/plan/"
                    async with httpx.AsyncClient() as client:
                        response = await client.post(url, json={'athlete_id': data.get('id'), 'data_plan': plan})
                        response.raise_for_status()
                        st.success(f"Задание отправлено спортсмену")

                except HTTPStatusError as e:
                    st.error(f"Ошибка сервера: {e.response.status_code}, {e.response.text}")
            else:
                st.error("Пожалуйста, введите задание.")
        st.divider()

    st.write("Отчеты от спортсменов:")
    reports_url = f"{BASE_URL}/trainers/athlete_reports/"
    async with httpx.AsyncClient() as client:
        reports_response = await client.get(reports_url,
                                            cookies={"users_access_token": controller.get("users_access_token")})
        if reports_response.status_code == 200:
            reports_data = reports_response.json()
            if not reports_data:
                st.info("Пока нет доступных отчетов.")
            else:


                # Отображение списка отчетов
                report_options = {f"Отчет от {report['athlete_first_name']} {report['athlete_last_name']}, план был выдан: {datetime.fromisoformat(report['plan_created_time']).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}": (report['report_id'], report['plan_data'], report['report_data'])
                                  for report in reports_data}
                selected_report = st.selectbox("Выберите отчет для просмотра:", list(report_options.keys()))

                # Просмотр деталей отчета
                if selected_report:
                    selected_report_plan_data = report_options[selected_report][1]
                    selected_report_report_data = report_options[selected_report][2]
                    st.write(f"Содержание поставленного плана: {selected_report_plan_data}")
                    st.divider()
                    st.write(f"Отчёт спортсмена: {selected_report_report_data}")
        else:
            st.error(f"Ошибка при загрузке отчетов: {reports_response.status_code}, {reports_response.text}")

    st.divider()

    st.write("Информация о соревнованиях для всех ваших спортсменов:")
    url = f"{BASE_URL}/trainers/signed_athletes/competitions/"
    async with httpx.AsyncClient() as client:
        competitions = await client.get(url, cookies={"users_access_token": controller.get("users_access_token")})
        if competitions.status_code == 200:
            data = competitions.json()
            if data:
                # Отображаем данные в виде таблицы
                st.dataframe(data)
            else:
                st.write("Нет данных о соревнованиях.")
        else:
            st.error(f"Ошибка при загрузке соревнований: {competitions.status_code}, {competitions.text}")

    st.divider()


    #функционал добавления соревнования для каждого спортсмена лично
    url = f"{BASE_URL}/trainers/signed_athletes/"
    async with httpx.AsyncClient() as client:
        athletes = await client.get(url, cookies={"users_access_token": controller.get("users_access_token")})
        if athletes.status_code == 200:
            data = athletes.json()
            athlete_names = [f"{athlete['first_name']} {athlete['last_name']}" for athlete in data]
        else:
            st.error(f"Ошибка при загрузке тренеров: {athletes.status_code}, {athletes.text}")
            return

    if data:
        selected_athlete = st.selectbox("Выберите спортсмена для добавления сорвенования", athlete_names)
        # Получаем выбранного спортсмена
        athlete_id = next(athlete['id'] for athlete in data if
                          f"{athlete['first_name']} {athlete['last_name']}" == selected_athlete)

        title = st.text_input("Добавьет название соревнования:")
        data = st.text_input("Добавьте описание соревнования:")
        if st.button("Добавить соревнование"):
            if title and data:
                try:
                    url = f"{BASE_URL}/trainers/add_competition/{athlete_id}/"
                    async with httpx.AsyncClient() as client:
                        response = await client.post(url, json={'title': title, 'data': data})
                        response.raise_for_status()
                        st.success(f"Соревнование успешно добавлено")

                except HTTPStatusError as e:
                    st.error(f"Ошибка сервера: {e.response.status_code}, {e.response.text}")
            else:
                st.error("Пожалуйста, добавьте полную информацию о соревновании.")


    st.divider()
    if st.button("Выйти"):
        controller.remove("users_access_token")
        del st.session_state.logged_in
        st.success("Вы успешно вышли из аккаунта!")
        if st.button("Страница входа"):
            pass

async def registration():
    st.header("Регистрация")

    first_name = st.text_input("Имя")
    last_name = st.text_input("Фамилия")
    phone = st.text_input("Телефон")
    password = st.text_input("Пароль", type="password")
    role = st.selectbox("Выберите роль", ROLES)

    if st.button("Зарегистрироваться"):

        url = f"{BASE_URL}/auth/register/"
        data = {
            "password": password,
            "phone_number": phone,
            "first_name": first_name,
            "last_name": last_name,
            "role":  role
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=data)
            if response.status_code == 200:
                st.success("Регистрация прошла успешно!")
            elif response.status_code == 409:
                st.error("Пользователь уже существует")
            else:
                st.error(f"Ошибка: {response.status_code}, {response.text}")

async def login():
    st.header("Вход")

    phone = st.text_input("Телефон")
    password = st.text_input("Пароль", type="password")
    if st.button("Войти"):
        url = f"{BASE_URL}/auth/login/"
        data = {
            "phone_number": phone,
            "password": password,
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=data)
            if response.status_code == 200:
                access_token = response.json().get("access_token")
                if access_token:
                    controller.set("users_access_token", access_token)
                    st.success("Вы успешно вошли в систему!")
                    st.session_state.logged_in = True
                    if st.button("Перейти в личный кабинет"):
                        pass
                else:
                    st.error("Токен не найден в ответе сервера")
            elif response.status_code == 401:
                st.error("Неверный номер или пароль")
            elif response.status_code == 422:
                st.error("Неверный формат телефона")
            else:
                st.error(f"Ошибка: {response.status_code}, {response.text}")

def choose_profile():
    if (st.session_state.current_role == "Спортсмен"):
        asyncio.run(athlete_profile())
    else:
        asyncio.run(trainer_profile())

if "logged_in" in st.session_state:
    st.session_state.current_role = asyncio.run(get_current_role())
    choose_profile()
elif controller.get("users_access_token") is not None and (asyncio.run(token_is_correct())):
    st.session_state.current_role = asyncio.run(get_current_role())
    st.session_state.logged_in = True
    choose_profile()
else:
    choice = st.sidebar.radio("Выберите действие", ["Регистрация", "Вход"])
    if choice == "Регистрация":
        asyncio.run(registration())
    elif choice == "Вход":
        asyncio.run(login())