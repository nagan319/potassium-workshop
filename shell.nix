# Simulation shell for POTASSIUM-WORKSHOP
#
# Provides a Python 3.10 environment pinned to the same nixpkgs commit used by
# artiq/flake.nix (nixos-22.11), so llvmlite and other deps are compatible with
# artiq 8.  Local lab repos are added to PYTHONPATH rather than built as Nix
# packages, which avoids versioneer / GUI-dep complications.
#
# arc-alkali-rydberg-calculator and its dependencies (sympy, lmfit, asteval,
# uncertainties) are not in nixpkgs-22.11, so they are built here from PyPI
# sources using fetchurl + buildPythonPackage.
#
# Usage:
#   nix-shell                          # enter the shell
#   python3 -m artiq.frontend.artiq_run --device-db sim/device_db.py \
#     k-exp/kexp/experiments/test/raman_pulse_test.py

let
  nixpkgs = builtins.fetchGit {
    url = "https://github.com/NixOS/nixpkgs";
    rev = "54644f409ab471e87014bb305eac8c50190bcf48"; # nixos-22.11
  };

  pkgs = import nixpkgs {};
  py  = pkgs.python3Packages;

  # ── sipyco (pinned to artiq's flake.lock) ───────────────────────────────
  sipyco = py.buildPythonPackage {
    pname = "sipyco";
    version = "1.4";
    src = builtins.fetchGit {
      url = "https://github.com/m-labs/sipyco";
      rev = "38f8f4185d7db6b68bd7f71546da9077b1e2561c";
    };
    propagatedBuildInputs = [ py.numpy ];
    doCheck = false;
  };

  # ── pythonparser (pinned to artiq's flake.lock) ─────────────────────────
  pythonparser = py.buildPythonPackage {
    pname = "pythonparser";
    version = "1.4";
    src = builtins.fetchGit {
      url = "https://github.com/m-labs/pythonparser";
      rev = "5413ee5c9f8760e95c6acd5d6e88dabb831ad201";
    };
    propagatedBuildInputs = [ py.regex ];
    doCheck = false;
  };

  # ── sympy 1.11.1 (required by arc and lmfit) ────────────────────────────
  sympy = py.buildPythonPackage {
    pname = "sympy";
    version = "1.11.1";
    format = "setuptools";
    src = pkgs.fetchurl {
      url = "https://files.pythonhosted.org/packages/5a/36/4667b08bc45131fe655a27b1a112c1730f3244343c53a338f44d730bd6ba/sympy-1.11.1.tar.gz";
      sha256 = "e32380dce63cb7c0108ed525570092fd45168bdae2faa17e528221ef72e88658";
    };
    propagatedBuildInputs = [ py.mpmath ];
    doCheck = false;
  };

  # ── asteval 0.9.28 (required by lmfit) ──────────────────────────────────
  asteval = py.buildPythonPackage {
    pname = "asteval";
    version = "0.9.28";
    format = "setuptools";
    src = pkgs.fetchurl {
      url = "https://files.pythonhosted.org/packages/ff/bb/08e3939c0269b3fe6b4396e3c0fec09b8231cb95c0f6cc50c6c2733e0bc0/asteval-0.9.28.tar.gz";
      sha256 = "91bc7d7826bb9c33f4a5a3ef0a8a50fbd5a4695001944ff1d4e0163c413c0a91";
    };
    doCheck = false;
  };

  # ── uncertainties 3.1.7 (required by lmfit) ─────────────────────────────
  uncertainties = py.buildPythonPackage {
    pname = "uncertainties";
    version = "3.1.7";
    format = "setuptools";
    src = pkgs.fetchurl {
      url = "https://files.pythonhosted.org/packages/9d/22/34b918373b9626a50117abd31c0185b96ad1242e46096d6b0a2ef6dd4303/uncertainties-3.1.7.tar.gz";
      sha256 = "80111e0839f239c5b233cb4772017b483a0b7a1573a581b92ab7746a35e6faab";
    };
    propagatedBuildInputs = [ py.numpy ];
    doCheck = false;
  };

  # ── lmfit 1.1.0 (required by arc) ───────────────────────────────────────
  lmfit = py.buildPythonPackage {
    pname = "lmfit";
    version = "1.1.0";
    format = "setuptools";
    src = pkgs.fetchurl {
      url = "https://files.pythonhosted.org/packages/ce/77/8cc51e8f8397e90653688306c79cb2a91662821df613721a276313ec226c/lmfit-1.1.0.tar.gz";
      sha256 = "a2755b708ad7bad010178da28f082f55cbee7a084a625b452632e2d77b5391fb";
    };
    propagatedBuildInputs = [ py.numpy py.scipy sympy asteval uncertainties py.matplotlib ];
    doCheck = false;
  };

  # ── arc-alkali-rydberg-calculator 3.4.1 ─────────────────────────────────
  # Version 3.4.1: scipy>=0.18.1, numpy>=1.16.0, sympy>=1.1.1, lmfit>=0.9.0
  # Compatible with nixpkgs-22.11 (scipy 1.9.1, numpy 1.24.x).
  arc = py.buildPythonPackage {
    pname = "arc-alkali-rydberg-calculator";
    version = "3.4.1";
    format = "setuptools";
    src = pkgs.fetchurl {
      url = "https://files.pythonhosted.org/packages/35/91/ab23e869a8fbe8661e07e9728e650a6e312fc76c23367ebcddb84d8cf1dd/ARC-Alkali-Rydberg-Calculator-3.4.1.tar.gz";
      sha256 = "dee81a906ad6159ebb4926a8339ef3179869646086f3b818bb68462c924c6c50";
    };
    propagatedBuildInputs = [ py.numpy py.scipy sympy lmfit py.matplotlib ];
    doCheck = false;
  };

  # ── Combined Python environment ──────────────────────────────────────────
  # artiq, waxx, waxa, kexp are loaded via PYTHONPATH from local clones
  # (avoids versioneer and GUI-dep complications at build time).
  pythonEnv = pkgs.python3.withPackages (ps: [
    sipyco
    pythonparser
    arc           # real ARC physics — sympy, lmfit, uncertainties, asteval pulled in
    ps.llvmlite   # must match artiq 8 / LLVM 11; nixpkgs-22.11 provides 0.39.x
    ps.numpy
    ps.scipy
    ps.h5py
    ps.pandas
    ps.matplotlib
    ps.pyserial
    ps.prettytable
    ps.python-dateutil
    ps.levenshtein
  ]);

