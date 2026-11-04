from random import choice, randint

import pygame as pg

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Словарь для определения нового направления движения
DIRECTIONS = {
    (LEFT, pg.K_UP): UP,
    (RIGHT, pg.K_UP): UP,
    (UP, pg.K_LEFT): LEFT,
    (DOWN, pg.K_LEFT): LEFT,
    (LEFT, pg.K_DOWN): DOWN,
    (RIGHT, pg.K_DOWN): DOWN,
    (UP, pg.K_RIGHT): RIGHT,
    (DOWN, pg.K_RIGHT): RIGHT,
}

# Цвет фона - черный:
BOARD_BACKGROUND_COLOR = (0, 0, 0)

# Цвет границы ячейки
BORDER_COLOR = (93, 216, 228)

# Цвет яблока
APPLE_COLOR = (255, 0, 0)

# Цвет змейки
SNAKE_COLOR = (0, 255, 0)

# Настройки скорости змейки:
SPEED = 20
MIN_SPEED = 5
MAX_SPEED = 40
SPEED_STEP = 5

# Настройка игрового окна:
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля (с подсказками по управлению):
pg.display.set_caption(
    'Змейка | Стрелки: движение | + / - : скорость | Esc: выход'
)

# Настройка времени:
clock = pg.time.Clock()


class GameObject:
    """Базовый класс для игровых объектов."""

    def __init__(self, body_color=None):
        """Инициализирует позицию объекта в центре экрана."""
        self.position = (
            SCREEN_WIDTH // 2 // GRID_SIZE * GRID_SIZE,
            SCREEN_HEIGHT // 2 // GRID_SIZE * GRID_SIZE,
        )
        self.body_color = body_color

    def draw_cell(self, position, color, border_color=None):
        """Вспомогательный метод для отрисовки одной клетки."""
        rect = pg.Rect(position, (GRID_SIZE, GRID_SIZE))
        pg.draw.rect(screen, color, rect)
        if border_color:
            pg.draw.rect(screen, border_color, rect, 1)

    def draw(self):
        """Отрисовывает объект. Переопределяется в наследниках."""
        raise NotImplementedError(
            'Метод draw() должен быть переопределен в дочернем классе'
        )


class Apple(GameObject):
    """Яблоко — игровой объект, который змейка может съесть."""

    def __init__(self, occupied_positions=None):
        """Создаёт яблоко в случайной позиции."""
        super().__init__(APPLE_COLOR)
        if occupied_positions is None:
            occupied_positions = []
        self.randomize_position(occupied_positions)

    def randomize_position(self, occupied_positions):
        """Устанавливает случайную позицию, не занятую змейкой."""
        if len(occupied_positions) >= GRID_WIDTH * GRID_HEIGHT:
            self.position = (-GRID_SIZE, -GRID_SIZE)
            return

        while True:
            new_position = (
                randint(0, GRID_WIDTH - 1) * GRID_SIZE,
                randint(0, GRID_HEIGHT - 1) * GRID_SIZE,
            )
            if new_position not in occupied_positions:
                self.position = new_position
                break

    def draw(self):
        """Рисует яблоко квадратом размером в одну клетку."""
        self.draw_cell(self.position, self.body_color, BORDER_COLOR)


class Snake(GameObject):
    """Змейка: хранит сегменты, движется, растёт, проверяет столкновения."""

    def __init__(self):
        """Инициализирует змейку в центре поля."""
        super().__init__(SNAKE_COLOR)
        self.reset()

    def get_head_position(self):
        """Возвращает координаты головы змейки."""
        return self.positions[0]

    def update_direction(self, new_direction):
        """Применяет новое направление, выбранное пользователем."""
        if new_direction:
            self.direction = new_direction

    def move(self):
        """Перемещает змейку на одну клетку с проходом сквозь границы."""
        head_x, head_y = self.get_head_position()
        delta_x, delta_y = self.direction

        self.position = (
            (head_x + delta_x * GRID_SIZE) % SCREEN_WIDTH,
            (head_y + delta_y * GRID_SIZE) % SCREEN_HEIGHT,
        )

        self.positions.insert(0, self.position)

        if len(self.positions) > self.length:
            self.last = self.positions.pop()
        else:
            self.last = None

    def reset(self):
        """Возвращает змейку в начальное состояние."""
        self.length = 1
        self.positions = [(
            SCREEN_WIDTH // 2 // GRID_SIZE * GRID_SIZE,
            SCREEN_HEIGHT // 2 // GRID_SIZE * GRID_SIZE,
        )]
        self.direction = choice([UP, DOWN, LEFT, RIGHT])
        self.last = None
        self.speed = SPEED

    def draw(self):
        """Отрисовывает голову змейки и затирает ушедший сегмент."""
        head_position = self.get_head_position()
        self.draw_cell(head_position, self.body_color, BORDER_COLOR)

        if self.last:
            self.draw_cell(self.last, BOARD_BACKGROUND_COLOR)


def handle_keys(game_object):
    """Обрабатывает нажатия клавиш и закрытие окна."""
    for event in pg.event.get():
        if event.type == pg.QUIT:
            return False

        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                return False

            # Изменение скорости
            if event.key in (pg.K_EQUALS, pg.K_KP_PLUS):
                game_object.speed = min(
                    game_object.speed + SPEED_STEP, MAX_SPEED
                )
            elif event.key in (pg.K_MINUS, pg.K_KP_MINUS):
                game_object.speed = max(
                    game_object.speed - SPEED_STEP, MIN_SPEED
                )

            # Изменение направления через словарь
            new_direction = DIRECTIONS.get(
                (game_object.direction, event.key)
            )
            game_object.update_direction(new_direction)

    return True


def main():
    """Запускает основной игровой цикл."""
    pg.init()

    snake = Snake()
    apple = Apple(snake.positions)

    running = True
    while running:
        clock.tick(snake.speed)

        running = handle_keys(snake)
        snake.move()

        if snake.get_head_position() == apple.position:
            snake.length += 1
            apple.randomize_position(snake.positions)
        elif snake.get_head_position() in snake.positions[1:]:
            snake.reset()
            screen.fill(BOARD_BACKGROUND_COLOR)
            apple.randomize_position(snake.positions)

        apple.draw()
        snake.draw()
        pg.display.update()


if __name__ == '__main__':
    main()
