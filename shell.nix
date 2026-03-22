# Simulation shell for POTASSIUM-WORKSHOP
#
# Provides a Python 3.10 environment pinned to the same nixpkgs commit used by
# artiq/flake.nix (nixos-22.11), so llvmlite and other deps are compatible with
# artiq 8.  Local lab repos are added to PYTHONPATH rather than built as Nix
# packages, which avoids versioneer / GUI-dep complications.
#
# Usage:
#   nix-shell                          # enter the shell
#   artiq-run --device-db sim/device_db.py \
#     k-exp/kexp/experiments/test/raman_pulse_test.py
#
# First run downloads nixpkgs (~600 MB) and sipyco/pythonparser from GitHub.
# Subsequent runs use the Nix store cache.

let
  nixpkgs = builtins.fetchGit {
    url = "https://github.com/NixOS/nixpkgs";
    rev = "54644f409ab471e87014bb305eac8c50190bcf48"; # nixos-22.11
  };

  pkgs = import nixpkgs {};

  # ── sipyco ──────────────────────────────────────────────────────────────
  sipycoSrc = builtins.fetchGit {
    url = "https://github.com/m-labs/sipyco";
    rev = "38f8f4185d7db6b68bd7f71546da9077b1e2561c";
  };

  sipyco = pkgs.python3Packages.buildPythonPackage {
    pname = "sipyco";
    version = "1.4";
    src = sipycoSrc;
    propagatedBuildInputs = with pkgs.python3Packages; [ numpy ];
    doCheck = false;
  };

  # ── pythonparser ─────────────────────────────────────────────────────────
  pythonparserSrc = builtins.fetchGit {
    url = "https://github.com/m-labs/pythonparser";
    rev = "5413ee5c9f8760e95c6acd5d6e88dabb831ad201";
  };

  pythonparser = pkgs.python3Packages.buildPythonPackage {
    pname = "pythonparser";
    version = "1.4";
    src = pythonparserSrc;
    propagatedBuildInputs = with pkgs.python3Packages; [ regex ];
    doCheck = false;
  };

  # ── Python environment ────────────────────────────────────────────────────
  # artiq, waxx, waxa, kexp are loaded via PYTHONPATH from the local clones,
  # so we only need their external dependencies here.
  pythonEnv = pkgs.python3.withPackages (ps: [
    sipyco
    pythonparser
    ps.llvmlite       # must match artiq 8 / LLVM 11 — nixpkgs-22.11 provides 0.39.x
    ps.numpy
    ps.scipy
    ps.h5py
    ps.pandas
    ps.matplotlib
    ps.pyserial
    ps.prettytable
    ps.python-dateutil
    ps.levenshtein    # python-Levenshtein, required by artiq compiler
  ]);

in pkgs.mkShell {
  buildInputs = [ pythonEnv ];

  shellHook = ''
    WORKSPACE="$(pwd)"

    # ── PYTHONPATH: add local repos in import-priority order ──────────────
    export PYTHONPATH="$WORKSPACE:$WORKSPACE/artiq:$WORKSPACE/wax/waxx-src:$WORKSPACE/wax/waxa-src:$WORKSPACE/k-exp''${PYTHONPATH:+:$PYTHONPATH}"

    # ── Environment variables expected by kexp/config/ip.py ──────────────
    export data="$WORKSPACE/sim-data"
    export code="$WORKSPACE"

    # ── Create sim-data directory and run_id file ─────────────────────────
    mkdir -p "$WORKSPACE/sim-data"
    if [ ! -f "$WORKSPACE/sim-data/run_id.py" ]; then
      echo "1" > "$WORKSPACE/sim-data/run_id.py"
    fi

    # ── artiq_run wrapper (artiq is on PYTHONPATH but not installed) ───────
    artiq-run() {
      python -m artiq.frontend.artiq_run "$@"
    }
    export -f artiq-run

    echo ""
    echo "┌─ POTASSIUM-WORKSHOP simulation shell ──────────────────────────┐"
    echo "│  Python:  $(python --version 2>&1)                                    │"
    echo "│  data:    $data"
    echo "│  code:    $code"
    echo "│                                                                 │"
    echo "│  Run an experiment:                                             │"
    echo "│    artiq-run --device-db sim/device_db.py \\                   │"
    echo "│      k-exp/kexp/experiments/test/raman_pulse_test.py           │"
    echo "└─────────────────────────────────────────────────────────────────┘"
    echo ""
  '';
}
