from classic_cli_boardgames.core.rng import create_rng


def test_seeded_rng_is_deterministic() -> None:
    rng_a = create_rng(123)
    rng_b = create_rng(123)
    sequence_a = [rng_a.randint(1, 100) for _ in range(5)]
    sequence_b = [rng_b.randint(1, 100) for _ in range(5)]
    assert sequence_a == sequence_b
