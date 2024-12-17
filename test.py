from main import *


def test_generate_universe():
    assert generate_universe((4, 4)) == [
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
    ]


def test_add_seed_to_universe():
    seed = seeds["r_pentomino"]
    universe = generate_universe(size=(6, 6))
    universe = add_seed_to_universe(seed, universe, x_start=1, y_start=1)
    test_equality = np.array(
        universe
        == np.array(
            [
                [0, 0, 0, 0, 0, 0],
                [0, 0, 1, 1, 0, 0],
                [0, 1, 1, 0, 0, 0],
                [0, 0, 1, 0, 0, 0],
                [0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0],
            ],
            dtype=np.uint8,
        )
    )
    assert test_equality.all()


def test_survival_1():
    universe = generate_universe(size=(6, 6))
    for y in range(6):
        for x in range(6):
            assert survival(universe, x, y) == 0


def test_survival_2():
    universe = generate_universe(size=(3, 4))
    universe = add_seed_to_universe(seeds["glider"], universe, 0, 0)
    next_gen = generate_universe(size=(3, 4))
    for y in range(4):
        for x in range(3):
            next_gen[y][x] = survival(universe, x, y)
    assert next_gen == [[0, 0, 0], [1, 0, 1], [0, 1, 1], [0, 1, 0]]


def test_generation():
    universe = generate_universe(size=(3, 4))
    universe = add_seed_to_universe(seeds["glider"], universe, 0, 0)
    assert generation(universe) == [[0, 0, 0], [1, 0, 1], [0, 1, 1], [0, 1, 0]]
