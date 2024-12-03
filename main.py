import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType

GROUP_1_TOKEN = 'vk1.a.uwjXMDjnjT-TJ1Sjl_Y9ojzSBC2Hk7pNkqHSpv2mOlO8ROOr7kZKNWlRqKdJ6LlOnFGgcQ0AdexBTM6ool7GkDeXD2vn46hpyqsZ7jvj0meINRCpbX5S3BEe6de59c8HxrFMlRdYtPrHiQlMIP42tO6LuZZfSNQQk3cH2EWivmXratAbHZwsWh3H64N79D5LRUKehhnaNy5prx4FS5qJCw'
GROUP_2_TOKEN = 'vk1.a.Bz7irK04nnzJt-yCL2CA34rMQebvtd_F2TBEfyWE-qmgYm47WxR7HelEtslUWkl5B-O3Cmf7IpAoKbgThmCyn_pUDuliLsOvQO33IAytTzKMtJkf7492aEZedPlLFtAZ60ztnmgyWJcJZRQsUlCV7v9UnBUd2LxcMGoVBpSduKSQ5dDW4D-Ohqwr9R194SzxfL57ZI8DzvrP9AimU0m9Xg'
GROUP_1_ID = '228462206'

vk1_session = vk_api.VkApi(token=GROUP_1_TOKEN)
vk2_session = vk_api.VkApi(token=GROUP_2_TOKEN)

vk1 = vk1_session.get_api()
vk2 = vk2_session.get_api()

# Настройка LongPoll для первой группы
longpoll = VkBotLongPoll(vk1_session, group_id=GROUP_1_ID)


def forward_post_to_user(user_id, message, group_id, post_id=None, comment_id=None):

    try:
        attachment = None
        if post_id:
            attachment = f"wall-{group_id}_{post_id}"
        elif comment_id:
            attachment = f"wall-{group_id}_{post_id}_r{comment_id}"

        vk2.messages.send(
            user_id=user_id,
            random_id=0,
            message=message,
            attachment=attachment
        )
        print(f"Уведомление отправлено пользователю {user_id}")
    except vk_api.exceptions.ApiError as e:
        print(f"Ошибка при отправке уведомления: {e}")


def process_mentions(text, group_id, post_id=None, comment_id=None):
    """
    Проверяет текст на наличие хэштегов и упоминаний пользователей.
    В зависимости от хэштегов пересылает пост с сообщением.
    """
    user_mentions = []
    words = text.split()

    for word in words:
        if word.startswith('[id'):
            try:
                user_id = int(word[3:].split('|')[0])
                user_mentions.append(user_id)
            except ValueError:
                continue

    # Проверяем наличие хэштегов
    is_payment = "#оплата@cardclub" in text
    is_received = "#получено@cardclub" in text

    if is_payment:
        message_text = f"#оплата@cardclub\n\nВас упомянули в посте с оплатой."
    elif is_received:
        message_text = f"#получено@cardclub\n\nВас упомянули в посте с пришедшим"
    else:
        message_text = "Вас упомянули в посте или комментарии!"

    if post_id:
        attachment = f"wall-{group_id}_{post_id}"  # Идентификатор поста
    else:
        print("Ошибка: post_id обязателен для пересылки.")
        return

    for user_id in user_mentions:
        try:
            vk2.messages.send(
                user_id=user_id,
                random_id=0,
                message=message_text,
                attachment=attachment
            )
            print(f"Пост отправлен пользователю {user_id}")
        except vk_api.exceptions.ApiError as e:
            print(f"Ошибка при отправке поста пользователю {user_id}: {e}")

def main():
    print("Бот запущен и слушает события...")
    for event in longpoll.listen():
        if event.type == VkBotEventType.WALL_POST_NEW:
            # Новый пост
            post = event.object
            post_id = post['id']
            group_id = abs(post['owner_id'])
            text = post.get('text', '')

            print(f"Новый пост: {text}")
            process_mentions(text, group_id, post_id=post_id)

        elif event.type == VkBotEventType.WALL_REPLY_NEW:
            # Новый комментарий
            comment = event.object
            comment_id = comment['id']
            post_id = comment['post_id']
            group_id = abs(comment['owner_id'])
            text = comment.get('text', '')

            print(f"Новый комментарий: {text}")
            process_mentions(text, group_id, post_id=post_id, comment_id=comment_id)


if __name__ == "__main__":
    main()