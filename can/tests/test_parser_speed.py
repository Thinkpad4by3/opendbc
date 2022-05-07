#!/usr/bin/env python3
import glob
import os
import random
import time
import unittest

from opendbc import DBC_PATH
from opendbc.can.packer import CANPacker
from opendbc.can.parser import CANParser
from opendbc.generator.generator import generated_suffix
from selfdrive.boardd.boardd import can_list_to_can_capnp


class TestCANParserSpeed(unittest.TestCase):
  @classmethod
  def setUpClass(cls):
    cls.dbcs = []
    for dbc in glob.glob(f"{DBC_PATH}/*{generated_suffix}"):
      cls.dbcs.append(os.path.basename(dbc).split('.')[0])

  def test_dbc_parsing(self):
    start_time = time.time()
    for dbc in self.dbcs:
      CANParser(dbc, [], [], 0)
    elapsed = time.time() - start_time
    self.assertLess(elapsed, 0.15, "Took too long to parse {} DBCs".format(len(self.dbcs)))

  def test_can_parsing(self):
    signals = [
      ("CR_VSM_DecCmd", "SCC12"),
      ("aReqValue", "SCC12"),
      ("aReqRaw", "SCC12"),
    ]
    checks = [("SCC12", 50)]
    parser = CANParser("hyundai_kia_generic", signals, checks, 0)
    packer = CANPacker("hyundai_kia_generic")

    start_time = time.time()
    for _ in range(100000):
      msg = packer.make_can_msg("SCC12", 0, {"CR_VSM_DecCmd": random.uniform(0, 2.55),
                                             "aReqValue": random.uniform(-10.23, 10.24),
                                             "aReqRaw": random.uniform(-10.23, 10.24)})
      parser.update_strings([can_list_to_can_capnp([msg])] * 10)
    elapsed = time.time() - start_time
    self.assertLess(elapsed, 5, "Took too long parsing messages")


if __name__ == "__main__":
  unittest.main()
