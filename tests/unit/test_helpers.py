import pytest

from tests.helpers.generate_data import generate_rand_stage


@pytest.mark.usefixtures("create_users")
class TestGenerate:
    def test_generate_target(self, test_client, captured_templates):
        num_shots = 10
        stage = generate_rand_stage(self.student.id, num_shots, 0, 0, 0.1, 0.1, "300m")
        stage.init_shots()
        assert (len(stage.shotList) == num_shots)
