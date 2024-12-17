import math
import argparse
import json
import random as rd
import sys
from os import path
import pygame


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = path.abspath(".")

    return path.join(base_path, relative_path)


def generate_universe(size):
    """Generate an empty universe

    Args:
        size (tuple): The dimensions of the universe

    Returns:
        list: The universe
    """
    return [
        [0 for x in range(size[0])] for y in range(size[1])
    ]  # Creation of a matrix full of 0 using the comprehension method


seeds = json.loads(
    open(resource_path("./seeds.json"), "r").read()
)  # Load the seed dictionary from seeds.json


def add_seed_to_universe(seed, universe, x_start, y_start):
    """Adds the seed to the universe at the given position

    Args:
        seed (list): The seed matrix
        universe (list): The universe matrix
        x_start (int): The x coordinate of the top-left corner of the seed
        y_start (int): The y coordinate of the top-left corner of the seed

    Returns:
        list: The universe to which the seed has been added
    """
    width = len(universe[0])  # Width of the universe
    height = len(universe)  # Height of the universe
    seed_width = len(seed[0])  # Width of the seed
    seed_height = len(seed)  # Height of the seed
    if (
        seed_width <= width - x_start and seed_height <= height - y_start
    ):  # If the seed fits in the universe at the given position
        for y in range(seed_height):
            for x in range(seed_width):
                universe[y_start + y][x_start + x] = seed[y][
                    x
                ]  # Replace cells of the universe with the corresponding cell in the seed
    else:
        return None
    return universe


def survival(universe, xc, yc):
    """Find the next state of a given cell

    Args:
        universe (list): The universe matrix
        xc (int): The x coordinate of the cell to evaluate
        yc (int): The y coordinate of the cell to evaluate

    Returns:
        int: The next state of the cell (either 0 or 1)
    """
    live = 0  # Initialize the number of living neighbors to 0
    for x in range(-1, 2):  # x going from -1 to 1
        for y in range(-1, 2):  # y going from -1 to 1
            if (
                x == y == 0
            ):  # Ignore the cell we are evaluating (when the absolute offset equals 0)
                continue
            if (
                xc == 0
                and x < 0
                or yc == 0
                and y < 0
                or xc == len(universe[0]) - 1
                and x > 0
                or yc == len(universe) - 1
                and y > 0
            ):  # Handle the cases when the evaluated cell is at the border of the grid
                continue
            try:
                if universe[yc + y][xc + x] == 1:  # If the neighbor is alive
                    live += 1  # Increment the number of living neighbors
            except IndexError:
                pass
    if (
        universe[yc][xc] == 0 and live == 3 or universe[yc][xc] == 1 and live in [2, 3]
    ):  # If the cell is dead and there are exactly 3 alive neighbors or if the cell is living and there are either 2 or 3 living neighbors
        return 1
    return 0


def generation(universe):
    """Generate the next generation of the universe

    Args:
        universe (list): The universe matrix

    Returns:
        list: The next generation matrix
    """
    new_universe = generate_universe(
        (len(universe[0]), len(universe))
    )  # Initialize an empty universe
    for y in range(len(universe)):
        for x in range(len(universe[0])):
            new_universe[y][x] = survival(
                universe, x, y
            )  # Set the value of each cell of the new universe to the value in the next generation (computed with survival)
    return new_universe


def game_life_simulate(universe, gens):
    display_universe(universe)
    for _ in range(gens):
        universe = generation(universe)
        display_universe(universe)


def clockwise_transpose(matrix):
    num_rows, num_cols = len(matrix), len(matrix[0])

    # Reverse the rows of the matrix
    reversed_matrix = matrix[::-1]

    # Transpose the reversed matrix
    transposed_matrix = [
        [reversed_matrix[j][i] for j in range(num_rows)] for i in range(num_cols)
    ]

    return transposed_matrix


def mirror_vertical(matrix):
    if not matrix:
        return []

    mirrored_matrix = [row[::-1] for row in matrix]

    return mirrored_matrix


