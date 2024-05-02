import unittest
from datetime import datetime

from cloud_function.replay_from_bigquery import TimeConfig


class TestTimeConfig(unittest.TestCase):
    config = TimeConfig(
        real_start_time=datetime.fromtimestamp(4000).isoformat(),
        simulation_start_time=datetime.fromtimestamp(10000).isoformat(),
        simulation_end_time=datetime.fromtimestamp(20000).isoformat(),
        speed=2,
        scheduler_name=""
    )

    def test_is_before_simulation(self):
        self.assertEqual(self.config.is_before_simulation(datetime.fromtimestamp(12000)), False)
        self.assertEqual(self.config.is_before_simulation(datetime.fromtimestamp(10000)), False)
        self.assertEqual(self.config.is_before_simulation(datetime.fromtimestamp(6000)), False)
        self.assertEqual(self.config.is_before_simulation(datetime.fromtimestamp(4000)), False)
        self.assertEqual(self.config.is_before_simulation(datetime.fromtimestamp(2000)), True)
        self.assertEqual(self.config.is_before_simulation(datetime.fromtimestamp(3999)), True)

    def test_is_after_simulation(self):
        self.assertEqual(self.config.is_after_simulation(datetime.fromtimestamp(12000)), True)
        self.assertEqual(self.config.is_after_simulation(datetime.fromtimestamp(10000)), True)
        self.assertEqual(self.config.is_after_simulation(datetime.fromtimestamp(9000)), True)
        self.assertEqual(self.config.is_after_simulation(datetime.fromtimestamp(8999)), False)
        self.assertEqual(self.config.is_after_simulation(datetime.fromtimestamp(2000)), False)
        self.assertEqual(self.config.is_after_simulation(datetime.fromtimestamp(3999)), False)

    def test_get_simulation_time(self):
        self.assertEqual(self.config.get_simulation_time(datetime.fromtimestamp(4000)), datetime.fromtimestamp(10000))
        self.assertEqual(self.config.get_simulation_time(datetime.fromtimestamp(4001)), datetime.fromtimestamp(10002))
        self.assertEqual(self.config.get_simulation_time(datetime.fromtimestamp(6000)), datetime.fromtimestamp(14000))
        self.assertEqual(self.config.get_simulation_time(datetime.fromtimestamp(9000)), datetime.fromtimestamp(20000))


if __name__ == '__main__':
    unittest.main()