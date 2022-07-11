from .common import new_test_dir, CONTRACTS_DIR
import pytest
import os
from typing import Optional
from optik.echidna import run_hybrid_echidna

COVERAGE_TARGET_MARKER = "test::coverage"

# List of tests as tuples:
# (contract, coverage mode, tx sequence length)
to_test = [
    ("ExploreMe.sol", "inst", 40),
    ("Primality.sol", "inst", 40),
    ("MultiMagic.sol", "path-relaxed", 10),
    ("MultiMagic256.sol", "inst-sg", 40),
    ("CoverageInt.sol", "inst", 40),
    ("CoverageBool.sol", "path-relaxed", 5),
    ("CoverageBytesM.sol", "path-relaxed", 1),
    ("CoverageStaticTuple.sol", "inst-tx", 5),
    ("CoverageNestedTuple.sol", "inst-tx", 5),
    ("CoverageNestedArrays1.sol", "inst-tx", 1),
    ("CoverageNestedArrays2.sol", "inst-tx", 1),
    ("CoverageNestedArrays3.sol", "inst-tx", 1),
    ("CoverageFixedArray.sol", "inst-tx", 10),
    ("CoverageDynamicArray.sol", "inst-tx", 10),
    ("CoverageArrayOfTuple.sol", "inst-tx", 1),
    ("CoverageDynamicTuple1.sol", "inst-tx", 1),
    ("CoverageDynamicTuple3.sol", "inst-tx", 1),
    ("CoverageDynamicTuple2.sol", "inst-tx", 1),
    ("Time.sol", "inst", 10),
    ("SmartianExample.sol", "inst-tx", 40),
    ("Payable.sol", "inst", 10),
    ("IntCast.sol", "inst", 10),
    ("CreateContracts.sol", "inst-tx", 10),
    ("CreateContracts2.sol", "inst-tx", 30),
    ("MessageCall.sol", "inst-tx", 1),
    ("Reentrency.sol", "inst-tx", 20),
]

to_test = [
    (CONTRACTS_DIR / contract_file, *rest) for contract_file, *rest in to_test
]

# Test coverage on every contract
@pytest.mark.parametrize("contract,cov_mode,seq_len", to_test)
def test_coverage(contract: str, cov_mode: str, seq_len: int):
    """Test coverage for a given contract. The function
    runs hybrid echidna on the contract and asserts that all target lines in the
    source code were reached. It does so by looking at the `covered.<timestamp>.txt`
    file generated by Echidna after fuzzing, and making that every line marked
    with the coverage test marker was reached (indicated by '*').
    """
    test_dir = new_test_dir()
    contract_name = contract.stem
    # Run hybrid echidna
    cmdline_args = f"{contract}  --contract {contract_name} --test-mode assertion --corpus-dir {test_dir} --seq-len {seq_len} --seed 46541521 --max-iters 10 --test-limit 10000 --cov-mode {cov_mode} --debug ".split()
    run_hybrid_echidna(cmdline_args)
    # Check coverage
    covered_file = get_coverage_file(test_dir)
    assert (
        not covered_file is None
    ), f"Couldn't find coverage file in test dir {test_dir}"
    with open(covered_file, "r") as f:
        for i, line in enumerate(f.readlines()):
            if COVERAGE_TARGET_MARKER in line and not line[0] == "*":
                assert (
                    False
                ), f"Failed to cover line {i+1}:\n|{''.join(line.split('|')[1:])}"


def get_coverage_file(
    test_dir: str,
) -> Optional[str]:
    """Returns the path to covered.<timestamp>.txt file generated by echidna
    in the 'test_dir' directory. Returns None if no such file exists"""
    # Get the first file after reverse sorting the filename list, so
    # that we get the latest coverage file (name with the bigger timestamp)
    for filename in sorted(os.listdir(test_dir), reverse=True):
        if filename.startswith("covered.") and filename.endswith(".txt"):
            return os.path.join(test_dir, filename)
    return None