if __name__ == "__main__":
    pygame.init()
    pygame.font.init()

    # Constants for the window
    WIDTH, HEIGHT = 1200, 900
    WINDOW_SIZE = (WIDTH, HEIGHT)
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    BLUE = (0, 126, 243)
    GREEN = (77, 255, 97)
    BACKGROUND_COLOR = WHITE
    frame_delay = 10
    my_font = pygame.font.SysFont("Copperplate Gothic", 30, bold=True)
    button_font = pygame.font.SysFont("Copperplate Gothic", 20, bold=True)

    # Create the window
    screen = pygame.display.set_mode(WINDOW_SIZE)
    pygame.display.set_caption("L'Arche's game of life")  # Set the window title
    arche_icon = pygame.image.load(resource_path("images/icon.png"))
    pygame.display.set_icon(arche_icon)
    state = 0
    width_input_color = BLACK  # Set the color of the input as black
    height_input_color = BLACK
    width_input_value = ""  # Initialize the value of the input to an empty string
    height_input_value = ""
    mousedown_pos = (None, None)
    mousedown_witness = False
    pause_state = False  # This indicates whether the game is in pause
    selected_seed = []  # Initialize the selected seed
    scroll_pos = 0  # Initialize the scroll position
    # Main game loop
    running = True
    while running:
        # Initialize some rectangles
        width_input = pygame.Rect(3 * WIDTH // 8, 50, WIDTH // 4, 50)
        height_input = pygame.Rect(3 * WIDTH // 8, 300, WIDTH // 4, 50)
        submit_button = pygame.Rect(7 * WIDTH // 16, 500, WIDTH // 8, 25)
        seeds_list = (
            {}
        )  # The dictionary that associates each seed name to their respective rect
        i = 0
        for seed in seeds:
            seeds_list[seed] = pygame.Rect(
                (i % 3) * (WIDTH // 4 + WIDTH // 12) + WIDTH // 24,
                50 + (i // 3) * (WIDTH // 4 + 30) + scroll_pos,
                WIDTH // 4,
                WIDTH // 4,
            )  # Setup the position of the rectangles based on its order in the list of seeds, and the scroll position
            i += 1
        for event in pygame.event.get():
            if (
                event.type == pygame.QUIT
            ):  # If the user clicked on the red cross to close the window
                running = False
            if (
                event.type == pygame.MOUSEBUTTONDOWN
            ):  # If the left button of the mouse is clicked
                if event.button == 1:
                    if state == 0:
                        for seed in seeds_list:
                            if seeds_list[seed].collidepoint(
                                event.pos
                            ):  # Get the clicked seed
                                selected_seed = seeds[seed]
                                state += 1
                                break
                    elif state == 1:
                        if width_input.collidepoint(
                            event.pos
                        ):  # If the user clicked on the width input
                            width_input_color = BLUE
                            height_input_color = BLACK
                        elif height_input.collidepoint(
                            event.pos
                        ):  # If the user clicked on the height input
                            height_input_color = BLUE
                            width_input_color = BLACK
                        elif (
                            submit_button.collidepoint(
                                event.pos
                            )  # If the user clicked on the "Next" button
                            and len(width_input_value) > 0
                            and len(height_input_value) > 0
                            and int(width_input_value)
                            >= max(len(selected_seed), len(selected_seed[0]))
                            and int(height_input_value)
                            >= max(len(selected_seed), len(selected_seed[0]))
                        ):  # Check the validity of the given universe dimensions
                            universe_width = int(width_input_value)
                            universe_height = int(height_input_value)
                            state += 1
                        else:  # If the user clicked elsewhere
                            width_input_color = BLACK
                            height_input_color = BLACK
                    elif state == 2:
                        universe = add_seed_to_universe(
                            selected_seed,
                            generate_universe((universe_width, universe_height)),
                            cell_x,
                            cell_y,
                        )  # Generate the universe to which the seed has been added at the hovered cell
                        frame_delay = 50  # Increment the frame delay so that the animation will run more slowly
                        mousedown_witness = False
                        state += 1
                    elif state == 3:
                        mousedown_pos = (
                            event.pos[0] * universe_width // WIDTH,
                            event.pos[1] * universe_height // HEIGHT,
                        )
                        mousedown_witness = True
                elif event.button == 3 and state == 3:
                    mousedown_pos = (
                        event.pos[0] * universe_width // WIDTH,
                        event.pos[1] * universe_height // HEIGHT,
                    )
                    mousedown_witness = True
            if event.type == pygame.MOUSEBUTTONUP and state == 3 and mousedown_witness:
                cell_x = event.pos[0] * universe_width // WIDTH
                cell_y = event.pos[1] * universe_height // HEIGHT
                if mousedown_pos[0] == cell_x and mousedown_pos[1] == cell_y:
                    universe[cell_y][cell_x] = int(not universe[cell_y][cell_x])
                else:
                    for y in range(
                        min(mousedown_pos[1], cell_y),
                        max(mousedown_pos[1], cell_y) + 1,
                    ):
                        for x in range(
                            min(mousedown_pos[0], cell_x),
                            max(mousedown_pos[0], cell_x) + 1,
                        ):
                            universe[y][x] = (
                                1
                                if event.button == 1
                                else 0
                                if event.button == 3
                                else universe[y][x]
                            )
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and state in [2, 3]:
                    pause_state = not pause_state  # Toggle pause state
                if event.key == pygame.K_RETURN and state == 1:
                    if (
                        len(width_input_value) > 0
                        and len(height_input_value) > 0
                        and int(width_input_value)
                        >= max(len(selected_seed), len(selected_seed[0]))
                        and int(height_input_value)
                        >= max(len(selected_seed), len(selected_seed[0]))
                    ):
                        universe_width = int(width_input_value)
                        universe_height = int(height_input_value)
                        state += 1
                if (
                    event.key == pygame.K_TAB and state == 1
                ):  # Allow switching between input fields using the tab character
                    if width_input_color == BLUE:
                        width_input_color = BLACK
                        height_input_color = BLUE
                    else:
                        width_input_color = BLUE
                        height_input_color = BLACK
                if event.key == pygame.K_r and state == 2:
                    selected_seed = clockwise_transpose(
                        selected_seed
                    )  # Rotate the seed
                if event.key == pygame.K_m and state == 2:
                    selected_seed = mirror_vertical(selected_seed)  # Mirror the seed
                if event.key == pygame.K_b:
                    state -= 1  # Go back to the previous state
                    if state < 0:
                        state = 0
                if event.key == pygame.K_c and state == 3:
                    universe = generate_universe((universe_width, universe_height))
                if event.key == pygame.K_RIGHT and pause_state:
                    universe = generation(universe)  # Go to the next generation
                if event.key == pygame.K_BACKSPACE:
                    if (
                        width_input_color == BLUE and len(width_input_value) > 0
                    ):  # If the width input and selected and it is non-empty
                        width_input_value = width_input_value[
                            :-1
                        ]  # Remove the last character
                    elif height_input_color == BLUE and len(height_input_value) > 0:
                        height_input_value = height_input_value[:-1]
                if event.key == pygame.K_0 or event.key == pygame.K_KP0:
                    if (
                        width_input_color == BLUE and len(width_input_value) < 2
                    ):  # If the width input is selected and there are no more than 2 characters in it
                        width_input_value += "0"  # Concatenate 0
                    elif height_input_color == BLUE and len(height_input_value) < 2:
                        height_input_value += "0"
                if event.key == pygame.K_1 or event.key == pygame.K_KP1:
                    if width_input_color == BLUE and len(width_input_value) < 2:
                        width_input_value += "1"
                    elif height_input_color == BLUE and len(height_input_value) < 2:
                        height_input_value += "1"
                if event.key == pygame.K_2 or event.key == pygame.K_KP2:
                    if width_input_color == BLUE and len(width_input_value) < 2:
                        width_input_value += "2"
                    elif height_input_color == BLUE and len(height_input_value) < 2:
                        height_input_value += "2"
                if event.key == pygame.K_3 or event.key == pygame.K_KP3:
                    if width_input_color == BLUE and len(width_input_value) < 2:
                        width_input_value += "3"
                    elif height_input_color == BLUE and len(height_input_value) < 2:
                        height_input_value += "3"
                if event.key == pygame.K_4 or event.key == pygame.K_KP4:
                    if width_input_color == BLUE and len(width_input_value) < 2:
                        width_input_value += "4"
                    elif height_input_color == BLUE and len(height_input_value) < 2:
                        height_input_value += "4"
                if event.key == pygame.K_5 or event.key == pygame.K_KP5:
                    if width_input_color == BLUE and len(width_input_value) < 2:
                        width_input_value += "5"
                    elif height_input_color == BLUE and len(height_input_value) < 2:
                        height_input_value += "5"
                if event.key == pygame.K_6 or event.key == pygame.K_KP6:
                    if width_input_color == BLUE and len(width_input_value) < 2:
                        width_input_value += "6"
                    elif height_input_color == BLUE and len(height_input_value) < 2:
                        height_input_value += "6"
                if event.key == pygame.K_7 or event.key == pygame.K_KP7:
                    if width_input_color == BLUE and len(width_input_value) < 2:
                        width_input_value += "7"
                    elif height_input_color == BLUE and len(height_input_value) < 2:
                        height_input_value += "7"
                if event.key == pygame.K_8 or event.key == pygame.K_KP8:
                    if width_input_color == BLUE and len(width_input_value) < 2:
                        width_input_value += "8"
                    elif height_input_color == BLUE and len(height_input_value) < 2:
                        height_input_value += "8"
                if event.key == pygame.K_9 or event.key == pygame.K_KP9:
                    if width_input_color == BLUE and len(width_input_value) < 2:
                        width_input_value += "9"
                    elif height_input_color == BLUE and len(height_input_value) < 2:
                        height_input_value += "9"
            if event.type == pygame.MOUSEWHEEL:
                scroll_pos += event.y * 100
                if scroll_pos > 0:  # Disable the user to scroll over the first line
                    scroll_pos = 0
                elif (
                    scroll_pos
                    < -(math.ceil(len(seeds) / 3) * (WIDTH // 4 + 30) + 50) + HEIGHT
                ):  # Disable the user to scroll under the last line
                    scroll_pos = (
                        -(math.ceil(len(seeds) / 3) * (WIDTH // 4 + 30) + 50) + HEIGHT
                    )

        screen.fill(BACKGROUND_COLOR)  # Fill the background white
        if state == 0:
            for seed_tuple in seeds_list.items():
                seed_rect = seed_tuple[1]
                seed = seeds[seed_tuple[0]]
                if len(seed) == len(seed[0]):  # Center the seed inside the square
                    correction_x = 0
                    correction_y = 0
                elif len(seed[0]) > len(seed):
                    correction_x = 0
                    correction_y = (
                        WIDTH // 8 - len(seed) * WIDTH // (4 * len(seed[0])) / 2
                    )
                else:
                    correction_x = (
                        WIDTH // 8 - len(seed[0]) * WIDTH // (4 * len(seed)) / 2
                    )
                    correction_y = 0
                for y in range(len(seed)):
                    for x in range(len(seed[0])):
                        pygame.draw.rect(
                            screen,
                            BLACK if seed[y][x] else WHITE,
                            pygame.Rect(
                                seed_rect.x
                                + x * WIDTH // (4 * max(len(seed), len(seed[0])))
                                + correction_x,
                                seed_rect.y
                                + y * WIDTH // (4 * max(len(seed), len(seed[0])))
                                + correction_y,
                                WIDTH // (4 * len(seed[0])),
                                WIDTH // (4 * len(seed[0])),
                            ),
                            0,
                        )
                pygame.draw.rect(
                    screen, BLACK, seed_rect, 2
                )  # Draw the preview of the seed
            pygame.draw.rect(
                screen,
                WHITE,
                pygame.Rect(
                    0, 0, WIDTH, my_font.size("Select the seed (scroll down)")[1]
                ),
                0,
            )  # Draw a white rectangle to make the header readable at all times
            select_the_seed = my_font.render(
                "Select the seed (scroll down)", False, BLACK
            )
            screen.blit(
                select_the_seed,
                (
                    WIDTH // 2
                    - my_font.size("Select the seed (scroll down)")[0]
                    // 2,  # Center the text
                    0,
                ),
            )
        elif state == 1:
            pygame.draw.rect(screen, width_input_color, width_input, 2)
            pygame.draw.rect(screen, height_input_color, height_input, 2)
            pygame.draw.rect(
                screen,
                GREEN
                if len(width_input_value) > 0
                and len(height_input_value) > 0
                and int(width_input_value)
                >= max(len(selected_seed), len(selected_seed[0]))
                and int(height_input_value)
                >= max(len(selected_seed), len(selected_seed[0]))
                else BLACK,
                submit_button,
                2,
            )
            width_value = my_font.render(width_input_value, False, BLACK)
            screen.blit(
                width_value,
                (
                    WIDTH // 2
                    - my_font.size(width_input_value)[0]
                    // 2,  # Center text in the input
                    75 - my_font.size(width_input_value)[1] // 2,
                ),
            )
            height_value = my_font.render(height_input_value, False, BLACK)
            screen.blit(
                height_value,
                (
                    WIDTH // 2
                    - my_font.size(height_input_value)[0]
                    // 2,  # Center text in the input
                    325 - my_font.size(height_input_value)[1] // 2,
                ),
            )
            width_label = my_font.render(
                f"Width of the universe (min {max(len(selected_seed), len(selected_seed[0]))})",
                False,
                BLACK,
            )
            screen.blit(
                width_label,
                (
                    WIDTH // 2
                    - my_font.size(
                        f"Width of the universe (min {max(len(selected_seed), len(selected_seed[0]))})"
                    )[0]
                    // 2,
                    25
                    - my_font.size(
                        f"Width of the universe (min {max(len(selected_seed), len(selected_seed[0]))})"
                    )[1]
                    // 2,
                ),
            )
            height_label = my_font.render(
                f"Height of the universe (min {max(len(selected_seed), len(selected_seed[0]))})",
                False,
                BLACK,
            )
            screen.blit(
                height_label,
                (
                    WIDTH // 2
                    - my_font.size(
                        f"Height of the universe (min {max(len(selected_seed), len(selected_seed[0]))})"
                    )[0]
                    // 2,
                    275
                    - my_font.size(
                        f"Height of the universe (min {max(len(selected_seed), len(selected_seed[0]))})"
                    )[1]
                    // 2,
                ),
            )
            submit_button_text = button_font.render("Next", False, BLACK)
            screen.blit(
                submit_button_text,
                (
                    WIDTH // 2 - button_font.size("Next")[0] // 2,
                    512 - button_font.size("Next")[1] // 2,
                ),
            )
        elif state == 2:
            seed = selected_seed
            mx, my = pygame.mouse.get_pos()
            cell_x = min(
                mx * universe_width // WIDTH, universe_width - len(seed[0])
            )  # Choose the smallest value between the mouse position and the width of the screen minus the seed width to prevent the seed from overflowing from the screen
            cell_y = min(my * universe_height // HEIGHT, universe_height - len(seed))
            for y in range(universe_height):
                for x in range(universe_width):
                    if 0 <= x - cell_x < len(seed[0]) and 0 <= y - cell_y < len(
                        seed
                    ):  # If the current cell is inside the area the seed is to occupy
                        pygame.draw.rect(
                            screen,
                            BLACK,
                            pygame.Rect(
                                x * WIDTH / universe_width,
                                y * HEIGHT / universe_height,
                                WIDTH / universe_width,
                                HEIGHT / universe_height,
                            ),
                            not (seed[y - cell_y][x - cell_x]),
                        )
                    else:
                        pygame.draw.rect(
                            screen,
                            BLACK,
                            pygame.Rect(
                                x * WIDTH / universe_width,
                                y * HEIGHT / universe_height,
                                WIDTH / universe_width,
                                HEIGHT / universe_height,
                            ),
                            1,
                        )
        elif state == 3:
            for y in range(universe_height):
                for x in range(universe_width):
                    pygame.draw.rect(
                        screen,
                        BLACK,
                        pygame.Rect(
                            x * WIDTH / universe_width,
                            y * HEIGHT / universe_height,
                            WIDTH / universe_width,
                            HEIGHT / universe_height,
                        ),
                        int(not (universe[y][x])),
                    )  # Draw the cell according to its state in universe
            if not pause_state:
                universe = generation(universe)
        # Update the display
        pygame.display.flip()

        # Control the frame rate
        pygame.time.delay(frame_delay)

    # Quit Pygame
    pygame.quit()
