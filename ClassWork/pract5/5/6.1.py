# Функция перехода из комнаты в комнату
def go(room):
    def func(state):
        return dict(state, room=room)
    return func

# Структура игры. Комнаты и допустимые в них действия
game = {
    'room0': dict(
        left=go('room1'),
        up=go('room2'),
        right=go('room3')
    ),
    'room1': dict(
        up=go('room2'),
        right=go('room0')
    ),
    'room2': dict(
    ),
    'room3': dict(
        up=go('room4'),
        right=go('room5')
    ),
    'room4': dict(
        down=go('room3'),
        right=go('room5')
    ),
    'room5': dict(
        up=go('room4'),
        left=go('room3')
    )
}

# Стартовое состояние
START_STATE = dict(room='room0')

def is_goal_state(state):
    '''
    Проверить, является ли состояние целевым.
    '''
    return state['room'] == 'room2'

def get_current_room(state):
    '''
    Выдать комнату, в которой находится игрок.
    '''
    return state['room']

from collections import deque

from collections import deque

def make_model(game, start_state):
    '''
    Построить граф всех возможных состояний.
    '''
    model = {}
    queue = deque([tuple(start_state.items())])  # Преобразуем состояние в кортеж
    while queue:
        state = queue.popleft()
        model[state] = model.get(state, [])
        room = get_current_room(dict(state))  # Преобразуем состояние обратно в словарь
        for action, next_state_func in game[room].items():
            new_state = tuple(next_state_func(dict(state)).items())  # Преобразуем новое состояние в кортеж
            if new_state not in model:
                model[new_state] = []
                queue.append(new_state)
            model[state].append((action, new_state))
    return model

model = make_model(game, START_STATE)
for state, actions in model.items():
    print(f'{state}: {actions}')
