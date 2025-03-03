import glob
import os
import pytest
from pathlib import Path
from typing import Dict, Any

# These will be imported from the schemas repository
from schemas.python.can_frame import CANIDFormat
from schemas.python.json_formatter import format_file
from schemas.python.signals_testing import obd_testrunner

REPO_ROOT = Path(__file__).parent.parent.absolute()

TEST_CASES = [
    {
        "model_year": "2022",
        "signalset": "default.json",
        "tests": [
            # Front left tire pressure
            ("72E0562281302E5", {"MACHE_TP_FL": 37.05}),
            ("72E05622813033F", {"MACHE_TP_FL": 41.55}),

            # Front right tire pressure
            ("72E0562281402EA", {"MACHE_TP_FR": 37.3}),
            ("72E056228140344", {"MACHE_TP_FR": 41.8}),

            # Rear right tire pressure
            ("72E0562281502DB", {"MACHE_TP_RR": 36.55}),
            ("72E056228150344", {"MACHE_TP_RR": 41.8}),

            # Rear left tire pressure
            ("72E0562281602DB", {"MACHE_TP_RL": 36.55}),
            ("72E056228160344", {"MACHE_TP_RL": 41.8}),

            # Interior temperature
            ("7EA0462DD0426", {"MACHE_IAT": -2}),
            ("7EA0462DD043E", {"MACHE_IAT": 22}),

            # Exterior temperature
            ("7EA0462DD0521", {"MACHE_AAT": -7}),
            ("7EA0462DD0527", {"MACHE_AAT": -1}),

            # Transmission temperature
            ("7EE05621E1C0001", {"MACHE_TT": 0.0625}),
            ("7EE05621E1C0120", {"MACHE_TT": 18}),
            ("7EE05621E1CFFFD", {"MACHE_TT": -0.1875}),
        ]
    },
    {
        "model_year": "2023",
        "signalset": "default.json",
        "tests": [
            # State of charge
            ("7EC0562480120B1", {"MACHE_HVBAT_SOC": 16.738}),
            ("7EC04624845B1", {"MACHE_HVBAT_SOC_DISP": 88.5}),
            ("7EC04624845B6", {"MACHE_HVBAT_SOC_DISP": 91}),

            # State of health
            ("7EC0462490CC6", {"MACHE_HVBAT_SOH": 99}),

            # HV battery voltage
            ("7EC0562480D9123", {"MACHE_HVBAT_V": 371.55}),
            ("7EC0562480D93E8", {"MACHE_HVBAT_V": 378.64}),

            # HV battery temperature
            ("7EC0462480042", {"MACHE_HVBAT_T": 16.0}),

            # HV battery age? pid is theoretically in months
            ("7EC056248100F45", {"MACHE_HVBAT_AGE": 14072.4}),

            # Charge state
            ("7EC0462484F00", {"MACHE_CHRG_STATE": "NOT_READY"}),
        ]
    },
]

def load_signalset(filename: str) -> str:
    """Load a signalset JSON file from the standard location."""
    signalset_path = REPO_ROOT / "signalsets" / "v3" / filename
    with open(signalset_path) as f:
        return f.read()

@pytest.mark.parametrize(
    "test_group",
    TEST_CASES,
    ids=lambda test_case: f"MY{test_case['model_year']}"
)
def test_signals(test_group: Dict[str, Any]):
    """Test signal decoding against known responses."""
    signalset_json = load_signalset(test_group["signalset"])

    # Run each test case in the group
    for response_hex, expected_values in test_group["tests"]:
        try:
            obd_testrunner(
                signalset_json,
                response_hex,
                expected_values,
                can_id_format=CANIDFormat.ELEVEN_BIT
            )
        except Exception as e:
            pytest.fail(
                f"Failed on response {response_hex} "
                f"(Model Year: {test_group['model_year']}, "
                f"Signalset: {test_group['signalset']}): {e}"
            )

def get_json_files():
    """Get all JSON files from the signalsets/v3 directory."""
    signalsets_path = os.path.join(REPO_ROOT, 'signalsets', 'v3')
    json_files = glob.glob(os.path.join(signalsets_path, '*.json'))
    # Convert full paths to relative filenames
    return [os.path.basename(f) for f in json_files]

@pytest.mark.parametrize("test_file",
    get_json_files(),
    ids=lambda x: x.split('.')[0].replace('-', '_')  # Create readable test IDs
)
def test_formatting(test_file):
    """Test signal set formatting for all vehicle models in signalsets/v3/."""
    signalset_path = os.path.join(REPO_ROOT, 'signalsets', 'v3', test_file)

    formatted = format_file(signalset_path)

    with open(signalset_path) as f:
        assert f.read() == formatted

if __name__ == '__main__':
    pytest.main([__file__])