in pkgs.mkShell {
  buildInputs = [ pythonEnv ];

  shellHook = ''
    WORKSPACE="$(pwd)"

    # ── PYTHONPATH: local repos, highest priority first ───────────────────
    # sim/ provides stub hardware devices (not physics stubs).
    # arc is installed via Nix; k-amo uses the real arc.
    export PYTHONPATH="$WORKSPACE:$WORKSPACE/artiq:$WORKSPACE/wax/waxx-src:$WORKSPACE/wax/waxa-src:$WORKSPACE/k-exp:$WORKSPACE/k-amo:$WORKSPACE/pyLabLib''${PYTHONPATH:+:$PYTHONPATH}"

    # ── Environment variables expected by kexp/config/ip.py ───────────────
    export data="$WORKSPACE/sim-data"
    export code="$WORKSPACE"

    # ── Create sim-data directory and run_id file ─────────────────────────
    mkdir -p "$WORKSPACE/sim-data"
    if [ ! -f "$WORKSPACE/sim-data/run_id.py" ]; then
      echo "1" > "$WORKSPACE/sim-data/run_id.py"
    fi

    # ── artiq_run wrapper (artiq is on PYTHONPATH, not installed as cmd) ──
    artiq-run() {
      python3 -m artiq.frontend.artiq_run "$@"
    }
    export -f artiq-run

    echo ""
    echo "┌─ POTASSIUM-WORKSHOP simulation shell ──────────────────────────┐"
    echo "│  Python: $(python3 --version 2>&1)"
    echo "│  arc:    $(python3 -c 'import arc; print(arc.__version__)' 2>/dev/null || echo 'not loaded')"
    echo "│  data:   $data"
    echo "│  code:   $code"
    echo "│                                                                 │"
    echo "│  Run an experiment:                                             │"
    echo "│    artiq-run --device-db sim/device_db.py \\                   │"
    echo "│      k-exp/kexp/experiments/test/raman_pulse_test.py           │"
    echo "└─────────────────────────────────────────────────────────────────┘"
    echo ""
  '';
}
